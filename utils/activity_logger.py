import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ActivityLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.activities = []
        self.current_operation = None
        
    def log_activity(self, action: str, status: str = "success", details: Dict[str, Any] = None, error: str = None):
        """Log an activity with timestamp and details"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'action': action,
            'status': status,  # success, failed, in_progress, warning
            'details': details or {},
            'error': error
        }
        
        self.activities.append(activity)
        print(f"📝 Activity logged: {action} - {status}")
        
        return activity
    
    def start_operation(self, operation: str, details: Dict[str, Any] = None):
        """Start tracking a long-running operation"""
        self.current_operation = {
            'operation': operation,
            'start_time': datetime.now().isoformat(),
            'details': details or {}
        }
        
        return self.log_activity(
            action=f"{operation}_started",
            status="in_progress",
            details=details
        )
    
    def complete_operation(self, success: bool = True, details: Dict[str, Any] = None, error: str = None):
        """Complete the current operation"""
        if not self.current_operation:
            return None
            
        operation = self.current_operation['operation']
        start_time = datetime.fromisoformat(self.current_operation['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        
        final_details = self.current_operation['details'].copy()
        if details:
            final_details.update(details)
        final_details['duration_seconds'] = round(duration, 2)
        
        activity = self.log_activity(
            action=f"{operation}_completed",
            status="success" if success else "failed",
            details=final_details,
            error=error
        )
        
        self.current_operation = None
        return activity
    
    def log_document_upload(self, filename: str, file_size: int, success: bool = True, error: str = None):
        """Log document upload activity"""
        return self.log_activity(
            action="document_upload",
            status="success" if success else "failed",
            details={
                'filename': filename,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            },
            error=error
        )
    
    def log_ai_analysis(self, section: str, feedback_count: int, duration: float = None, success: bool = True, error: str = None):
        """Log AI analysis activity"""
        details = {
            'section': section,
            'feedback_generated': feedback_count
        }
        if duration:
            details['analysis_duration_seconds'] = round(duration, 2)
            
        return self.log_activity(
            action="ai_analysis",
            status="success" if success else "failed",
            details=details,
            error=error
        )
    
    def log_feedback_action(self, action_type: str, feedback_id: str, section: str, feedback_text: str = None):
        """Log feedback accept/reject actions"""
        return self.log_activity(
            action=f"feedback_{action_type}",
            status="success",
            details={
                'feedback_id': feedback_id,
                'section': section,
                'feedback_preview': feedback_text[:100] + "..." if feedback_text and len(feedback_text) > 100 else feedback_text
            }
        )
    
    def log_user_feedback(self, section: str, feedback_type: str, category: str, text: str):
        """Log user custom feedback"""
        return self.log_activity(
            action="user_feedback_added",
            status="success",
            details={
                'section': section,
                'type': feedback_type,
                'category': category,
                'text_preview': text[:100] + "..." if len(text) > 100 else text
            }
        )
    
    def log_chat_interaction(self, message_type: str, message_length: int, response_time: float = None):
        """Log chat interactions"""
        details = {
            'message_type': message_type,
            'message_length': message_length
        }
        if response_time:
            details['response_time_seconds'] = round(response_time, 2)
            
        return self.log_activity(
            action="chat_interaction",
            status="success",
            details=details
        )
    
    def log_s3_operation(self, operation: str, success: bool, details: Dict[str, Any] = None, error: str = None):
        """Log S3 operations with detailed status"""
        return self.log_activity(
            action=f"s3_{operation}",
            status="success" if success else "failed",
            details=details or {},
            error=error
        )
    
    def log_export_operation(self, export_type: str, file_count: int = None, total_size: int = None, 
                           location: str = None, success: bool = True, error: str = None):
        """Log export operations"""
        details = {
            'export_type': export_type,
            'location': location
        }
        if file_count:
            details['files_exported'] = file_count
        if total_size:
            details['total_size_bytes'] = total_size
            details['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
        return self.log_activity(
            action="export_operation",
            status="success" if success else "failed",
            details=details,
            error=error
        )
    
    def log_session_event(self, event: str, details: Dict[str, Any] = None):
        """Log session-level events"""
        return self.log_activity(
            action=f"session_{event}",
            status="success",
            details=details or {}
        )
    
    def get_activities_by_status(self, status: str) -> List[Dict]:
        """Get activities filtered by status"""
        return [activity for activity in self.activities if activity['status'] == status]
    
    def get_activities_by_action(self, action: str) -> List[Dict]:
        """Get activities filtered by action type"""
        return [activity for activity in self.activities if action in activity['action']]
    
    def get_failed_activities(self) -> List[Dict]:
        """Get all failed activities"""
        return self.get_activities_by_status('failed')
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get summary of all activities"""
        total = len(self.activities)
        success_count = len(self.get_activities_by_status('success'))
        failed_count = len(self.get_activities_by_status('failed'))
        in_progress_count = len(self.get_activities_by_status('in_progress'))
        warning_count = len(self.get_activities_by_status('warning'))
        
        # Count by action type
        action_counts = {}
        for activity in self.activities:
            action = activity['action'].split('_')[0]  # Get base action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            'total_activities': total,
            'success_count': success_count,
            'failed_count': failed_count,
            'in_progress_count': in_progress_count,
            'warning_count': warning_count,
            'success_rate': round((success_count / total * 100), 1) if total > 0 else 0,
            'action_breakdown': action_counts,
            'session_duration': self._calculate_session_duration(),
            'last_activity': self.activities[-1]['timestamp'] if self.activities else None
        }
    
    def _calculate_session_duration(self) -> float:
        """Calculate total session duration in minutes"""
        if len(self.activities) < 2:
            return 0
        
        try:
            start_time = datetime.fromisoformat(self.activities[0]['timestamp'])
            end_time = datetime.fromisoformat(self.activities[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0
    
    def export_activities(self) -> Dict[str, Any]:
        """Export all activities for saving"""
        return {
            'session_id': self.session_id,
            'export_timestamp': datetime.now().isoformat(),
            'summary': self.get_activity_summary(),
            'activities': self.activities
        }
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get most recent activities"""
        return self.activities[-limit:] if len(self.activities) >= limit else self.activities
    
    def clear_activities(self):
        """Clear all activities (use with caution)"""
        self.activities = []
        self.current_operation = None