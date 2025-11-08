"""
Audit Logger Module for AI-Prism
Comprehensive logging of all user actions and system events
"""

import json
import os
import uuid
from datetime import datetime
from collections import defaultdict


class AuditLogger:
    def __init__(self, log_file="data/audit_logs.json"):
        self.log_file = log_file
        self.session_id = str(uuid.uuid4())[:8]
        self.session_start = datetime.now()
        self.session_logs = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Log session start
        self.log("SESSION_START", "New review session started")
    
    def log(self, action, details, level="INFO"):
        """Add a log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": level,
            "action": action,
            "details": details
        }
        
        # Add to session logs
        self.session_logs.append(log_entry)
        
        # Also save to persistent file
        self._save_to_file(log_entry)
    
    def _save_to_file(self, log_entry):
        """Save log entry to persistent file"""
        try:
            # Load existing logs
            existing_logs = []
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r') as f:
                        existing_logs = json.load(f)
                except json.JSONDecodeError:
                    existing_logs = []
            
            # Add new entry
            existing_logs.append(log_entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(existing_logs) > 1000:
                existing_logs = existing_logs[-1000:]
            
            # Save back to file
            with open(self.log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2)
                
        except Exception as e:
            print(f"Error saving log entry: {e}")
    
    def get_session_logs(self):
        """Get logs for current session"""
        return self.session_logs
    
    def get_all_logs(self):
        """Get all logs from file"""
        if not os.path.exists(self.log_file):
            return []
        
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def get_logs_by_session(self, session_id):
        """Get logs for a specific session"""
        all_logs = self.get_all_logs()
        return [log for log in all_logs if log.get('session_id') == session_id]
    
    def generate_audit_report_html(self):
        """Generate HTML audit report for current session"""
        logs = self.get_session_logs()
        
        html = f"""
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);" class="dark-mode-panel">
            <h3>📋 Audit Log for Session {self.session_id}</h3>
            <p><strong>Session started:</strong> {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total actions logged:</strong> {len(logs)}</p>
            
            <div style="max-height: 400px; overflow-y: auto; margin-top: 15px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f5f5f5;" class="dark-mode-feedback-item">
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Time</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Level</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Action</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Details</th>
                    </tr>
        """
        
        for log in logs:
            level_color = "#2ecc71" if log['level'] == "INFO" else "#e74c3c" if log['level'] == "ERROR" else "#f39c12"
            timestamp = log['timestamp'].split('T')[1].split('.')[0] if 'T' in log['timestamp'] else log['timestamp']
            
            html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{timestamp}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; color: {level_color}; font-weight: bold;">{log['level']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">{log['action']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{log['details']}</td>
                </tr>
            """
        
        html += """
                </table>
            </div>
        </div>
        """
        
        return html
    
    def generate_summary_report(self):
        """Generate summary report of session activity"""
        logs = self.get_session_logs()
        
        # Count actions by type
        action_counts = defaultdict(int)
        for log in logs:
            action_counts[log['action']] += 1
        
        # Calculate session duration
        if logs:
            session_duration = datetime.now() - self.session_start
            duration_minutes = int(session_duration.total_seconds() / 60)
        else:
            duration_minutes = 0
        
        summary = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_duration_minutes": duration_minutes,
            "total_actions": len(logs),
            "action_breakdown": dict(action_counts),
            "most_common_action": max(action_counts, key=action_counts.get) if action_counts else None,
            "error_count": len([log for log in logs if log['level'] == 'ERROR']),
            "warning_count": len([log for log in logs if log['level'] == 'WARNING'])
        }
        
        return summary
    
    def export_logs(self, format_type="json"):
        """Export logs in different formats"""
        logs = self.get_session_logs()
        
        if format_type == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Timestamp', 'Session ID', 'Level', 'Action', 'Details'])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log['timestamp'],
                    log['session_id'],
                    log['level'],
                    log['action'],
                    log['details']
                ])
            
            output.seek(0)
            return output.getvalue()
        
        elif format_type == "txt":
            output = f"Audit Log Export\\n"
            output += f"Session ID: {self.session_id}\\n"
            output += f"Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\\n"
            output += f"Total Actions: {len(logs)}\\n"
            output += "=" * 50 + "\\n\\n"
            
            for log in logs:
                output += f"[{log['timestamp']}] {log['level']} - {log['action']}\\n"
                output += f"  {log['details']}\\n\\n"
            
            return output
        
        else:  # JSON format
            return {
                "export_timestamp": datetime.now().isoformat(),
                "session_summary": self.generate_summary_report(),
                "logs": logs
            }
    
    def clear_session_logs(self):
        """Clear current session logs"""
        self.session_logs = []
        self.log("LOGS_CLEARED", "Session logs cleared by user")
    
    def get_activity_timeline(self):
        """Get activity timeline for visualization"""
        logs = self.get_session_logs()
        
        timeline = []
        for log in logs:
            timeline.append({
                "time": log['timestamp'],
                "action": log['action'],
                "details": log['details'][:50] + "..." if len(log['details']) > 50 else log['details'],
                "level": log['level']
            })
        
        return timeline
    
    def get_performance_metrics(self):
        """Get performance metrics from logs"""
        logs = self.get_session_logs()
        
        # Count different types of activities
        document_uploads = len([log for log in logs if log['action'] == 'DOCUMENTS_UPLOADED'])
        sections_analyzed = len([log for log in logs if log['action'] == 'SECTION_ANALYZED'])
        feedback_accepted = len([log for log in logs if log['action'] == 'FEEDBACK_ACCEPTED'])
        feedback_rejected = len([log for log in logs if log['action'] == 'FEEDBACK_REJECTED'])
        custom_feedback_added = len([log for log in logs if log['action'] == 'CUSTOM_FEEDBACK_ADDED'])
        chat_interactions = len([log for log in logs if log['action'] == 'CHAT_INTERACTION'])
        
        return {
            "document_uploads": document_uploads,
            "sections_analyzed": sections_analyzed,
            "feedback_accepted": feedback_accepted,
            "feedback_rejected": feedback_rejected,
            "custom_feedback_added": custom_feedback_added,
            "chat_interactions": chat_interactions,
            "total_user_actions": feedback_accepted + feedback_rejected + custom_feedback_added,
            "engagement_score": (feedback_accepted + feedback_rejected + custom_feedback_added + chat_interactions) / max(sections_analyzed, 1)
        }