import boto3
import json
import os
import shutil
import zipfile
from datetime import datetime
from botocore.exceptions import NoCredentialsError, BotoCoreError
import tempfile

class S3ExportManager:
    def __init__(self, bucket_name='felix-s3-bucket', base_path='tara/'):
        self.bucket_name = bucket_name
        self.base_path = base_path.rstrip('/') + '/'
        self.s3_client = None
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Initialize S3 client - uses AWS CLI credentials locally, IAM role in App Runner"""
        try:
            # Detect environment
            is_app_runner = os.environ.get('AWS_EXECUTION_ENV') or os.environ.get('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI')

            if is_app_runner:
                # App Runner: Use IAM role (no profile needed)
                print("✅ AWS App Runner detected - using IAM role credentials")
                self.s3_client = boto3.client('s3')
            else:
                # Local: Use AWS CLI default credentials (from ~/.aws/credentials)
                print("✅ Local environment - using AWS CLI credentials")
                session = boto3.Session()  # Automatically uses default credentials from CLI
                credentials = session.get_credentials()
                if credentials:
                    self.s3_client = boto3.client('s3')
                    cred_source = os.environ.get('AWS_PROFILE', 'default profile')
                    print(f"✅ AWS credentials loaded from: {cred_source}")
                else:
                    print("⚠️ No AWS CLI credentials found. S3 export will use local fallback.")
                    print("   Run 'aws configure' to set up credentials")
                    self.s3_client = None
                    return
            
            # Test connection with timeout
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                print(f"✅ S3 connection established to bucket: {self.bucket_name}")
            except Exception as bucket_error:
                print(f"⚠️ S3 bucket '{self.bucket_name}' not accessible: {str(bucket_error)}")
                print("📝 S3 export will use local fallback.")
                self.s3_client = None
                
        except NoCredentialsError:
            print("⚠️ AWS credentials not found. S3 export will use local fallback.")
            self.s3_client = None
        except Exception as e:
            print(f"⚠️ S3 initialization failed: {str(e)}. Using local fallback.")
            self.s3_client = None
    
    def test_s3_connection(self):
        """Test S3 connection and return status"""
        if not self.s3_client:
            return {
                'connected': False,
                'error': 'S3 client not initialized - check AWS credentials',
                'bucket_accessible': False
            }
        
        try:
            # Test bucket access
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            # Test write permissions by attempting to list objects
            self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.base_path, MaxKeys=1)
            
            return {
                'connected': True,
                'bucket_accessible': True,
                'bucket_name': self.bucket_name,
                'base_path': self.base_path
            }
        except Exception as e:
            return {
                'connected': True,
                'bucket_accessible': False,
                'error': str(e),
                'bucket_name': self.bucket_name
            }
    
    def create_export_folder_name(self, document_name):
        """Create folder name with timestamp and document name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean document name for folder usage
        clean_doc_name = "".join(c for c in document_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_doc_name = clean_doc_name.replace(' ', '_')
        return f"{timestamp}_{clean_doc_name}"
    
    def export_complete_review_to_s3(self, review_session, before_document_path, after_document_path):
        """Export complete review session to S3 with comprehensive data"""
        try:
            # Create folder name
            folder_name = self.create_export_folder_name(review_session.document_name)
            s3_folder_path = f"{self.base_path}{folder_name}/"
            
            print(f"📦 Creating comprehensive export for: {folder_name}")
            
            # Create temporary directory for export preparation
            with tempfile.TemporaryDirectory() as temp_dir:
                export_dir = os.path.join(temp_dir, folder_name)
                os.makedirs(export_dir, exist_ok=True)
                
                # 1. Export documents
                docs_dir = os.path.join(export_dir, "documents")
                os.makedirs(docs_dir, exist_ok=True)
                
                # Before document
                if before_document_path and os.path.exists(before_document_path):
                    before_filename = f"before_{review_session.document_name}"
                    shutil.copy2(before_document_path, os.path.join(docs_dir, before_filename))
                
                # After document (reviewed)
                if after_document_path and os.path.exists(after_document_path):
                    after_filename = f"after_{review_session.document_name}"
                    shutil.copy2(after_document_path, os.path.join(docs_dir, after_filename))
                
                # Guidelines document if exists
                if hasattr(review_session, 'guidelines_path') and review_session.guidelines_path and os.path.exists(review_session.guidelines_path):
                    guidelines_filename = f"guidelines_{review_session.guidelines_name}"
                    shutil.copy2(review_session.guidelines_path, os.path.join(docs_dir, guidelines_filename))
                
                # 2. Export all feedback data
                feedback_dir = os.path.join(export_dir, "feedback")
                os.makedirs(feedback_dir, exist_ok=True)
                
                # Accepted feedback
                self._export_feedback_data(
                    review_session.accepted_feedback, 
                    os.path.join(feedback_dir, "accepted_feedback.json"),
                    "Accepted AI Feedback"
                )
                
                # Rejected feedback  
                self._export_feedback_data(
                    review_session.rejected_feedback,
                    os.path.join(feedback_dir, "rejected_feedback.json"),
                    "Rejected AI Feedback"
                )
                
                # User custom feedback
                self._export_feedback_data(
                    review_session.user_feedback,
                    os.path.join(feedback_dir, "user_custom_feedback.json"),
                    "User Custom Feedback"
                )
                
                # All original AI suggestions (before user decisions)
                all_ai_feedback = {}
                for section_name, feedback_items in review_session.feedback_data.items():
                    all_ai_feedback[section_name] = feedback_items
                
                self._export_feedback_data(
                    all_ai_feedback,
                    os.path.join(feedback_dir, "all_ai_suggestions.json"),
                    "All Original AI Suggestions"
                )
                
                # 3. Export logs and activity
                logs_dir = os.path.join(export_dir, "logs")
                os.makedirs(logs_dir, exist_ok=True)
                
                # Activity logs
                with open(os.path.join(logs_dir, "activity_log.json"), 'w') as f:
                    json.dump({
                        'export_info': {
                            'timestamp': datetime.now().isoformat(),
                            'document_name': review_session.document_name,
                            'session_id': review_session.session_id,
                            'total_activities': len(review_session.activity_log)
                        },
                        'activity_log': review_session.activity_log
                    }, f, indent=2)
                
                # Chat history
                with open(os.path.join(logs_dir, "chat_history.json"), 'w') as f:
                    json.dump({
                        'export_info': {
                            'timestamp': datetime.now().isoformat(),
                            'total_messages': len(review_session.chat_history)
                        },
                        'chat_history': review_session.chat_history
                    }, f, indent=2)
                
                # Audit logs from audit logger
                try:
                    audit_logs = review_session.audit_logger.get_session_logs()
                    with open(os.path.join(logs_dir, "audit_logs.json"), 'w') as f:
                        json.dump({
                            'export_info': {
                                'timestamp': datetime.now().isoformat(),
                                'session_id': review_session.session_id
                            },
                            'audit_logs': audit_logs,
                            'performance_metrics': review_session.audit_logger.get_performance_metrics(),
                            'activity_timeline': review_session.audit_logger.get_activity_timeline()
                        }, f, indent=2)
                except Exception as e:
                    print(f"⚠️ Failed to export audit logs: {e}")
                
                # 4. Export comprehensive report
                report_data = self._generate_comprehensive_report(review_session)
                with open(os.path.join(export_dir, "comprehensive_report.json"), 'w') as f:
                    json.dump(report_data, f, indent=2)
                
                # Export as readable text report
                self._export_readable_report(review_session, export_dir)
                
                # 5. Upload to S3 or save locally
                if self.s3_client:
                    return self._upload_to_s3(export_dir, s3_folder_path, folder_name)
                else:
                    return self._save_locally(export_dir, folder_name)
                    
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'location': 'local_fallback'
            }
    
    def _export_feedback_data(self, feedback_dict, output_path, description):
        """Export feedback data with metadata"""
        export_data = {
            'export_info': {
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'total_sections': len(feedback_dict),
                'total_items': sum(len(items) for items in feedback_dict.values())
            },
            'feedback_by_section': dict(feedback_dict)
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def _generate_comprehensive_report(self, review_session):
        """Generate comprehensive review report with statistics and summary"""
        # Calculate statistics
        total_ai_suggestions = sum(len(items) for items in review_session.feedback_data.values())
        total_accepted = sum(len(items) for items in review_session.accepted_feedback.values())
        total_rejected = sum(len(items) for items in review_session.rejected_feedback.values())
        total_user_feedback = sum(len(items) for items in review_session.user_feedback.values())
        
        # Risk level analysis
        risk_analysis = {'High': 0, 'Medium': 0, 'Low': 0}
        for feedback_items in review_session.feedback_data.values():
            for item in feedback_items:
                risk_level = item.get('risk_level', 'Low')
                risk_analysis[risk_level] += 1
        
        # Category analysis
        category_analysis = {}
        for feedback_items in review_session.feedback_data.values():
            for item in feedback_items:
                category = item.get('category', 'Unknown')
                category_analysis[category] = category_analysis.get(category, 0) + 1
        
        # Section analysis
        section_analysis = {}
        for section_name, feedback_items in review_session.feedback_data.items():
            section_analysis[section_name] = {
                'total_suggestions': len(feedback_items),
                'accepted': len(review_session.accepted_feedback.get(section_name, [])),
                'rejected': len(review_session.rejected_feedback.get(section_name, [])),
                'user_added': len(review_session.user_feedback.get(section_name, [])),
                'acceptance_rate': (len(review_session.accepted_feedback.get(section_name, [])) / len(feedback_items) * 100) if feedback_items else 0
            }
        
        return {
            'export_metadata': {
                'timestamp': datetime.now().isoformat(),
                'session_id': review_session.session_id,
                'document_name': review_session.document_name,
                'guidelines_used': getattr(review_session, 'guidelines_name', None),
                'guidelines_preference': getattr(review_session, 'guidelines_preference', 'both')
            },
            'summary_statistics': {
                'total_ai_suggestions': total_ai_suggestions,
                'total_accepted': total_accepted,
                'total_rejected': total_rejected,
                'total_user_feedback': total_user_feedback,
                'acceptance_rate': (total_accepted / total_ai_suggestions * 100) if total_ai_suggestions > 0 else 0,
                'user_engagement_rate': (total_user_feedback / total_ai_suggestions * 100) if total_ai_suggestions > 0 else 0
            },
            'risk_analysis': risk_analysis,
            'category_analysis': category_analysis,
            'section_analysis': section_analysis,
            'activity_summary': {
                'total_activities': len(review_session.activity_log),
                'chat_interactions': len(review_session.chat_history),
                'sections_analyzed': len(review_session.sections)
            },
            'performance_metrics': {
                'review_duration': self._calculate_review_duration(review_session.activity_log),
                'avg_time_per_section': self._calculate_avg_time_per_section(review_session.activity_log, len(review_session.sections))
            }
        }
    
    def _calculate_review_duration(self, activity_log):
        """Calculate total review duration from activity log"""
        if not activity_log or len(activity_log) < 2:
            return 0
        
        try:
            start_time = datetime.fromisoformat(activity_log[0]['timestamp'])
            end_time = datetime.fromisoformat(activity_log[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds() / 60  # in minutes
            return round(duration, 2)
        except:
            return 0
    
    def _calculate_avg_time_per_section(self, activity_log, total_sections):
        """Calculate average time spent per section"""
        duration = self._calculate_review_duration(activity_log)
        if duration > 0 and total_sections > 0:
            return round(duration / total_sections, 2)
        return 0
    
    def _export_readable_report(self, review_session, export_dir):
        """Export human-readable text report"""
        report_data = self._generate_comprehensive_report(review_session)
        
        report_text = f"""AI-PRISM DOCUMENT REVIEW REPORT
{'=' * 50}

Document: {review_session.document_name}
Session ID: {review_session.session_id}
Review Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Guidelines Used: {getattr(review_session, 'guidelines_name', 'Default Hawkeye Framework')}

SUMMARY STATISTICS
{'-' * 30}
Total AI Suggestions: {report_data['summary_statistics']['total_ai_suggestions']}
Accepted Feedback: {report_data['summary_statistics']['total_accepted']}
Rejected Feedback: {report_data['summary_statistics']['total_rejected']}
User Custom Feedback: {report_data['summary_statistics']['total_user_feedback']}
Acceptance Rate: {report_data['summary_statistics']['acceptance_rate']:.1f}%
User Engagement Rate: {report_data['summary_statistics']['user_engagement_rate']:.1f}%

RISK ANALYSIS
{'-' * 30}
High Risk Issues: {report_data['risk_analysis']['High']}
Medium Risk Issues: {report_data['risk_analysis']['Medium']}
Low Risk Issues: {report_data['risk_analysis']['Low']}

TOP CATEGORIES
{'-' * 30}
"""
        
        # Add top categories
        sorted_categories = sorted(report_data['category_analysis'].items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories[:5]:
            report_text += f"{category}: {count} issues\n"
        
        report_text += f"\nSECTION ANALYSIS\n{'-' * 30}\n"
        
        # Add section analysis
        for section_name, analysis in report_data['section_analysis'].items():
            report_text += f"{section_name}:\n"
            report_text += f"  - Total Suggestions: {analysis['total_suggestions']}\n"
            report_text += f"  - Accepted: {analysis['accepted']}\n"
            report_text += f"  - Rejected: {analysis['rejected']}\n"
            report_text += f"  - User Added: {analysis['user_added']}\n"
            report_text += f"  - Acceptance Rate: {analysis['acceptance_rate']:.1f}%\n\n"
        
        report_text += f"\nPERFORMANCE METRICS\n{'-' * 30}\n"
        report_text += f"Review Duration: {report_data['performance_metrics']['review_duration']} minutes\n"
        report_text += f"Average Time per Section: {report_data['performance_metrics']['avg_time_per_section']} minutes\n"
        report_text += f"Total Activities: {report_data['activity_summary']['total_activities']}\n"
        report_text += f"Chat Interactions: {report_data['activity_summary']['chat_interactions']}\n"
        
        with open(os.path.join(export_dir, "readable_report.txt"), 'w') as f:
            f.write(report_text)
    
    def _upload_to_s3(self, local_dir, s3_folder_path, folder_name):
        """Upload directory contents to S3"""
        try:
            uploaded_files = []
            
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_dir)
                    s3_key = f"{s3_folder_path}{relative_path}"
                    
                    print(f"📤 Uploading {relative_path} to S3...")
                    
                    self.s3_client.upload_file(
                        local_file_path,
                        self.bucket_name,
                        s3_key
                    )
                    
                    uploaded_files.append({
                        'local_path': relative_path,
                        's3_key': s3_key,
                        'size': os.path.getsize(local_file_path)
                    })
            
            print(f"✅ Successfully uploaded {len(uploaded_files)} files to S3")
            
            return {
                'success': True,
                'location': f's3://{self.bucket_name}/{s3_folder_path}',
                'folder_name': folder_name,
                'uploaded_files': uploaded_files,
                'total_files': len(uploaded_files),
                'bucket': self.bucket_name,
                's3_path': s3_folder_path
            }
            
        except Exception as e:
            print(f"❌ S3 upload failed: {str(e)}")
            return self._save_locally(local_dir, folder_name)
    
    def _save_locally(self, local_dir, folder_name):
        """Save export locally as fallback"""
        try:
            # Create local exports directory
            local_exports_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(local_exports_dir, exist_ok=True)
            
            # Copy to exports directory
            final_export_path = os.path.join(local_exports_dir, folder_name)
            if os.path.exists(final_export_path):
                shutil.rmtree(final_export_path)
            
            shutil.copytree(local_dir, final_export_path)
            
            # Create zip file
            zip_path = f"{final_export_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(final_export_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, final_export_path)
                        zipf.write(file_path, arcname)
            
            print(f"💾 Export saved locally: {final_export_path}")
            print(f"📦 Zip file created: {zip_path}")
            
            return {
                'success': True,
                'location': 'local',
                'folder_path': final_export_path,
                'zip_path': zip_path,
                'folder_name': folder_name
            }
            
        except Exception as e:
            print(f"❌ Local save failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'location': 'failed'
            }
