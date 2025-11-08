"""
Pattern Analysis Module for AI-Prism
Identifies recurring patterns across documents and feedback
"""

import json
import os
from datetime import datetime
from collections import defaultdict


class DocumentPatternAnalyzer:
    def __init__(self, storage_file="data/pattern_analysis.json"):
        self.storage_file = storage_file
        self.pattern_data = self._load_pattern_data()
        
    def _load_pattern_data(self):
        """Load existing pattern data"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {
                    "document_history": [],
                    "recurring_patterns": [],
                    "category_trends": {},
                    "risk_patterns": {}
                }
        else:
            return {
                "document_history": [],
                "recurring_patterns": [],
                "category_trends": {},
                "risk_patterns": {}
            }
    
    def _save_pattern_data(self):
        """Save pattern data to file"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(self.pattern_data, f, indent=2)
    
    def add_document_feedback(self, doc_name, feedback_items):
        """Add feedback from a document to the analyzer"""
        document_entry = {
            "document_name": doc_name,
            "timestamp": datetime.now().isoformat(),
            "feedback_items": feedback_items,
            "total_items": len(feedback_items),
            "risk_distribution": self._calculate_risk_distribution(feedback_items),
            "category_distribution": self._calculate_category_distribution(feedback_items)
        }
        
        self.pattern_data["document_history"].append(document_entry)
        self._update_patterns()
        self._save_pattern_data()
        
    def _calculate_risk_distribution(self, feedback_items):
        """Calculate risk level distribution"""
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        for item in feedback_items:
            risk_level = item.get('risk_level', 'Low')
            risk_counts[risk_level] += 1
        return risk_counts
    
    def _calculate_category_distribution(self, feedback_items):
        """Calculate category distribution"""
        category_counts = {}
        for item in feedback_items:
            category = item.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
    
    def _update_patterns(self):
        """Update recurring patterns based on all documents"""
        if len(self.pattern_data["document_history"]) < 2:
            return
        
        # Find recurring categories across documents
        category_occurrences = defaultdict(list)
        
        for doc in self.pattern_data["document_history"]:
            for category, count in doc["category_distribution"].items():
                category_occurrences[category].append({
                    "document": doc["document_name"],
                    "count": count,
                    "timestamp": doc["timestamp"]
                })
        
        # Identify patterns that appear in multiple documents
        recurring_patterns = []
        for category, occurrences in category_occurrences.items():
            if len(occurrences) >= 2:  # Appears in at least 2 documents
                total_occurrences = sum(occ["count"] for occ in occurrences)
                
                recurring_patterns.append({
                    "pattern": f"Issues related to {category}",
                    "category": category.lower(),
                    "occurrence_count": len(occurrences),
                    "total_instances": total_occurrences,
                    "documents_affected": [occ["document"] for occ in occurrences],
                    "examples": self._get_pattern_examples(category)
                })
        
        # Sort by occurrence count
        recurring_patterns.sort(key=lambda x: x["occurrence_count"], reverse=True)
        self.pattern_data["recurring_patterns"] = recurring_patterns
        
        # Update category trends
        self._update_category_trends()
        
        # Update risk patterns
        self._update_risk_patterns()
    
    def _get_pattern_examples(self, category):
        """Get examples of feedback for a specific category"""
        examples = []
        for doc in self.pattern_data["document_history"]:
            for item in doc["feedback_items"]:
                if item.get("category") == category and len(examples) < 3:
                    examples.append({
                        "document": doc["document_name"],
                        "description": item.get("description", "")[:100] + "..." if len(item.get("description", "")) > 100 else item.get("description", ""),
                        "risk_level": item.get("risk_level", "Low")
                    })
        return examples
    
    def _update_category_trends(self):
        """Update category trends over time"""
        category_trends = {}
        
        for doc in self.pattern_data["document_history"]:
            for category, count in doc["category_distribution"].items():
                if category not in category_trends:
                    category_trends[category] = {
                        "total_count": 0,
                        "document_count": 0,
                        "average_per_document": 0,
                        "trend": "stable"
                    }
                
                category_trends[category]["total_count"] += count
                category_trends[category]["document_count"] += 1
        
        # Calculate averages
        for category, data in category_trends.items():
            data["average_per_document"] = data["total_count"] / data["document_count"]
        
        self.pattern_data["category_trends"] = category_trends
    
    def _update_risk_patterns(self):
        """Update risk level patterns"""
        risk_patterns = {"High": [], "Medium": [], "Low": []}
        
        for doc in self.pattern_data["document_history"]:
            for risk_level, count in doc["risk_distribution"].items():
                if count > 0:
                    risk_patterns[risk_level].append({
                        "document": doc["document_name"],
                        "count": count,
                        "timestamp": doc["timestamp"]
                    })
        
        self.pattern_data["risk_patterns"] = risk_patterns
    
    def find_recurring_patterns(self, threshold=2):
        """Get recurring patterns that meet the threshold"""
        return [pattern for pattern in self.pattern_data["recurring_patterns"] 
                if pattern["occurrence_count"] >= threshold]
    
    def get_pattern_report_html(self):
        """Generate HTML report of patterns"""
        patterns = self.find_recurring_patterns()
        
        if not patterns:
            return """
            <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);" class="dark-mode-panel">
                <h3>📊 Pattern Analysis</h3>
                <p>No recurring patterns found yet. Review more documents to identify patterns.</p>
                <p><em>Patterns are identified when similar issues appear across multiple documents.</em></p>
            </div>
            """
        
        html = """
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);" class="dark-mode-panel">
            <h3>📊 Recurring Feedback Patterns</h3>
            <p>The following patterns have been identified across multiple documents:</p>
            <div style="max-height: 400px; overflow-y: auto;">
        """
        
        for i, pattern in enumerate(patterns):
            html += f"""
            <div style="margin: 15px 0; padding: 15px; border-left: 4px solid #667eea; background: #f8f9ff; border-radius: 4px;" class="dark-mode-feedback-item">
                <h4>Pattern #{i+1}: {pattern['category'].title()}</h4>
                <p><strong>Description:</strong> {pattern['pattern']}</p>
                <p><strong>Occurrences:</strong> {pattern['occurrence_count']} documents ({pattern['total_instances']} total instances)</p>
                <p><strong>Documents Affected:</strong> {', '.join(pattern['documents_affected'])}</p>
                <details>
                    <summary>Examples</summary>
                    <ul>
            """
            
            for example in pattern['examples']:
                risk_color = '#e74c3c' if example['risk_level'] == 'High' else '#f39c12' if example['risk_level'] == 'Medium' else '#3498db'
                html += f"""
                <li>
                    <strong>{example['document']}:</strong> 
                    <span style="color: {risk_color}; font-weight: bold;">
                        {example['risk_level']} risk
                    </span> - 
                    {example['description']}
                </li>
                """
            
            html += """
                    </ul>
                </details>
            </div>
            """
        
        # Add summary statistics
        total_docs = len(self.pattern_data["document_history"])
        html += f"""
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 4px;" class="dark-mode-feedback-item">
                <h4>📈 Pattern Summary</h4>
                <p><strong>Total Documents Analyzed:</strong> {total_docs}</p>
                <p><strong>Recurring Patterns Found:</strong> {len(patterns)}</p>
                <p><strong>Most Common Pattern:</strong> {patterns[0]['pattern'] if patterns else 'None'}</p>
            </div>
        </div>
        """
        
        return html
    
    def get_category_trends(self):
        """Get category trends data"""
        return self.pattern_data.get("category_trends", {})
    
    def get_risk_patterns(self):
        """Get risk pattern data"""
        return self.pattern_data.get("risk_patterns", {})
    
    def clear_pattern_data(self):
        """Clear all pattern data"""
        self.pattern_data = {
            "document_history": [],
            "recurring_patterns": [],
            "category_trends": {},
            "risk_patterns": {}
        }
        self._save_pattern_data()