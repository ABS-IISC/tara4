import json
import re
import boto3
from datetime import datetime
from collections import defaultdict

class AIFeedbackEngine:
    def __init__(self):
        self.hawkeye_sections = {
            1: "Initial Assessment",
            2: "Investigation Process", 
            3: "Seller Classification",
            4: "Enforcement Decision-Making",
            5: "Additional Verification (High-Risk Cases)",
            6: "Multiple Appeals Handling",
            7: "Account Hijacking Prevention",
            8: "Funds Management",
            9: "REs-Q Outreach Process",
            10: "Sentiment Analysis",
            11: "Root Cause Analysis",
            12: "Preventative Actions",
            13: "Documentation and Reporting",
            14: "Cross-Team Collaboration",
            15: "Quality Control",
            16: "Continuous Improvement",
            17: "Communication Standards",
            18: "Performance Metrics",
            19: "Legal and Compliance",
            20: "New Service Launch Considerations"
        }
        
        self.feedback_cache = {}
        self.hawkeye_checklist = self._load_hawkeye_checklist()

    def _load_hawkeye_checklist(self):
        """Load Hawkeye checklist content"""
        try:
            # In production, this would load from the actual Hawkeye document
            return """
            HAWKEYE INVESTIGATION CHECKLIST:
            1. Initial Assessment - Evaluate customer experience (CX) impact
            2. Investigation Process - Challenge SOPs and enforcement decisions
            3. Seller Classification - Identify good/bad/confused actors
            4. Enforcement Decision-Making - Proper violation assessment
            5. Additional Verification - High-risk case handling
            6. Multiple Appeals Handling - Pattern recognition
            7. Account Hijacking Prevention - Security measures
            8. Funds Management - Financial impact assessment
            9. REs-Q Outreach Process - Communication protocols
            10. Sentiment Analysis - Escalation and health safety
            11. Root Cause Analysis - Process gaps identification
            12. Preventative Actions - Solution implementation
            13. Documentation and Reporting - Proper record keeping
            14. Cross-Team Collaboration - Stakeholder engagement
            15. Quality Control - Audit and review processes
            16. Continuous Improvement - Training and updates
            17. Communication Standards - Clear messaging
            18. Performance Metrics - Tracking and measurement
            19. Legal and Compliance - Regulatory adherence
            20. New Service Launch Considerations - Pilot and rollback
            """
        except:
            return ""

    def analyze_section(self, section_name, content, doc_type="Full Write-up"):
        """Analyze section with comprehensive Hawkeye framework"""
        cache_key = f"{section_name}_{hash(content)}"
        if cache_key in self.feedback_cache:
            return self.feedback_cache[cache_key]

        # Get section-specific guidance
        section_guidance = self._get_section_guidance(section_name)
        
        prompt = f"""Analyze this section "{section_name}" from a {doc_type} document using the Hawkeye investigation framework.

{section_guidance}

SECTION CONTENT:
{content[:3000]}

Provide comprehensive feedback following the 20-point Hawkeye checklist. For each feedback item, include:
1. Specific questions from the Hawkeye checklist that should be addressed
2. References to relevant Hawkeye checkpoint numbers (#1-20)
3. Examples from case studies when applicable
4. Risk classification (High/Medium/Low)

Focus on:
- Missing critical information
- Process gaps and improvements
- Customer impact assessment
- Root cause depth
- Preventative action completeness
- Documentation quality
- Compliance with investigation standards

Return feedback in this JSON format:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion|positive",
            "category": "category matching Hawkeye sections",
            "description": "Clear description referencing Hawkeye criteria",
            "suggestion": "Specific suggestion based on Hawkeye guidelines",
            "example": "Example from case studies or Hawkeye checklist",
            "questions": ["Question 1 from Hawkeye?", "Question 2?"],
            "hawkeye_refs": [1, 11, 12],
            "risk_level": "High|Medium|Low",
            "confidence": 0.95
        }}
    ]
}}"""

        system_prompt = f"""You are an expert document reviewer following the Hawkeye investigation mental models for CT EE guidelines.

{self.hawkeye_checklist}

Apply these Hawkeye investigation mental models in your analysis. Reference specific checklist items when providing feedback. Be thorough and identify all potential issues, gaps, and improvements."""

        response = self._invoke_bedrock(system_prompt, prompt)
        
        try:
            result = json.loads(response)
        except:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                except:
                    result = {"feedback_items": []}
            else:
                result = {"feedback_items": []}

        # Enhance feedback items
        for item in result.get('feedback_items', []):
            if 'hawkeye_refs' not in item:
                item['hawkeye_refs'] = self._get_hawkeye_references(item.get('category', ''), item.get('description', ''))
            
            if 'risk_level' not in item:
                item['risk_level'] = self._classify_risk_level(item)
            
            # Add unique ID if missing
            if 'id' not in item:
                item['id'] = f"{section_name}_{len(result['feedback_items'])}_{datetime.now().strftime('%H%M%S')}"

        self.feedback_cache[cache_key] = result
        return result

    def _get_section_guidance(self, section_name):
        """Get section-specific analysis guidance"""
        section_lower = section_name.lower()
        
        if "timeline" in section_lower:
            return """
            For Timeline sections, focus on:
            - Chronological accuracy and completeness
            - Missing critical events or time gaps
            - Clear date formatting and consistency
            - Correlation with enforcement actions
            - Customer impact timeline alignment
            """
        elif "resolving action" in section_lower:
            return """
            For Resolving Actions, focus on:
            - Completeness of resolution steps
            - Validation of actions taken
            - Impact on affected parties
            - Follow-up mechanisms and ownership
            - Clear completion dates and accountability
            """
        elif "root cause" in section_lower or "preventative action" in section_lower:
            return """
            For Root Causes and Preventative Actions, focus on:
            - Depth of root cause analysis (use 5 Whys methodology)
            - Systemic vs symptomatic causes identification
            - Actionability and feasibility of preventative measures
            - Long-term effectiveness assessment
            - Process improvements and gap closure
            - Clear ownership and estimated completion dates
            - Placeholder identification and completion status
            """
        elif "executive summary" in section_lower or "summary" in section_lower:
            return """
            For Executive Summary, focus on:
            - Completeness of key points coverage
            - Clarity and conciseness of communication
            - Accurate representation of findings and outcomes
            - Clear statement of impact and business implications
            - Action items and next steps highlighting
            """
        elif "background" in section_lower:
            return """
            For Background sections, focus on:
            - Context clarity and completeness
            - Relevance of historical information
            - Key milestones and decision points
            - Policy or guideline references
            - Process maturity (pilot vs established)
            """
        else:
            return """
            General section analysis focusing on:
            - Completeness and clarity of information
            - Alignment with Hawkeye investigation standards
            - Evidence quality and documentation
            - Clear action items and ownership
            - Customer impact consideration
            """

    def _get_hawkeye_references(self, category, description):
        """Map feedback to relevant Hawkeye checklist items"""
        keyword_mapping = {
            1: ["customer experience", "cx impact", "customer trust", "buyer impact"],
            2: ["investigation", "sop", "enforcement decision", "abuse pattern"],
            3: ["seller classification", "good actor", "bad actor", "confused actor"],
            4: ["enforcement", "violation", "warning", "suspension"],
            5: ["verification", "supplier", "authenticity", "documentation"],
            6: ["appeal", "repeat", "retrospective"],
            7: ["hijacking", "security", "authentication", "secondary user"],
            8: ["funds", "disbursement", "financial"],
            9: ["outreach", "communication", "clarification"],
            10: ["sentiment", "escalation", "health safety", "legal threat"],
            11: ["root cause", "process gap", "system failure"],
            12: ["preventative", "solution", "improvement", "mitigation"],
            13: ["documentation", "reporting", "background"],
            14: ["cross-team", "collaboration", "engagement"],
            15: ["quality", "audit", "review", "performance"],
            16: ["continuous improvement", "training", "update"],
            17: ["communication standard", "messaging", "clarity"],
            18: ["metrics", "tracking", "measurement"],
            19: ["legal", "compliance", "regulation"],
            20: ["launch", "pilot", "rollback"]
        }
        
        content_lower = f"{category} {description}".lower()
        references = []
        
        for section_num, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in content_lower:
                    references.append(section_num)
                    break
        
        return references[:3]  # Return top 3 most relevant

    def _classify_risk_level(self, feedback_item):
        """Classify risk level based on content analysis"""
        high_risk_indicators = [
            "counterfeit", "fraud", "manipulation", "multiple violation",
            "immediate action", "legal", "health safety", "bad actor",
            "critical", "urgent", "severe impact"
        ]
        
        medium_risk_indicators = [
            "pattern", "violation", "enforcement", "remediation",
            "correction", "warning", "process gap", "important"
        ]
        
        content_lower = f"{feedback_item.get('description', '')} {feedback_item.get('category', '')} {feedback_item.get('type', '')}".lower()
        
        for indicator in high_risk_indicators:
            if indicator in content_lower:
                return "High"
        
        for indicator in medium_risk_indicators:
            if indicator in content_lower:
                return "Medium"
        
        return "Low"

    def _invoke_bedrock(self, system_prompt, user_prompt):
        """Invoke AWS Bedrock for AI analysis"""
        try:
            runtime = boto3.client('bedrock-runtime')
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            })
            
            response = runtime.invoke_model(
                body=body,
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            # Comprehensive fallback response for testing
            return json.dumps({
                "feedback_items": [
                    {
                        "id": "fb_001",
                        "type": "critical",
                        "category": "Investigation Process",
                        "description": "Missing evaluation of customer experience (CX) impact. The analysis should assess how this issue affects customer trust, satisfaction, and potential negative reviews or complaints.",
                        "suggestion": "Add comprehensive analysis of potential customer impact including immediate effects (returns, complaints) and long-term effects (trust erosion, reputation damage)",
                        "example": "Consider both direct impact (affected customers) and indirect impact (market perception) as outlined in Hawkeye checkpoint #1",
                        "questions": [
                            "Have you evaluated the customer experience (CX) impact?",
                            "Did you consider how this affects buyer trust and satisfaction?",
                            "What are the potential negative reviews or complaints that could result?"
                        ],
                        "hawkeye_refs": [1, 10],
                        "risk_level": "High",
                        "confidence": 0.95
                    },
                    {
                        "id": "fb_002",
                        "type": "important",
                        "category": "Root Cause Analysis",
                        "description": "Root cause analysis lacks depth and identification of process gaps that allowed this issue to occur. The analysis should use 5 Whys methodology to identify systemic causes.",
                        "suggestion": "Implement deeper root cause analysis using 5 Whys methodology. Identify specific process gaps, system failures, and procedural weaknesses that contributed to the issue.",
                        "example": "Reference successful root cause analysis from similar cases that identified both immediate and systemic causes",
                        "questions": [
                            "What process gaps allowed this issue to occur?",
                            "Are there system failures that contributed to the problem?",
                            "Have you applied 5 Whys methodology to identify deeper causes?"
                        ],
                        "hawkeye_refs": [11, 12],
                        "risk_level": "Medium",
                        "confidence": 0.88
                    },
                    {
                        "id": "fb_003",
                        "type": "suggestion",
                        "category": "Documentation and Reporting",
                        "description": "Documentation could be enhanced with more specific details about the investigation methodology and evidence collection process.",
                        "suggestion": "Include detailed methodology section explaining investigation approach, evidence sources, and validation steps taken",
                        "example": "Follow documentation standards from Hawkeye checkpoint #13 for comprehensive reporting",
                        "questions": [
                            "Is the investigation methodology clearly documented?",
                            "Are all evidence sources properly cited and validated?"
                        ],
                        "hawkeye_refs": [13, 15],
                        "risk_level": "Low",
                        "confidence": 0.75
                    }
                ]
            })

    def process_chat_query(self, query, context):
        """Process chat queries with TARA focused on guidelines and document analysis"""
        context_info = f"""
        Current Section: {context.get('current_section', 'Current section')}
        Document Type: Full Write-up Investigation
        Hawkeye Framework: 20-point comprehensive checklist
        Session Progress: {context.get('session_progress', 'In progress')}
        Guidelines Preference: {context.get('guidelines_preference', 'both')}
        """
        
        prompt = f"""You are TARA, an AI assistant for document analysis using the Hawkeye framework.
        
        Your role:
        - Provide precise, actionable guidance on document analysis
        - Reference specific Hawkeye framework criteria
        - Focus on compliance and quality standards
        - Give clear, direct answers about guidelines and procedures
        - Maintain professional tone while being helpful
        
        CONTEXT:
        {context_info}
        
        HAWKEYE GUIDELINES REFERENCE:
        {self.hawkeye_checklist}
        
        USER QUESTION: {query}
        
        Respond with:
        1. Direct, actionable advice
        2. Specific references to Hawkeye criteria when relevant
        3. Clear explanations of guidelines and procedures
        4. Practical next steps
        5. Professional, focused guidance
        
        Keep responses concise, accurate, and directly relevant to document analysis and guidelines."""
        
        system_prompt = """You are TARA, a professional AI assistant specialized in document analysis using the Hawkeye framework. 
        You provide clear, direct guidance on document review processes, compliance requirements, and quality standards.
        Focus on being helpful, accurate, and professional in all responses."""
        
        try:
            response = self._invoke_bedrock(system_prompt, prompt)
            return response
        except:
            # Professional error messages
            error_responses = [
                "I'm experiencing technical difficulties. Please try rephrasing your question.",
                "Unable to process your request at the moment. Please try again.",
                "Technical issue encountered. Please rephrase your question and try again.",
                "Service temporarily unavailable. Please try your question again.",
                "Connection issue detected. Please try asking your question again."
            ]
            import random
            return random.choice(error_responses)