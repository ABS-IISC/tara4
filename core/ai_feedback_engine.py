import json
import re
import boto3
import os
import time
from datetime import datetime
from collections import defaultdict
from config.model_config import model_config

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
        
        prompt = f"""DOCUMENT ANALYSIS TASK:
Analyze section "{section_name}" from a CT EE investigation writeup against Hawkeye framework standards.

{section_guidance}

SECTION CONTENT:
{content[:3000]}

CRITICAL ANALYSIS REQUIREMENTS:
1. IDENTIFY SPECIFIC GAPS: What concrete information is missing?
2. ASSESS COMPLIANCE: Does content meet investigation standards?
3. EVALUATE DEPTH: Is analysis thorough enough for the issue type?
4. CHECK COMPLETENESS: Are all required elements present?
5. VERIFY ACCURACY: Are facts, dates, and processes correct?

FOCUS AREAS:
- Missing critical details that impact investigation quality
- Insufficient evidence or documentation
- Gaps in root cause analysis or preventative actions
- Unclear accountability or ownership
- Inadequate customer impact assessment

Return precise, actionable feedback in JSON format:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion",
            "category": "specific Hawkeye area",
            "description": "Precise gap or issue identified",
            "suggestion": "Specific action to address the gap",
            "questions": ["Direct question to address"],
            "hawkeye_refs": [checkpoint_numbers],
            "risk_level": "High|Medium|Low",
            "confidence": 0.95
        }}
    ]
}}"""

        system_prompt = f"""You are a CT EE investigation expert conducting detailed document analysis. Focus on identifying specific gaps, missing information, and compliance issues. Be precise, direct, and actionable in your feedback.

{self.hawkeye_checklist}

Analyze documents for:
- Specific missing information that impacts investigation quality
- Compliance gaps with investigation standards
- Insufficient depth in analysis or evidence
- Unclear accountability and ownership
- Inadequate risk assessment or customer impact evaluation

Provide only meaningful, actionable feedback that improves document quality. Structure responses professionally with clear bullet points and specific recommendations."""

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
            
            print(f"🎭 Falling back to mock response for section: {section_name}")
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
            print(f"🔄 Creating safe fallback response")
            result = {
                "feedback_items": [],
                "error": "Failed to parse AI response",
                "fallback": True
            }

        # Ensure result has the expected structure
        if 'feedback_items' not in result:
            result['feedback_items'] = []
        
        # Validate and enhance feedback items
        validated_items = []
        for i, item in enumerate(result.get('feedback_items', [])):
            if not isinstance(item, dict):
                print(f"⚠️ Skipping invalid feedback item {i}: {type(item)}")
                continue
                
            # Ensure all required fields exist
            validated_item = {
                'id': item.get('id', f"{section_name}_{i}_{datetime.now().strftime('%H%M%S')}"),
                'type': item.get('type', 'suggestion'),
                'category': item.get('category', 'General'),
                'description': item.get('description', 'No description provided'),
                'suggestion': item.get('suggestion', ''),
                'example': item.get('example', ''),
                'questions': item.get('questions', []) if isinstance(item.get('questions'), list) else [],
                'hawkeye_refs': item.get('hawkeye_refs', []) if isinstance(item.get('hawkeye_refs'), list) else [],
                'risk_level': item.get('risk_level', 'Low'),
                'confidence': float(item.get('confidence', 0.8)) if isinstance(item.get('confidence'), (int, float)) else 0.8
            }
            
            # Add hawkeye references if missing
            if not validated_item['hawkeye_refs']:
                validated_item['hawkeye_refs'] = self._get_hawkeye_references(
                    validated_item['category'], 
                    validated_item['description']
                )
            
            # Classify risk level if not provided or invalid
            if validated_item['risk_level'] not in ['High', 'Medium', 'Low']:
                validated_item['risk_level'] = self._classify_risk_level(validated_item)
            
            validated_items.append(validated_item)
        
        # Update result with validated items
        result['feedback_items'] = validated_items
        
        # Cache the result
        self.feedback_cache[cache_key] = result
        
        print(f"✅ Analysis complete: {len(validated_items)} validated feedback items")
        return result

    def _get_section_guidance(self, section_name):
        """Get section-specific analysis guidance"""
        section_lower = section_name.lower()
        
        if "timeline" in section_lower:
            return """
            TIMELINE ANALYSIS REQUIREMENTS:
            - DATES: Verify all dates are accurate, formatted consistently (DD-MMM-YYYY)
            - SEQUENCE: Check chronological order, identify time gaps >24 hours
            - EVENTS: Ensure all critical events are documented (first detection, escalation, resolution)
            - CORRELATION: Link timeline events to enforcement actions and customer impact
            - COMPLETENESS: Verify no missing steps between problem identification and resolution
            - ACCOUNTABILITY: Each event should have clear ownership and action taken
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
            ROOT CAUSE & PREVENTATIVE ACTION ANALYSIS:
            - 5 WHYS DEPTH: Each "why" must lead to deeper systemic understanding
            - SYSTEMIC vs SYMPTOMATIC: Distinguish between surface issues and underlying causes
            - ACTIONABILITY: Each preventative action must be specific, measurable, achievable
            - OWNERSHIP: Clear DRI (Directly Responsible Individual) for each action
            - TIMELINE: Specific completion dates, not vague "Q1" or "soon"
            - EFFECTIVENESS: How will success be measured? What metrics will track improvement?
            - PROCESS GAPS: Identify specific process failures that enabled the issue
            - PLACEHOLDER STATUS: Mark incomplete items clearly, provide completion timeline
            """
        elif "executive summary" in section_lower or "summary" in section_lower:
            return """
            EXECUTIVE SUMMARY REQUIREMENTS:
            - IMPACT STATEMENT: Quantify customer, business, and financial impact
            - KEY FINDINGS: 3-5 most critical discoveries from investigation
            - ROOT CAUSE: Single sentence summary of primary cause
            - ACTIONS TAKEN: Immediate response and resolution steps
            - PREVENTION: Key preventative measures implemented
            - ACCOUNTABILITY: Clear ownership for ongoing actions
            - TIMELINE: When issue occurred, detected, and resolved
            - COMPLETENESS: Can executive understand full situation from summary alone?
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
            # Return mock response for testing
            return self._mock_ai_response(user_prompt)
    

    

    
    def _mock_ai_response(self, user_prompt):
        """Enhanced mock AI response for development/testing with realistic feedback"""
        # Simulate processing delay
        time.sleep(2)
        
        # Generate contextual mock responses based on prompt content
        prompt_lower = user_prompt.lower()
        
        if "timeline" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"mock_timeline_{int(time.time())}",
                        "type": "critical",
                        "category": "Timeline of Events",
                        "description": "Timeline lacks specific timestamps and chronological accuracy. Missing critical event markers that could impact investigation validity.",
                        "suggestion": "Add precise timestamps (DD-MMM-YYYY HH:MM format) and ensure chronological order with clear event markers.",
                        "example": "Use format: '15-Jan-2024 14:30 - Initial detection' rather than vague time references.",
                        "questions": [
                            "Are all timestamps accurate and verifiable?",
                            "What events occurred between detection and response?",
                            "Who was responsible for each timeline entry?"
                        ],
                        "hawkeye_refs": [2, 13],
                        "risk_level": "High",
                        "confidence": 0.92
                    }
                ]
            })
        elif "root cause" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"mock_rootcause_{int(time.time())}",
                        "type": "critical",
                        "category": "Root Cause Analysis",
                        "description": "Root cause analysis insufficient - lacks 5-whys methodology and systemic issue identification. Current analysis addresses symptoms rather than underlying causes.",
                        "suggestion": "Implement comprehensive 5-whys analysis to identify true systemic root causes. Include process gap analysis.",
                        "example": "Why did X happen? Because Y. Why did Y happen? Because Z. Continue until systemic cause identified.",
                        "questions": [
                            "What process failures enabled this issue?",
                            "How can we prevent similar systemic problems?",
                            "What organizational changes are needed?"
                        ],
                        "hawkeye_refs": [11, 12],
                        "risk_level": "High",
                        "confidence": 0.95
                    }
                ]
            })
        else:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"mock_general_{int(time.time())}",
                        "type": "important",
                        "category": "Investigation Process",
                        "description": "Section requires enhanced analysis depth and evidence validation. Current content meets basic requirements but lacks comprehensive investigation rigor.",
                        "suggestion": "Strengthen evidence validation protocols and include cross-verification steps for critical findings.",
                        "example": "Add independent verification sources and document validation methodology used.",
                        "questions": [
                            "What evidence supports the key conclusions?",
                            "How was the evidence independently verified?",
                            "What additional investigation steps could strengthen this analysis?"
                        ],
                        "hawkeye_refs": [2, 15],
                        "risk_level": "Medium",
                        "confidence": 0.85
                    },
                    {
                        "id": f"mock_documentation_{int(time.time())}",
                        "type": "suggestion",
                        "category": "Documentation and Reporting",
                        "description": "Documentation quality is adequate but could benefit from enhanced clarity and stakeholder context.",
                        "suggestion": "Include executive summary section and ensure technical details are accessible to non-technical stakeholders.",
                        "example": "Add glossary of technical terms and provide context for business impact.",
                        "questions": [
                            "Will all stakeholders understand the technical content?",
                            "Is the business impact clearly articulated?"
                        ],
                        "hawkeye_refs": [13, 17],
                        "risk_level": "Low",
                        "confidence": 0.78
                    }
                ]
            })
    
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
        """Generate enhanced structured mock chat responses for development/testing"""
        # Simulate processing delay
        time.sleep(1)
        
        query_lower = query.lower()
        current_section = context.get('current_section', 'current section')
        
        if 'help' in query_lower or 'how' in query_lower:
            return """**AI-Prism Document Analysis Assistance**

• **Current Focus**: Analysis of '{0}' section using Hawkeye framework methodology
• **Core Capabilities**: Investigation quality assessment, compliance validation, risk evaluation
• **Framework Application**: 20-point comprehensive checklist for thorough document review

**Key Areas I Can Help With:**
• Investigation methodology and evidence validation
• Risk assessment and classification protocols
• Documentation quality and compliance standards
• Stakeholder communication and reporting clarity

**Hawkeye References:**
• Checkpoint #2: Investigation Process - Methodology validation
• Checkpoint #15: Quality Control - Standards compliance

**Recommended Next Steps:**
• Identify specific areas needing improvement in current section
• Apply relevant Hawkeye checkpoints for comprehensive analysis

**Follow-up Question:** What particular aspect of '{0}' would you like me to analyze in detail?""".format(current_section)
        
        elif 'hawkeye' in query_lower or 'framework' in query_lower:
            return """**Hawkeye Framework Application**

• **Framework Overview**: Comprehensive 20-point investigation checklist ensuring thorough document analysis
• **Current Section Relevance**: '{0}' requires specific checkpoint validation for compliance
• **Quality Assurance**: Systematic approach to investigation documentation and reporting

**Most Relevant Checkpoints for '{0}':**
• Checkpoint #2: Investigation Process - Ensure thorough methodology and evidence validation
• Checkpoint #11: Root Cause Analysis - Identify systemic issues and underlying causes
• Checkpoint #13: Documentation & Reporting - Maintain professional quality standards
• Checkpoint #15: Quality Control - Validate findings and ensure accuracy

**Implementation Guidelines:**
• Apply systematic review process for each checkpoint
• Document evidence supporting compliance with each standard
• Identify gaps requiring additional investigation or clarification

**Recommended Actions:**
• Review current section against applicable checkpoints
• Document compliance status for each relevant standard

**Follow-up Question:** Which specific Hawkeye checkpoint would you like me to explain in greater detail?""".format(current_section)
        
        elif 'risk' in query_lower:
            return """**Risk Assessment Framework**

• **Assessment Scope**: Comprehensive risk evaluation for '{0}' section
• **Classification System**: Three-tier risk categorization with specific criteria
• **Impact Analysis**: Customer, business, and operational impact consideration

**Risk Classification Criteria:**
• **High Risk**: Customer safety concerns, legal compliance violations, significant financial impact, regulatory non-compliance
• **Medium Risk**: Process gaps, operational inefficiencies, moderate business impact, stakeholder concerns
• **Low Risk**: Documentation improvements, minor enhancements, formatting issues, clarity improvements

**Assessment Factors:**
• Customer experience and trust impact
• Regulatory and legal compliance requirements
• Business continuity and operational stability
• Financial implications and cost considerations

**Hawkeye References:**
• Checkpoint #1: Initial Assessment - Customer experience impact evaluation
• Checkpoint #19: Legal and Compliance - Regulatory adherence validation

**Recommended Actions:**
• Conduct systematic risk assessment using established criteria
• Document risk rationale with supporting evidence

**Follow-up Question:** What specific risk factors are you most concerned about in this section?""".format(current_section)
        
        elif 'feedback' in query_lower or 'comment' in query_lower:
            return """**Feedback Evaluation Guidelines**

• **Evaluation Framework**: Systematic approach to assessing AI-generated feedback quality
• **Quality Standards**: Hawkeye framework alignment and actionable improvement focus
• **Decision Criteria**: Clear guidelines for acceptance and rejection decisions

**Accept Feedback That:**
• Provides specific, actionable improvement recommendations
• References relevant Hawkeye checkpoints with clear rationale
• Addresses compliance gaps or quality enhancement opportunities
• Includes concrete examples or implementation guidance
• Aligns with investigation standards and best practices

**Reject Feedback That:**
• Offers generic or vague suggestions without specific guidance
• Lacks alignment with established investigation standards
• Provides no supporting rationale or evidence
• Duplicates existing content without adding value
• Falls outside scope of current section analysis

**Quality Assessment Process:**
• Evaluate feedback against Hawkeye framework relevance
• Assess actionability and implementation feasibility
• Consider stakeholder value and investigation enhancement

**Recommended Actions:**
• Apply consistent evaluation criteria for all feedback items
• Document rationale for acceptance and rejection decisions

**Follow-up Question:** Would you like help evaluating specific feedback items for '{0}'?""".format(current_section)
        
        elif 'improve' in query_lower or 'enhance' in query_lower:
            return """**Section Enhancement Strategy**

• **Improvement Focus**: Systematic enhancement of '{0}' section quality and compliance
• **Quality Standards**: Hawkeye framework alignment and professional documentation requirements
• **Enhancement Areas**: Evidence validation, stakeholder clarity, process documentation

**Priority Enhancement Areas:**
• **Evidence Validation**: Add independent verification sources and cross-reference documentation
• **Stakeholder Context**: Include comprehensive business impact analysis and stakeholder considerations
• **Process Documentation**: Detail methodology used and provide clear procedural references
• **Risk Assessment**: Quantify potential impacts with specific metrics and measurements
• **Action Items**: Specify clear ownership, timelines, and accountability measures

**Implementation Guidelines:**
• Conduct systematic review of current content against quality standards
• Identify specific gaps requiring additional information or clarification
• Apply Hawkeye checkpoints for comprehensive quality validation

**Hawkeye References:**
• Checkpoint #2: Investigation Process - Methodology documentation
• Checkpoint #13: Documentation & Reporting - Quality standards
• Checkpoint #15: Quality Control - Validation processes

**Recommended Actions:**
• Prioritize enhancement areas based on impact and feasibility
• Develop implementation timeline with specific milestones

**Follow-up Question:** Which enhancement area would you like to focus on first for maximum impact?""".format(current_section)
        
        elif 'timeline' in query_lower:
            return """**Timeline Documentation Standards**

• **Documentation Requirements**: Precise chronological documentation with verified timestamps
• **Quality Standards**: Hawkeye framework compliance for timeline accuracy and completeness
• **Validation Process**: Independent verification of events and sequence accuracy

**Essential Timeline Elements:**
• **Precise Timestamps**: Use standardized DD-MMM-YYYY HH:MM format for all entries
• **Chronological Order**: Verify sequence accuracy with clear event progression
• **Event Ownership**: Identify responsible parties and decision-makers for each entry
• **Gap Analysis**: Explain any significant time gaps with supporting rationale
• **Event Correlation**: Link timeline events to outcomes and investigation findings

**Quality Validation Criteria:**
• All timestamps independently verified and documented
• Clear accountability established for each timeline entry
• Logical sequence maintained throughout documentation
• Critical events properly highlighted and explained

**Hawkeye References:**
• Checkpoint #2: Investigation Process - Timeline accuracy requirements
• Checkpoint #13: Documentation & Reporting - Chronological documentation standards

**Recommended Actions:**
• Conduct comprehensive timeline review for accuracy and completeness
• Validate all timestamps through independent sources
• Document verification methodology used

**Follow-up Question:** What specific timeline aspects require clarification or additional validation?"""
        
        else:
            return """**AI-Prism Analysis Guidance**

• **Query Understanding**: Analysis request for "{0}" regarding '{1}' section
• **Expertise Areas**: Document analysis, quality assessment, compliance validation, risk evaluation
• **Framework Application**: Hawkeye methodology for comprehensive investigation review

**Available Assistance Areas:**
• **Document Analysis**: Comprehensive quality assessment and compliance validation
• **Hawkeye Framework**: Application of 20-point investigation checklist
• **Risk Evaluation**: Classification and impact assessment protocols
• **Evidence Validation**: Verification techniques and quality standards
• **Stakeholder Communication**: Professional reporting and clarity enhancement

**Analysis Approach:**
• Systematic review using established quality standards
• Evidence-based assessment with supporting documentation
• Risk-focused evaluation with clear classification criteria
• Actionable recommendations with implementation guidance

**Hawkeye References:**
• Multiple checkpoints applicable based on specific analysis requirements
• Framework provides comprehensive quality assurance methodology

**Recommended Next Steps:**
• Clarify specific analysis requirements for targeted guidance
• Identify priority areas for detailed investigation

**Follow-up Question:** What specific aspect of '{1}' analysis would be most helpful for your current needs?""".format(query, current_section)


    def process_chat_query(self, query, context):
        """Process chat queries with AI-Prism focused on guidelines and document analysis"""
        print(f"Processing chat query: {query[:50]}...")
        
        context_info = f"""
        Current Section: {context.get('current_section', 'Current section')}
        Document Type: Full Write-up Investigation
        Hawkeye Framework: 20-point comprehensive checklist
        Current Feedback Count: {context.get('current_feedback', [])}
        Accepted Items: {context.get('accepted_count', 0)}
        Rejected Items: {context.get('rejected_count', 0)}
        """
        
        prompt = f"""DOCUMENT ANALYSIS GUIDANCE REQUEST:
        
        CONTEXT:
        {context_info}
        
        USER QUESTION: {query}
        
        HAWKEYE FRAMEWORK REFERENCE:
        {self.hawkeye_checklist}
        
        RESPONSE REQUIREMENTS:
        1. Structure your response with clear sections using bullet points
        2. Use professional, guidelines-oriented language
        3. Reference specific Hawkeye checkpoints when relevant
        4. Provide actionable recommendations
        5. Use proper formatting with line breaks and justification
        6. Include specific examples when helpful
        7. End with a follow-up question to continue the conversation
        
        Format your response as:
        **[Main Topic]**
        
        • Key Point 1: [Detailed explanation]
        • Key Point 2: [Detailed explanation]
        
        **Hawkeye References:**
        • Checkpoint #X: [Specific relevance]
        
        **Recommended Actions:**
        • Action 1: [Specific step]
        • Action 2: [Specific step]
        
        **Follow-up Question:** [Engaging question to continue discussion]
        
        Provide helpful, specific guidance that references the Hawkeye guidelines when relevant. Be professional, structured, and actionable."""
        
        system_prompt = """You are AI-Prism, a professional CT EE investigation specialist providing expert guidance on document analysis and compliance. 
        
        Your responses must be:
        - Structured with clear bullet points and sections
        - Professional and guidelines-oriented
        - Actionable with specific recommendations
        - Referenced to Hawkeye framework when relevant
        - Formatted for easy reading with proper line breaks
        - Concluded with engaging follow-up questions
        
        Always maintain a professional tone while being helpful and accessible."""
        
        try:
            response = self._invoke_bedrock(system_prompt, prompt)
            return self._format_chat_response(response)
        except Exception as e:
            print(f"Chat processing error: {str(e)}")
            return self._mock_chat_response(query, context)