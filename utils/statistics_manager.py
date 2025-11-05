import json
from collections import defaultdict
from datetime import datetime

class StatisticsManager:
    def __init__(self):
        self.feedback_data = {}
        self.accepted_feedback = defaultdict(list)
        self.rejected_feedback = defaultdict(list)
        self.user_feedback = defaultdict(list)
        self.statistics_cache = {}

    def update_feedback_data(self, section_name, feedback_items):
        """Update feedback data for a section"""
        self.feedback_data[section_name] = feedback_items
        self._invalidate_cache()

    def record_acceptance(self, section_name, feedback_item):
        """Record feedback acceptance"""
        self.accepted_feedback[section_name].append(feedback_item)
        self._invalidate_cache()

    def record_rejection(self, section_name, feedback_item):
        """Record feedback rejection"""
        self.rejected_feedback[section_name].append(feedback_item)
        self._invalidate_cache()

    def add_user_feedback(self, section_name, feedback_item):
        """Add user-created feedback"""
        self.user_feedback[section_name].append(feedback_item)
        self._invalidate_cache()

    def get_statistics(self):
        """Get comprehensive statistics"""
        if 'main_stats' in self.statistics_cache:
            return self.statistics_cache['main_stats']

        stats = {
            'total_feedback': self._calculate_total_feedback(),
            'high_risk': self._count_risk_level('High'),
            'medium_risk': self._count_risk_level('Medium'),
            'low_risk': self._count_risk_level('Low'),
            'accepted': self._count_accepted(),
            'rejected': self._count_rejected(),
            'user_added': self._count_user_added(),
            'sections_analyzed': len(self.feedback_data),
            'completion_rate': self._calculate_completion_rate()
        }

        self.statistics_cache['main_stats'] = stats
        return stats

    def get_detailed_breakdown(self, stat_type):
        """Get detailed breakdown for a specific statistic"""
        cache_key = f"breakdown_{stat_type}"
        if cache_key in self.statistics_cache:
            return self.statistics_cache[cache_key]

        breakdown = {}

        if stat_type == 'total_feedback':
            breakdown = self._get_total_feedback_breakdown()
        elif stat_type == 'high_risk':
            breakdown = self._get_risk_breakdown('High')
        elif stat_type == 'medium_risk':
            breakdown = self._get_risk_breakdown('Medium')
        elif stat_type == 'low_risk':
            breakdown = self._get_risk_breakdown('Low')
        elif stat_type == 'accepted':
            breakdown = self._get_accepted_breakdown()
        elif stat_type == 'rejected':
            breakdown = self._get_rejected_breakdown()
        elif stat_type == 'user_added':
            breakdown = self._get_user_added_breakdown()

        self.statistics_cache[cache_key] = breakdown
        return breakdown

    def _calculate_total_feedback(self):
        """Calculate total feedback items across all sections"""
        return sum(len(items) for items in self.feedback_data.values())

    def _count_risk_level(self, risk_level):
        """Count feedback items by risk level"""
        count = 0
        for items in self.feedback_data.values():
            count += sum(1 for item in items if item.get('risk_level') == risk_level)
        return count

    def _count_accepted(self):
        """Count accepted feedback items"""
        return sum(len(items) for items in self.accepted_feedback.values())

    def _count_rejected(self):
        """Count rejected feedback items"""
        return sum(len(items) for items in self.rejected_feedback.values())

    def _count_user_added(self):
        """Count user-added feedback items"""
        return sum(len(items) for items in self.user_feedback.values())

    def _calculate_completion_rate(self):
        """Calculate review completion rate"""
        total_items = self._calculate_total_feedback()
        if total_items == 0:
            return 0
        
        reviewed_items = self._count_accepted() + self._count_rejected()
        return round((reviewed_items / total_items) * 100, 1)

    def _get_total_feedback_breakdown(self):
        """Get breakdown of total feedback by section and type"""
        breakdown = {
            'by_section': {},
            'by_type': defaultdict(int),
            'by_category': defaultdict(int)
        }

        for section_name, items in self.feedback_data.items():
            breakdown['by_section'][section_name] = {
                'count': len(items),
                'types': defaultdict(int),
                'risk_levels': defaultdict(int)
            }

            for item in items:
                item_type = item.get('type', 'unknown')
                risk_level = item.get('risk_level', 'Low')
                category = item.get('category', 'general')

                breakdown['by_type'][item_type] += 1
                breakdown['by_category'][category] += 1
                breakdown['by_section'][section_name]['types'][item_type] += 1
                breakdown['by_section'][section_name]['risk_levels'][risk_level] += 1

        return breakdown

    def _get_risk_breakdown(self, risk_level):
        """Get breakdown of items by risk level"""
        breakdown = {
            'by_section': {},
            'by_type': defaultdict(int),
            'by_category': defaultdict(int),
            'items': []
        }

        for section_name, items in self.feedback_data.items():
            risk_items = [item for item in items if item.get('risk_level') == risk_level]
            
            if risk_items:
                breakdown['by_section'][section_name] = len(risk_items)
                
                for item in risk_items:
                    breakdown['by_type'][item.get('type', 'unknown')] += 1
                    breakdown['by_category'][item.get('category', 'general')] += 1
                    breakdown['items'].append({
                        'section': section_name,
                        'type': item.get('type'),
                        'category': item.get('category'),
                        'description': item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', '')
                    })

        return breakdown

    def _get_accepted_breakdown(self):
        """Get breakdown of accepted feedback"""
        breakdown = {
            'by_section': {},
            'by_type': defaultdict(int),
            'by_risk_level': defaultdict(int),
            'items': []
        }

        for section_name, items in self.accepted_feedback.items():
            breakdown['by_section'][section_name] = len(items)
            
            for item in items:
                breakdown['by_type'][item.get('type', 'unknown')] += 1
                breakdown['by_risk_level'][item.get('risk_level', 'Low')] += 1
                breakdown['items'].append({
                    'section': section_name,
                    'type': item.get('type'),
                    'risk_level': item.get('risk_level'),
                    'description': item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', '')
                })

        return breakdown

    def _get_rejected_breakdown(self):
        """Get breakdown of rejected feedback"""
        breakdown = {
            'by_section': {},
            'by_type': defaultdict(int),
            'by_risk_level': defaultdict(int),
            'items': []
        }

        for section_name, items in self.rejected_feedback.items():
            breakdown['by_section'][section_name] = len(items)
            
            for item in items:
                breakdown['by_type'][item.get('type', 'unknown')] += 1
                breakdown['by_risk_level'][item.get('risk_level', 'Low')] += 1
                breakdown['items'].append({
                    'section': section_name,
                    'type': item.get('type'),
                    'risk_level': item.get('risk_level'),
                    'description': item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', '')
                })

        return breakdown

    def _get_user_added_breakdown(self):
        """Get breakdown of user-added feedback"""
        breakdown = {
            'by_section': {},
            'by_type': defaultdict(int),
            'by_category': defaultdict(int),
            'items': []
        }

        for section_name, items in self.user_feedback.items():
            breakdown['by_section'][section_name] = len(items)
            
            for item in items:
                breakdown['by_type'][item.get('type', 'unknown')] += 1
                breakdown['by_category'][item.get('category', 'general')] += 1
                breakdown['items'].append({
                    'section': section_name,
                    'type': item.get('type'),
                    'category': item.get('category'),
                    'description': item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', '')
                })

        return breakdown

    def generate_statistics_html(self, stats):
        """Generate HTML for statistics display with clickable numbers"""
        return f"""
        <div style="background: white; padding: 15px; border-radius: 8px; 
                    margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
                    display: flex; justify-content: space-around;" class="dark-mode-stats">
            <div style="text-align: center; cursor: pointer;" onclick="showStatDetail('total_feedback')">
                <div style="font-size: 24px; font-weight: 700; color: #667eea;">{stats['total_feedback']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Total Feedback</div>
            </div>
            <div style="text-align: center; cursor: pointer;" onclick="showStatDetail('high_risk')">
                <div style="font-size: 24px; font-weight: 700; color: #e74c3c;">{stats['high_risk']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">High Risk</div>
            </div>
            <div style="text-align: center; cursor: pointer;" onclick="showStatDetail('medium_risk')">
                <div style="font-size: 24px; font-weight: 700; color: #f39c12;">{stats['medium_risk']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Medium Risk</div>
            </div>
            <div style="text-align: center; cursor: pointer;" onclick="showStatDetail('accepted')">
                <div style="font-size: 24px; font-weight: 700; color: #2ecc71;">{stats['accepted']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Accepted</div>
            </div>
            <div style="text-align: center; cursor: pointer;" onclick="showStatDetail('user_added')">
                <div style="font-size: 24px; font-weight: 700; color: #3498db;">{stats['user_added']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">User Added</div>
            </div>
        </div>
        """

    def generate_breakdown_html(self, breakdown, stat_type):
        """Generate HTML for detailed breakdown"""
        if not breakdown:
            return "<p>No data available for this statistic.</p>"

        html = f"<div class='breakdown-container'><h3>Detailed Breakdown: {stat_type.replace('_', ' ').title()}</h3>"

        # By section breakdown
        if 'by_section' in breakdown and breakdown['by_section']:
            html += "<h4>By Section:</h4><ul>"
            for section, count in breakdown['by_section'].items():
                html += f"<li><strong>{section}:</strong> {count} items</li>"
            html += "</ul>"

        # By type breakdown
        if 'by_type' in breakdown and breakdown['by_type']:
            html += "<h4>By Type:</h4><ul>"
            for item_type, count in breakdown['by_type'].items():
                html += f"<li><strong>{item_type.title()}:</strong> {count} items</li>"
            html += "</ul>"

        # By category breakdown
        if 'by_category' in breakdown and breakdown['by_category']:
            html += "<h4>By Category:</h4><ul>"
            for category, count in breakdown['by_category'].items():
                html += f"<li><strong>{category}:</strong> {count} items</li>"
            html += "</ul>"

        # Individual items (limited to first 10)
        if 'items' in breakdown and breakdown['items']:
            html += f"<h4>Sample Items (showing first 10 of {len(breakdown['items'])}):</h4><ul>"
            for item in breakdown['items'][:10]:
                html += f"<li><strong>[{item.get('section', 'Unknown')}]</strong> {item.get('type', 'Unknown').title()}: {item.get('description', 'No description')}</li>"
            html += "</ul>"

        html += "</div>"
        return html

    def _invalidate_cache(self):
        """Clear statistics cache when data changes"""
        self.statistics_cache = {}

    def export_statistics(self):
        """Export statistics as JSON for external use"""
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'feedback_summary': {
                'total_sections': len(self.feedback_data),
                'sections_with_feedback': len([s for s in self.feedback_data.values() if s]),
                'acceptance_rate': self._calculate_acceptance_rate(),
                'user_engagement': self._calculate_user_engagement()
            }
        }

    def _calculate_acceptance_rate(self):
        """Calculate overall acceptance rate"""
        total_reviewed = self._count_accepted() + self._count_rejected()
        if total_reviewed == 0:
            return 0
        return round((self._count_accepted() / total_reviewed) * 100, 1)

    def _calculate_user_engagement(self):
        """Calculate user engagement score"""
        total_ai_feedback = self._calculate_total_feedback()
        user_additions = self._count_user_added()
        
        if total_ai_feedback == 0:
            return 0
        
        return round((user_additions / total_ai_feedback) * 100, 1)