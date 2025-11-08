"""
AI Learning System Module for AI-Prism
Learns from user feedback patterns to improve AI suggestions
"""

import json
import os
from datetime import datetime
from collections import defaultdict


class FeedbackLearningSystem:
    def __init__(self, storage_file="data/learning_data.json"):
        self.storage_file = storage_file
        self.learning_data = self._load_learning_data()
        
    def _load_learning_data(self):
        """Load existing learning data"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {
                    "custom_feedback": [],
                    "accepted_ai_feedback": [],
                    "rejected_ai_feedback": [],
                    "section_patterns": {},
                    "user_preferences": {},
                    "learning_metrics": {
                        "total_sessions": 0,
                        "total_feedback_items": 0,
                        "acceptance_rate": 0.0,
                        "learning_accuracy": 0.0
                    }
                }
        else:
            return {
                "custom_feedback": [],
                "accepted_ai_feedback": [],
                "rejected_ai_feedback": [],
                "section_patterns": {},
                "user_preferences": {},
                "learning_metrics": {
                    "total_sessions": 0,
                    "total_feedback_items": 0,
                    "acceptance_rate": 0.0,
                    "learning_accuracy": 0.0
                }
            }
    
    def _save_learning_data(self):
        """Save learning data to file"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def add_custom_feedback(self, feedback_item, section_name):
        """Add custom feedback for learning"""
        feedback_entry = feedback_item.copy()
        feedback_entry["section_type"] = section_name
        feedback_entry["timestamp"] = datetime.now().isoformat()
        
        self.learning_data["custom_feedback"].append(feedback_entry)
        
        # Update section patterns
        self._update_section_patterns(section_name, feedback_item, "custom")
        
        # Update learning metrics
        self._update_learning_metrics()
        
        self._save_learning_data()
    
    def record_ai_feedback_response(self, feedback_item, section_name, accepted):
        """Record user response to AI feedback"""
        feedback_entry = feedback_item.copy()
        feedback_entry["section_type"] = section_name
        feedback_entry["timestamp"] = datetime.now().isoformat()
        
        if accepted:
            self.learning_data["accepted_ai_feedback"].append(feedback_entry)
            self._update_section_patterns(section_name, feedback_item, "accepted")
        else:
            self.learning_data["rejected_ai_feedback"].append(feedback_entry)
            self._update_section_patterns(section_name, feedback_item, "rejected")
        
        # Update user preferences
        self._update_user_preferences(feedback_item, accepted)
        
        # Update learning metrics
        self._update_learning_metrics()
        
        self._save_learning_data()
    
    def _update_section_patterns(self, section_name, feedback_item, response_type):
        """Update patterns for specific sections"""
        if section_name not in self.learning_data["section_patterns"]:
            self.learning_data["section_patterns"][section_name] = {
                "feedback_types": {},
                "total_count": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "custom_count": 0
            }
        
        section_data = self.learning_data["section_patterns"][section_name]
        section_data["total_count"] += 1
        
        if response_type == "accepted":
            section_data["accepted_count"] += 1
        elif response_type == "rejected":
            section_data["rejected_count"] += 1
        elif response_type == "custom":
            section_data["custom_count"] += 1
        
        # Track feedback types
        feedback_type = feedback_item.get("type", "suggestion")
        category = feedback_item.get("category", "general")
        
        key = f"{feedback_type}:{category}"
        if key not in section_data["feedback_types"]:
            section_data["feedback_types"][key] = {
                "count": 0,
                "accepted": 0,
                "rejected": 0,
                "examples": []
            }
        
        type_data = section_data["feedback_types"][key]
        type_data["count"] += 1
        
        if response_type == "accepted":
            type_data["accepted"] += 1
        elif response_type == "rejected":
            type_data["rejected"] += 1
        
        # Keep examples (max 3)
        if len(type_data["examples"]) < 3:
            type_data["examples"].append({
                "description": feedback_item.get("description", "")[:100],
                "timestamp": datetime.now().isoformat(),
                "response": response_type
            })
    
    def _update_user_preferences(self, feedback_item, accepted):
        """Update user preferences based on feedback responses"""
        category = feedback_item.get("category", "general")
        feedback_type = feedback_item.get("type", "suggestion")
        risk_level = feedback_item.get("risk_level", "Low")
        
        # Initialize preference tracking
        if "categories" not in self.learning_data["user_preferences"]:
            self.learning_data["user_preferences"]["categories"] = {}
        if "types" not in self.learning_data["user_preferences"]:
            self.learning_data["user_preferences"]["types"] = {}
        if "risk_levels" not in self.learning_data["user_preferences"]:
            self.learning_data["user_preferences"]["risk_levels"] = {}
        
        # Update category preferences
        if category not in self.learning_data["user_preferences"]["categories"]:
            self.learning_data["user_preferences"]["categories"][category] = {
                "accepted": 0, "rejected": 0, "preference_score": 0.5
            }
        
        cat_pref = self.learning_data["user_preferences"]["categories"][category]
        if accepted:
            cat_pref["accepted"] += 1
        else:
            cat_pref["rejected"] += 1
        
        # Calculate preference score (0-1, where 1 is always accepted)
        total = cat_pref["accepted"] + cat_pref["rejected"]
        cat_pref["preference_score"] = cat_pref["accepted"] / total if total > 0 else 0.5
        
        # Update type preferences
        if feedback_type not in self.learning_data["user_preferences"]["types"]:
            self.learning_data["user_preferences"]["types"][feedback_type] = {
                "accepted": 0, "rejected": 0, "preference_score": 0.5
            }
        
        type_pref = self.learning_data["user_preferences"]["types"][feedback_type]
        if accepted:
            type_pref["accepted"] += 1
        else:
            type_pref["rejected"] += 1
        
        total = type_pref["accepted"] + type_pref["rejected"]
        type_pref["preference_score"] = type_pref["accepted"] / total if total > 0 else 0.5
        
        # Update risk level preferences
        if risk_level not in self.learning_data["user_preferences"]["risk_levels"]:
            self.learning_data["user_preferences"]["risk_levels"][risk_level] = {
                "accepted": 0, "rejected": 0, "preference_score": 0.5
            }
        
        risk_pref = self.learning_data["user_preferences"]["risk_levels"][risk_level]
        if accepted:
            risk_pref["accepted"] += 1
        else:
            risk_pref["rejected"] += 1
        
        total = risk_pref["accepted"] + risk_pref["rejected"]
        risk_pref["preference_score"] = risk_pref["accepted"] / total if total > 0 else 0.5
    
    def _update_learning_metrics(self):
        """Update overall learning metrics"""
        metrics = self.learning_data["learning_metrics"]
        
        total_accepted = len(self.learning_data["accepted_ai_feedback"])
        total_rejected = len(self.learning_data["rejected_ai_feedback"])
        total_ai_feedback = total_accepted + total_rejected
        
        metrics["total_feedback_items"] = total_ai_feedback + len(self.learning_data["custom_feedback"])
        metrics["acceptance_rate"] = (total_accepted / total_ai_feedback) if total_ai_feedback > 0 else 0.0
        
        # Calculate learning accuracy (how well we predict user preferences)
        # This is a simplified metric - in practice, you'd track prediction accuracy
        metrics["learning_accuracy"] = min(0.9, 0.5 + (total_ai_feedback / 100) * 0.4)
    
    def get_recommended_feedback(self, section_name, content):
        """Get recommended feedback based on past patterns"""
        if section_name not in self.learning_data["section_patterns"]:
            return []
        
        section_data = self.learning_data["section_patterns"][section_name]
        if section_data["total_count"] < 3:  # Not enough data yet
            return []
        
        # Sort feedback types by acceptance rate and frequency
        recommendations = []
        
        for type_key, type_data in section_data["feedback_types"].items():
            if type_data["count"] >= 2:  # Appeared at least twice
                acceptance_rate = type_data["accepted"] / type_data["count"] if type_data["count"] > 0 else 0
                
                if acceptance_rate > 0.6:  # User tends to accept this type
                    feedback_type, category = type_key.split(":", 1)
                    
                    # Get user preference scores
                    cat_score = self.learning_data["user_preferences"].get("categories", {}).get(category, {}).get("preference_score", 0.5)
                    type_score = self.learning_data["user_preferences"].get("types", {}).get(feedback_type, {}).get("preference_score", 0.5)
                    
                    # Calculate confidence based on data and preferences
                    confidence = min(0.9, (acceptance_rate + cat_score + type_score) / 3)
                    
                    if confidence > 0.7:  # High confidence recommendation
                        recommendations.append({
                            "type": feedback_type,
                            "category": category,
                            "description": f"[AI LEARNED SUGGESTION] Based on your past feedback patterns, consider reviewing {category.lower()} aspects in this section.",
                            "confidence": confidence,
                            "learned": True,
                            "based_on": type_data["count"],
                            "acceptance_rate": acceptance_rate,
                            "risk_level": "Medium" if feedback_type == "critical" else "Low"
                        })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def generate_learning_report_html(self):
        """Generate HTML report of learning system status"""
        metrics = self.learning_data["learning_metrics"]
        
        html = f"""
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);" class="dark-mode-panel">
            <h3>🧠 AI Learning System Status</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="padding: 15px; background: #f0f8ff; border-radius: 8px;" class="dark-mode-feedback-item">
                    <h4>📊 Learning Metrics</h4>
                    <p><strong>Total Feedback Items:</strong> {metrics['total_feedback_items']}</p>
                    <p><strong>Acceptance Rate:</strong> {metrics['acceptance_rate']:.1%}</p>
                    <p><strong>Learning Accuracy:</strong> {metrics['learning_accuracy']:.1%}</p>
                </div>
                
                <div style="padding: 15px; background: #f8f9ff; border-radius: 8px;" class="dark-mode-feedback-item">
                    <h4>📈 Training Data</h4>
                    <p><strong>Custom Feedback:</strong> {len(self.learning_data['custom_feedback'])}</p>
                    <p><strong>Accepted AI Feedback:</strong> {len(self.learning_data['accepted_ai_feedback'])}</p>
                    <p><strong>Rejected AI Feedback:</strong> {len(self.learning_data['rejected_ai_feedback'])}</p>
                </div>
            </div>
            
            <h4>🎯 Section-Specific Learning</h4>
            <div style="max-height: 300px; overflow-y: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f5f5f5;" class="dark-mode-feedback-item">
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Section</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Total Feedback</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Acceptance Rate</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Custom Added</th>
                    </tr>
        """
        
        for section_name, section_data in self.learning_data["section_patterns"].items():
            total = section_data["total_count"]
            accepted = section_data["accepted_count"]
            custom = section_data["custom_count"]
            acceptance_rate = (accepted / total * 100) if total > 0 else 0
            
            html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{section_name}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{total}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{acceptance_rate:.1f}%</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{custom}</td>
                </tr>
            """
        
        # Add user preferences section
        html += """
                </table>
            </div>
            
            <h4>👤 User Preferences</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 15px 0;">
        """
        
        # Top preferred categories
        categories = self.learning_data["user_preferences"].get("categories", {})
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1]["preference_score"])
            html += f"""
                <div style="padding: 10px; background: #e8f5e8; border-radius: 4px;" class="dark-mode-feedback-item">
                    <strong>Preferred Category:</strong><br>
                    {top_category[0]} ({top_category[1]['preference_score']:.1%})
                </div>
            """
        
        # Top preferred types
        types = self.learning_data["user_preferences"].get("types", {})
        if types:
            top_type = max(types.items(), key=lambda x: x[1]["preference_score"])
            html += f"""
                <div style="padding: 10px; background: #fff5e8; border-radius: 4px;" class="dark-mode-feedback-item">
                    <strong>Preferred Type:</strong><br>
                    {top_type[0]} ({top_type[1]['preference_score']:.1%})
                </div>
            """
        
        # Risk level preferences
        risk_levels = self.learning_data["user_preferences"].get("risk_levels", {})
        if risk_levels:
            top_risk = max(risk_levels.items(), key=lambda x: x[1]["preference_score"])
            html += f"""
                <div style="padding: 10px; background: #f0f8ff; border-radius: 4px;" class="dark-mode-feedback-item">
                    <strong>Preferred Risk Level:</strong><br>
                    {top_risk[0]} ({top_risk[1]['preference_score']:.1%})
                </div>
            """
        
        html += """
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; border-left: 4px solid #667eea;" class="dark-mode-feedback-item">
                <h4>💡 Learning Insights</h4>
                <p><em>The AI continuously learns from your feedback patterns to provide more relevant suggestions. The more you interact with the system, the better it becomes at predicting your preferences.</em></p>
        """
        
        # Add learning insights
        insights = self._generate_learning_insights()
        if insights:
            html += "<ul>"
            for insight in insights:
                html += f"<li>{insight}</li>"
            html += "</ul>"
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_learning_insights(self):
        """Generate insights about learning patterns"""
        insights = []
        
        # Acceptance rate insights
        acceptance_rate = self.learning_data["learning_metrics"]["acceptance_rate"]
        if acceptance_rate > 0.8:
            insights.append("High acceptance rate indicates AI is well-aligned with your preferences")
        elif acceptance_rate < 0.4:
            insights.append("Low acceptance rate suggests AI is still learning your preferences")
        
        # Custom feedback insights
        custom_count = len(self.learning_data["custom_feedback"])
        if custom_count > 10:
            insights.append(f"You've added {custom_count} custom feedback items, helping AI learn your specific needs")
        
        # Section-specific insights
        section_patterns = self.learning_data["section_patterns"]
        if section_patterns:
            most_active_section = max(section_patterns.items(), key=lambda x: x[1]["total_count"])
            insights.append(f"Most feedback activity in '{most_active_section[0]}' section")
        
        return insights
    
    def get_learning_statistics(self):
        """Get learning statistics for API"""
        return {
            "total_custom_feedback": len(self.learning_data["custom_feedback"]),
            "total_accepted": len(self.learning_data["accepted_ai_feedback"]),
            "total_rejected": len(self.learning_data["rejected_ai_feedback"]),
            "sections_with_patterns": len(self.learning_data["section_patterns"]),
            "learning_metrics": self.learning_data["learning_metrics"],
            "user_preferences": self.learning_data["user_preferences"]
        }
    
    def clear_learning_data(self):
        """Clear all learning data"""
        self.learning_data = {
            "custom_feedback": [],
            "accepted_ai_feedback": [],
            "rejected_ai_feedback": [],
            "section_patterns": {},
            "user_preferences": {},
            "learning_metrics": {
                "total_sessions": 0,
                "total_feedback_items": 0,
                "acceptance_rate": 0.0,
                "learning_accuracy": 0.0
            }
        }
        self._save_learning_data()