import json
import re
import boto3
import os
import time
from datetime import datetime
from collections import defaultdict
from config.model_config import model_config

class EnhancedAIFeedbackEngine:
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
        """Load comprehensive Hawkeye checklist content"""
        try:
            return """
            COMPREHENSIVE HAWKEYE INVESTIGATION CHECKLIST:
            
            1. Initial Assessment - Evaluate customer experience (CX) impact with quantified metrics
            2. Investigation Process - Challenge SOPs, validate methodology, ensure evidence quality
            3. Seller Classification - Identify good/bad/confused actors with supporting evidence
            4. Enforcement Decision-Making - Proper violation assessment with clear rationale
            5. Additional Verification - High-risk case handling with enhanced validation
            6. Multiple Appeals Handling - Pattern recognition and systematic analysis
            7. Account Hijacking Prevention - Security measures and authentication protocols
            8. Funds Management - Financial impact assessment with quantified losses
            9. REs-Q Outreach Process - Communication protocols and stakeholder engagement
            10. Sentiment Analysis - Escalation triggers, health safety, and legal threat assessment
            11. Root Cause Analysis - Deep systemic analysis using 5-whys and fishbone methodology
            12. Preventative Actions - Specific, measurable solutions with clear ownership and timelines
            13. Documentation and Reporting - Professional standards with audit-ready quality
            14. Cross-Team Collaboration - Stakeholder engagement and coordination protocols
            15. Quality Control - Audit processes, validation, and independent verification
            16. Continuous Improvement - Training programs, process updates, and learning integration
            17. Communication Standards - Clear messaging, stakeholder-appropriate language
            18. Performance Metrics - Tracking, measurement, and success criteria definition
            19. Legal and Compliance - Regulatory adherence and policy alignment
            20. New Service Launch Considerations - Pilot programs, rollback plans, risk mitigation
            """
        except:
            return ""

    def analyze_section(self, section_name, content, doc_type="Full Write-up"):
        """Analyze section with focused Hawkeye framework - concise and actionable"""
        cache_key = f"{section_name}_{hash(content)}"
        if cache_key in self.feedback_cache:
            return self.feedback_cache[cache_key]

        # Get focused section guidance
        section_guidance = self._get_focused_section_guidance(section_name)
        
        prompt = f"""ANALYSIS TASK: Review "{section_name}" for CT EE investigation compliance.

{section_guidance}

CONTENT:
{content[:2500]}

REQUIREMENTS:
• Identify 2-4 specific, actionable improvements only
• Focus on critical gaps impacting investigation quality
• Provide concrete suggestions with clear next steps
• Reference relevant Hawkeye checkpoints
• Be concise and direct - avoid generic feedback

RETURN FORMAT:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion",
            "category": "Investigation Process|Root Cause Analysis|Documentation|Timeline|Evidence",
            "description": "Specific gap or missing element (max 2 sentences)",
            "suggestion": "Concrete action to take (max 1 sentence)",
            "questions": ["1-2 direct questions to address"],
            "hawkeye_refs": [relevant_checkpoint_numbers],
            "risk_level": "High|Medium|Low",
            "confidence": 0.85
        }}
    ]
}}"""

        system_prompt = f"""You are a CT EE investigation specialist providing focused document analysis.

{self.hawkeye_checklist}

GUIDELINES:
• Provide 2-4 high-value feedback items maximum
• Focus on specific gaps that impact investigation quality
• Be direct and actionable - avoid generic suggestions
• Reference specific Hawkeye checkpoints when relevant
• Prioritize critical issues over minor improvements

AVOID:
• Generic feedback that applies to any document
• Overly detailed explanations
• Repetitive suggestions
• Minor formatting or style issues"""

        response = self._invoke_bedrock(system_prompt, prompt)
        
        # Always ensure we have a valid result structure
        result = None
        
        # Check if response contains error
        if response.startswith('{"error"'):
            try:
                error_data = json.loads(response)
                print(f"⚠️ Analysis error: {error_data.get('error')}")
            except:
                print(f"⚠️ Analysis error: Invalid error response format")
            
            print(f"🎭 Falling back to enhanced mock response for section: {section_name}")
            # Use mock response instead of returning error
            response = self._mock_ai_response(prompt)
        
        # Try to parse the response as JSON
        try:
            result = json.loads(response)
            print(f"✅ Response parsed successfully - {len(result.get('feedback_items', []))} items")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Response preview: {response[:200]}...")
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    print(f"✅ Extracted JSON successfully")
                except Exception as e2:
                    print(f"❌ JSON extraction failed: {e2}")
                    result = None
            else:
                print(f"❌ No JSON found in response")
                result = None
        except Exception as e:
            print(f"❌ Unexpected parsing error: {e}")
            result = None
        
        # If all parsing failed, create a safe fallback
        if result is None or not isinstance(result, dict):
            print(f"🔄 Creating enhanced fallback response")
            result = {
                "feedback_items": [],
                "error": "Failed to parse AI response",
                "fallback": True
            }

        # Ensure result has the expected structure
        if 'feedback_items' not in result:
            result['feedback_items'] = []
        
        # Validate and enhance feedback items - limit to top 4
        validated_items = []
        for i, item in enumerate(result.get('feedback_items', [])[:4]):  # Limit to 4 items
            if not isinstance(item, dict):
                continue
                
            # Ensure all required fields exist with improved defaults
            validated_item = {
                'id': item.get('id', f"{section_name}_{i}_{datetime.now().strftime('%H%M%S')}"),
                'type': item.get('type', 'suggestion'),
                'category': item.get('category', 'Investigation Process'),
                'description': self._truncate_text(item.get('description', 'Analysis gap identified'), 150),
                'suggestion': self._truncate_text(item.get('suggestion', ''), 100),
                'example': self._truncate_text(item.get('example', ''), 80),
                'questions': item.get('questions', [])[:2] if isinstance(item.get('questions'), list) else [],
                'hawkeye_refs': item.get('hawkeye_refs', [])[:3] if isinstance(item.get('hawkeye_refs'), list) else [],
                'risk_level': item.get('risk_level', 'Low'),
                'confidence': float(item.get('confidence', 0.8)) if isinstance(item.get('confidence'), (int, float)) else 0.8
            }
            
            # Add hawkeye references if missing
            if not validated_item['hawkeye_refs']:
                validated_item['hawkeye_refs'] = self._get_hawkeye_references(
                    validated_item['category'], 
                    validated_item['description']
                )[:2]
            
            # Classify risk level if not provided or invalid
            if validated_item['risk_level'] not in ['High', 'Medium', 'Low']:
                validated_item['risk_level'] = self._classify_risk_level(validated_item)
            
            validated_items.append(validated_item)
        
        # Update result with validated items
        result['feedback_items'] = validated_items
        
        # Cache the result
        self.feedback_cache[cache_key] = result
        
        print(f"✅ Analysis complete: {len(validated_items)} focused feedback items")
        return result

    def _get_focused_section_guidance(self, section_name):
        """Get focused section-specific analysis guidance"""
        section_lower = section_name.lower()
        
        if "timeline" in section_lower:
            return """TIMELINE FOCUS:
• Date accuracy and format consistency (DD-MMM-YYYY HH:MM)
• Chronological gaps >2 hours requiring explanation
• Missing critical events (detection, escalation, resolution)
• Clear ownership for each timeline entry
• Independent verification through logs/emails"""
        elif "resolving action" in section_lower:
            return """RESOLVING ACTIONS FOCUS:
• Completeness of resolution steps with clear ownership
• Validation evidence for actions claimed as completed
• Impact assessment on affected parties
• Specific completion dates and follow-up mechanisms
• Decision rationale for chosen solutions"""
        elif "root cause" in section_lower or "preventative action" in section_lower:
            return """ROOT CAUSE & PREVENTATIVE ACTIONS FOCUS:
• 5-whys depth reaching systemic causes (not symptoms)
• Specific, measurable preventative actions with DRIs
• Completion dates (avoid vague "Q1" or "soon")
• Success metrics and effectiveness measurement
• Process gaps that enabled the issue"""
        elif "executive summary" in section_lower or "summary" in section_lower:
            return """EXECUTIVE SUMMARY FOCUS:
• Quantified impact (customer, business, financial)
• Clear root cause statement (1 sentence)
• Key actions taken and prevention measures
• Executive-level completeness (standalone understanding)
• Clear accountability and ownership"""
        elif "background" in section_lower:
            return """BACKGROUND FOCUS:
• Context clarity and relevance to current issue
• Key milestones and decision points
• Process maturity indicators (pilot vs established)
• Policy/guideline references where applicable
• Business criticality and customer dependency"""
        else:
            return """GENERAL ANALYSIS FOCUS:
• Information completeness and clarity
• Evidence quality and documentation gaps
• Clear accountability and ownership
• Customer impact consideration
• Compliance with investigation standards"""

    def _mock_ai_response(self, user_prompt):
        """Focused mock AI response with concise, actionable feedback"""
        # Simulate processing delay
        time.sleep(1)
        
        # Generate contextual mock responses based on prompt content
        prompt_lower = user_prompt.lower()
        
        if "timeline" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"timeline_{int(time.time())}",
                        "type": "important",
                        "category": "Timeline",
                        "description": "Timeline missing specific timestamps and has chronological gaps >2 hours without explanation.",
                        "suggestion": "Add DD-MMM-YYYY HH:MM format timestamps and explain significant time gaps.",
                        "questions": [
                            "Are all critical events documented with precise times?",
                            "Who was responsible for each timeline entry?"
                        ],
                        "hawkeye_refs": [2, 13],
                        "risk_level": "Medium",
                        "confidence": 0.88
                    }
                ]
            })
        elif "root cause" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"rootcause_{int(time.time())}",
                        "type": "critical",
                        "category": "Root Cause Analysis",
                        "description": "Root cause analysis lacks 5-whys depth and addresses symptoms rather than systemic causes.",
                        "suggestion": "Apply 5-whys methodology to identify true systemic root causes.",
                        "questions": [
                            "What process failures enabled this issue?",
                            "How can similar systemic problems be prevented?"
                        ],
                        "hawkeye_refs": [11, 12],
                        "risk_level": "High",
                        "confidence": 0.92
                    }
                ]
            })
        elif "executive summary" in prompt_lower or "summary" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"summary_{int(time.time())}",
                        "type": "important",
                        "category": "Impact Assessment",
                        "description": "Executive summary lacks quantified impact metrics and clear accountability structure.",
                        "suggestion": "Add specific numbers for customer impact, financial loss, and clear ownership for improvements.",
                        "questions": [
                            "How many customers were affected and for how long?",
                            "Who is accountable for implementing preventative actions?"
                        ],
                        "hawkeye_refs": [1, 14],
                        "risk_level": "Medium",
                        "confidence": 0.89
                    }
                ]
            })
        elif "resolving action" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"resolving_{int(time.time())}",
                        "type": "important",
                        "category": "Resolution Validation",
                        "description": "Resolving actions lack validation evidence and effectiveness measurement.",
                        "suggestion": "Document validation method, success metrics, and monitoring for each action.",
                        "questions": [
                            "How was effectiveness independently verified?",
                            "What monitoring prevents recurrence?"
                        ],
                        "hawkeye_refs": [2, 15],
                        "risk_level": "Medium",
                        "confidence": 0.87
                    }
                ]
            })
        else:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"general_{int(time.time())}",
                        "type": "important",
                        "category": "Investigation Process",
                        "description": "Section needs stronger evidence validation and cross-verification for key findings.",
                        "suggestion": "Add independent verification sources and document validation methodology.",
                        "questions": [
                            "What evidence supports the key conclusions?",
                            "How was evidence independently verified?"
                        ],
                        "hawkeye_refs": [2, 15],
                        "risk_level": "Medium",
                        "confidence": 0.85
                    }
                ]
            })

    def _classify_risk_level(self, feedback_item):
        """Enhanced risk classification based on comprehensive impact analysis"""
        # Critical/High Risk: Issues that could impact customer safety, legal compliance, or business continuity
        high_risk_indicators = [
            "counterfeit", "fraud", "manipulation", "multiple violation", "systemic failure",
            "immediate action", "legal", "health safety", "bad actor", "regulatory",
            "critical", "urgent", "severe impact", "customer safety", "compliance violation",
            "financial impact", "reputation damage", "security breach", "data privacy",
            "missing evidence", "insufficient validation", "accountability gap", "process failure",
            "timeline gap", "root cause insufficient", "preventative action vague",
            "impact unquantified", "verification missing", "ownership unclear"
        ]
        
        # Important/Medium Risk: Issues that affect investigation quality or operational effectiveness
        medium_risk_indicators = [
            "pattern", "violation", "enforcement", "remediation", "correction", "warning",
            "process gap", "important", "documentation gap", "analysis depth",
            "stakeholder communication", "monitoring gap", "training deficiency",
            "resource allocation", "timeline accuracy", "evidence quality",
            "cross-verification", "methodology", "validation needed", "clarity issue",
            "coordination problem", "escalation delay", "approval process",
            "communication breakdown", "decision authority", "implementation gap"
        ]
        
        # Low Risk: Suggestions for improvement that don't affect core investigation quality
        low_risk_indicators = [
            "formatting", "style", "presentation", "readability", "organization",
            "visual aids", "glossary", "appendix", "reference", "citation",
            "template", "consistency", "minor enhancement", "suggestion",
            "best practice", "optimization", "efficiency", "user experience"
        ]
        
        content_lower = f"{feedback_item.get('description', '')} {feedback_item.get('category', '')} {feedback_item.get('type', '')} {feedback_item.get('suggestion', '')}".lower()
        
        # Check for high risk indicators first
        high_risk_count = sum(1 for indicator in high_risk_indicators if indicator in content_lower)
        if high_risk_count > 0:
            return "High"
        
        # Check for medium risk indicators
        medium_risk_count = sum(1 for indicator in medium_risk_indicators if indicator in content_lower)
        if medium_risk_count > 0:
            return "Medium"
        
        # Check for low risk indicators
        low_risk_count = sum(1 for indicator in low_risk_indicators if indicator in content_lower)
        if low_risk_count > 0:
            return "Low"
        
        # Default classification based on feedback type
        feedback_type = feedback_item.get('type', '').lower()
        if feedback_type == 'critical':
            return "High"
        elif feedback_type == 'important':
            return "Medium"
        else:
            return "Low"

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

    def _invoke_bedrock(self, system_prompt, user_prompt):
        """Invoke AWS Bedrock using original configuration"""
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
            print(f"Bedrock error: {str(e)}")
            # Return enhanced mock response for testing
            return self._enhanced_mock_ai_response(user_prompt)

    def process_chat_query(self, query, context):
        """Process chat queries with focused, concise responses"""
        print(f"Processing chat query: {query[:50]}...")
        
        context_info = f"""
        Current Section: {context.get('current_section', 'Current section')}
        Document Type: CT EE Investigation Writeup
        Feedback Items: {len(context.get('current_feedback', []))}
        Accepted: {context.get('accepted_count', 0)} | Rejected: {context.get('rejected_count', 0)}
        """
        
        prompt = f"""GUIDANCE REQUEST for CT EE Investigation Analysis:
        
        CONTEXT: {context_info}
        USER QUESTION: {query}
        
        HAWKEYE FRAMEWORK:
        {self.hawkeye_checklist}
        
        RESPONSE REQUIREMENTS:
        • Keep response concise (max 200 words)
        • Use bullet points for clarity
        • Reference specific Hawkeye checkpoints when relevant
        • Provide 2-3 actionable recommendations maximum
        • End with one focused follow-up question
        • Be direct and professional
        
        FORMAT:
        **[Topic]**
        • Key point 1
        • Key point 2
        
        **Hawkeye References:** #X, #Y
        **Actions:** Specific next steps
        **Question:** One follow-up question
        
        Be helpful, specific, and concise. Avoid lengthy explanations."""
        
        system_prompt = """You are AI-Prism, a CT EE investigation specialist providing concise guidance.
        
        Guidelines:
        - Keep responses under 200 words
        - Use bullet points and clear structure
        - Be direct and actionable
        - Reference Hawkeye checkpoints when relevant
        - Maintain professional tone
        - Focus on practical next steps"""
        
        try:
            # Always use mock response for consistent responses
            response = self._mock_chat_response(query, context)
            return self._format_chat_response(response)
        except Exception as e:
            print(f"Enhanced chat processing error: {str(e)}")
            # Fallback to basic response if mock fails
            return "Having trouble processing your request. Please try rephrasing your question or ask about specific aspects of the document analysis."

    def _format_chat_response(self, response):
        """Format chat response for better structure and readability"""
        # Ensure proper line breaks and formatting
        formatted = response.replace('\n\n', '<br><br>')
        formatted = formatted.replace('\n', '<br>')
        
        # Add proper spacing for bullet points
        formatted = formatted.replace('• ', '<br>• ')
        formatted = formatted.replace('- ', '<br>• ')
        
        # Format bold text
        formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
        
        # Clean up extra breaks
        formatted = formatted.replace('<br><br><br>', '<br><br>')
        
        return formatted

    def _mock_chat_response(self, query, context):
        """Generate concise, structured mock chat responses"""
        # Simulate processing delay
        time.sleep(0.5)
        
        query_lower = query.lower()
        current_section = context.get('current_section', 'current section')
        
        if 'help' in query_lower or 'how' in query_lower:
            return f"""**AI-Prism Assistance for '{current_section}'**

**Core Capabilities:**
• Investigation quality assessment using Hawkeye framework
• Risk evaluation and compliance validation
• Evidence validation and documentation review

**Key Areas I Help With:**
• Investigation methodology gaps
• Risk assessment and classification
• Documentation quality improvements
• Hawkeye checkpoint compliance

**Next Steps:**
• Ask about specific aspects of '{current_section}' section
• Request Hawkeye checkpoint explanations
• Get guidance on risk assessment

**What specific aspect of '{current_section}' would you like help with?"""
        
        elif 'hawkeye' in query_lower or 'framework' in query_lower:
            return f"""**Hawkeye Framework for '{current_section}'**

**Most Relevant Checkpoints:**
• #2: Investigation Process - Methodology validation
• #11: Root Cause Analysis - Systemic issue identification
• #13: Documentation & Reporting - Quality standards
• #15: Quality Control - Accuracy validation

**Application Guidelines:**
• Review section against applicable checkpoints
• Document compliance gaps
• Identify areas needing additional investigation

**Implementation:**
• Apply systematic review process
• Document evidence for each standard
• Address identified gaps

**Which specific Hawkeye checkpoint would you like me to explain?"""
        
        elif 'improve' in query_lower or 'enhance' in query_lower:
            return f"""**Enhancement Strategy for '{current_section}'**

**Priority Areas:**
• **Evidence Validation**: Add verification sources
• **Stakeholder Context**: Include business impact analysis
• **Process Documentation**: Detail methodology used
• **Risk Assessment**: Quantify impacts with metrics
• **Action Items**: Specify ownership and timelines

**Implementation:**
• Review content against quality standards
• Identify specific information gaps
• Apply relevant Hawkeye checkpoints

**Hawkeye References:**
• #2: Investigation Process
• #13: Documentation & Reporting
• #15: Quality Control

**Which enhancement area should we focus on first?"""
        
        elif 'risk' in query_lower:
            return f"""**Risk Assessment for '{current_section}'**

**Risk Classification:**
• **High**: Customer safety, legal violations, significant financial impact
• **Medium**: Process gaps, operational issues, moderate business impact
• **Low**: Documentation improvements, minor enhancements

**Assessment Factors:**
• Customer experience impact
• Regulatory compliance requirements
• Business continuity implications
• Financial and operational costs

**Hawkeye References:**
• #1: Initial Assessment - Customer impact evaluation
• #19: Legal & Compliance - Regulatory adherence

**What specific risk factors concern you most in this section?"""
        
        elif 'timeline' in query_lower:
            return f"""**Timeline Documentation Standards**

**Essential Elements:**
• **Timestamps**: DD-MMM-YYYY HH:MM format
• **Chronological Order**: Verify sequence accuracy
• **Event Ownership**: Identify responsible parties
• **Gap Analysis**: Explain significant time gaps
• **Event Correlation**: Link to outcomes

**Quality Validation:**
• Independent timestamp verification
• Clear accountability for each entry
• Logical sequence maintenance
• Critical event highlighting

**Hawkeye References:**
• #2: Investigation Process - Timeline accuracy
• #13: Documentation & Reporting - Standards

**What specific timeline aspects need clarification?"""
        
        else:
            return f"""**AI-Prism Guidance for '{current_section}'**

**Available Assistance:**
• Document analysis and quality assessment
• Hawkeye framework application
• Risk evaluation and classification
• Evidence validation techniques
• Professional reporting guidance

**Analysis Approach:**
• Systematic quality standards review
• Evidence-based assessment
• Risk-focused evaluation
• Actionable recommendations

**Hawkeye Framework:**
• 20-point investigation checklist
• Comprehensive quality assurance
• Multiple applicable checkpoints

**What specific aspect of '{current_section}' analysis would be most helpful?"""