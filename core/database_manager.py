"""
Database Manager for AI-Prism Document Analysis Tool
Automatically saves all analysis data to SQLite database
Supports CSV export and S3 integration
"""

import sqlite3
import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class DatabaseManager:
    def __init__(self, db_path='data/analysis_history.db'):
        """Initialize database manager with SQLite"""
        self.db_path = db_path

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        print(f"✅ Database initialized: {self.db_path}")

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Reviews table - stores document analysis sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                document_name TEXT NOT NULL,
                upload_timestamp TEXT NOT NULL,
                completion_timestamp TEXT,
                total_sections INTEGER DEFAULT 0,
                sections_analyzed INTEGER DEFAULT 0,
                total_feedback_items INTEGER DEFAULT 0,
                accepted_items INTEGER DEFAULT 0,
                rejected_items INTEGER DEFAULT 0,
                user_feedback_items INTEGER DEFAULT 0,
                high_risk_count INTEGER DEFAULT 0,
                medium_risk_count INTEGER DEFAULT 0,
                low_risk_count INTEGER DEFAULT 0,
                chat_interactions INTEGER DEFAULT 0,
                output_filename TEXT,
                s3_exported BOOLEAN DEFAULT 0,
                s3_location TEXT,
                status TEXT DEFAULT 'in_progress',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Feedback items table - stores all feedback (AI + user)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                section_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                category TEXT,
                description TEXT,
                suggestion TEXT,
                risk_level TEXT,
                confidence REAL,
                hawkeye_refs TEXT,
                user_action TEXT DEFAULT 'pending',
                is_user_created BOOLEAN DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES reviews(session_id)
            )
        ''')

        # Activity logs table - comprehensive logging
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT DEFAULT 'success',
                details TEXT,
                error TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES reviews(session_id)
            )
        ''')

        # Sections table - track section analysis status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                section_name TEXT NOT NULL,
                section_order INTEGER,
                analyzed BOOLEAN DEFAULT 0,
                feedback_count INTEGER DEFAULT 0,
                analysis_timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES reviews(session_id)
            )
        ''')

        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES reviews(session_id)
            )
        ''')

        conn.commit()
        conn.close()

        print("✅ Database tables created/verified")

    def create_review_session(self, session_id: str, document_name: str, sections: List[str]) -> bool:
        """Create a new review session in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert review record
            cursor.execute('''
                INSERT INTO reviews (session_id, document_name, upload_timestamp, total_sections)
                VALUES (?, ?, ?, ?)
            ''', (session_id, document_name, datetime.now().isoformat(), len(sections)))

            # Insert sections
            for idx, section_name in enumerate(sections):
                cursor.execute('''
                    INSERT INTO sections (session_id, section_name, section_order)
                    VALUES (?, ?, ?)
                ''', (session_id, section_name, idx))

            # Log activity
            self.log_activity(session_id, 'DOCUMENT_UPLOADED', 'success', {
                'document': document_name,
                'sections_count': len(sections)
            })

            conn.commit()
            conn.close()

            print(f"✅ Review session created: {session_id}")
            return True

        except Exception as e:
            print(f"❌ Error creating review session: {e}")
            return False

    def save_feedback_item(self, session_id: str, section_name: str, feedback_item: Dict[str, Any], user_action: str = 'pending') -> bool:
        """Save a feedback item to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            hawkeye_refs_str = json.dumps(feedback_item.get('hawkeye_refs', []))

            cursor.execute('''
                INSERT INTO feedback_items (
                    session_id, section_name, feedback_type, category, description,
                    suggestion, risk_level, confidence, hawkeye_refs, user_action, is_user_created
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                section_name,
                feedback_item.get('type', 'suggestion'),
                feedback_item.get('category', ''),
                feedback_item.get('description', ''),
                feedback_item.get('suggestion', ''),
                feedback_item.get('risk_level', 'Low'),
                feedback_item.get('confidence', 0.0),
                hawkeye_refs_str,
                user_action,
                feedback_item.get('user_created', False)
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Error saving feedback item: {e}")
            return False

    def update_section_analyzed(self, session_id: str, section_name: str, feedback_count: int) -> bool:
        """Mark a section as analyzed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE sections
                SET analyzed = 1, feedback_count = ?, analysis_timestamp = ?
                WHERE session_id = ? AND section_name = ?
            ''', (feedback_count, datetime.now().isoformat(), session_id, section_name))

            # Update review session analyzed count
            cursor.execute('''
                UPDATE reviews
                SET sections_analyzed = (
                    SELECT COUNT(*) FROM sections WHERE session_id = ? AND analyzed = 1
                ),
                updated_at = ?
                WHERE session_id = ?
            ''', (session_id, datetime.now().isoformat(), session_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Error updating section: {e}")
            return False

    def update_feedback_action(self, session_id: str, section_name: str, feedback_id: int, action: str) -> bool:
        """Update user action on feedback (accepted/rejected)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE feedback_items
                SET user_action = ?
                WHERE session_id = ? AND section_name = ? AND id = ?
            ''', (action, session_id, section_name, feedback_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Error updating feedback action: {e}")
            return False

    def complete_review(self, session_id: str, output_filename: str, stats: Dict[str, Any], s3_location: Optional[str] = None) -> bool:
        """Mark review as completed and save final statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE reviews
                SET completion_timestamp = ?,
                    total_feedback_items = ?,
                    accepted_items = ?,
                    rejected_items = ?,
                    user_feedback_items = ?,
                    high_risk_count = ?,
                    medium_risk_count = ?,
                    low_risk_count = ?,
                    output_filename = ?,
                    s3_exported = ?,
                    s3_location = ?,
                    status = 'completed',
                    updated_at = ?
                WHERE session_id = ?
            ''', (
                datetime.now().isoformat(),
                stats.get('total_feedback', 0),
                stats.get('accepted', 0),
                stats.get('rejected', 0),
                stats.get('user_added', 0),
                stats.get('high_risk', 0),
                stats.get('medium_risk', 0),
                stats.get('low_risk', 0),
                output_filename,
                1 if s3_location else 0,
                s3_location,
                datetime.now().isoformat(),
                session_id
            ))

            # Log completion
            self.log_activity(session_id, 'REVIEW_COMPLETED', 'success', {
                'output_file': output_filename,
                'total_feedback': stats.get('total_feedback', 0),
                's3_exported': bool(s3_location)
            })

            conn.commit()
            conn.close()

            print(f"✅ Review completed and saved: {session_id}")
            return True

        except Exception as e:
            print(f"❌ Error completing review: {e}")
            return False

    def log_activity(self, session_id: str, action: str, status: str = 'success', details: Any = None, error: str = None):
        """Log an activity to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            details_str = json.dumps(details) if details else None

            cursor.execute('''
                INSERT INTO activity_logs (session_id, action, status, details, error)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, action, status, details_str, error))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging activity: {e}")

    def log_chat_message(self, session_id: str, role: str, message: str):
        """Log a chat message"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO chat_history (session_id, role, message)
                VALUES (?, ?, ?)
            ''', (session_id, role, message))

            # Update chat interactions count
            cursor.execute('''
                UPDATE reviews
                SET chat_interactions = (
                    SELECT COUNT(*) FROM chat_history WHERE session_id = ? AND role = 'user'
                )
                WHERE session_id = ?
            ''', (session_id, session_id))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging chat: {e}")

    def export_to_csv(self, session_id: Optional[str] = None) -> str:
        """Export all data to CSV format"""
        try:
            conn = sqlite3.connect(self.db_path)

            output = io.StringIO()
            writer = csv.writer(output)

            # Export reviews
            if session_id:
                reviews = conn.execute('SELECT * FROM reviews WHERE session_id = ?', (session_id,)).fetchall()
            else:
                reviews = conn.execute('SELECT * FROM reviews').fetchall()

            # Write reviews section
            writer.writerow(['=== REVIEWS ==='])
            writer.writerow(['ID', 'Session ID', 'Document Name', 'Upload Time', 'Completion Time',
                           'Total Sections', 'Analyzed', 'Total Feedback', 'Accepted', 'Rejected',
                           'User Feedback', 'High Risk', 'Medium Risk', 'Low Risk', 'Chat Count',
                           'Output File', 'S3 Exported', 'S3 Location', 'Status'])

            for row in reviews:
                writer.writerow(row)

            writer.writerow([])

            # Export feedback items
            writer.writerow(['=== FEEDBACK ITEMS ==='])
            writer.writerow(['ID', 'Session ID', 'Section', 'Type', 'Category', 'Description',
                           'Suggestion', 'Risk Level', 'Confidence', 'Hawkeye Refs', 'User Action',
                           'User Created', 'Timestamp'])

            if session_id:
                feedback = conn.execute('SELECT * FROM feedback_items WHERE session_id = ?', (session_id,)).fetchall()
            else:
                feedback = conn.execute('SELECT * FROM feedback_items').fetchall()

            for row in feedback:
                writer.writerow(row)

            writer.writerow([])

            # Export activity logs
            writer.writerow(['=== ACTIVITY LOGS ==='])
            writer.writerow(['ID', 'Session ID', 'Action', 'Status', 'Details', 'Error', 'Timestamp'])

            if session_id:
                activities = conn.execute('SELECT * FROM activity_logs WHERE session_id = ?', (session_id,)).fetchall()
            else:
                activities = conn.execute('SELECT * FROM activity_logs').fetchall()

            for row in activities:
                writer.writerow(row)

            conn.close()

            output.seek(0)
            return output.getvalue()

        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary of a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get review data
            review = cursor.execute('SELECT * FROM reviews WHERE session_id = ?', (session_id,)).fetchone()

            if not review:
                return None

            # Get sections
            sections = cursor.execute('SELECT * FROM sections WHERE session_id = ?', (session_id,)).fetchall()

            # Get feedback items
            feedback = cursor.execute('SELECT * FROM feedback_items WHERE session_id = ?', (session_id,)).fetchall()

            # Get activity logs
            activities = cursor.execute('SELECT * FROM activity_logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT 50', (session_id,)).fetchall()

            conn.close()

            return {
                'review': dict(review),
                'sections': [dict(s) for s in sections],
                'feedback_items': [dict(f) for f in feedback],
                'activity_logs': [dict(a) for a in activities]
            }

        except Exception as e:
            print(f"❌ Error getting session summary: {e}")
            return None

    def get_all_reviews(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all review sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            reviews = conn.execute('''
                SELECT * FROM reviews
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()

            conn.close()

            return [dict(r) for r in reviews]

        except Exception as e:
            print(f"❌ Error getting reviews: {e}")
            return []

# Global database manager instance
# Use /tmp on App Runner (read-only filesystem), local data/ directory otherwise
is_production = os.environ.get('FLASK_ENV') == 'production'
db_path = '/tmp/data/analysis_history.db' if is_production else 'data/analysis_history.db'
db_manager = DatabaseManager(db_path)
