import json
import re
import boto3
import os
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
        
        # Check if response contains error
        if response.startswith('{"error"'):
            error_data = json.loads(response)
            print(f"Analysis error: {error_data.get('error')}")
            # Use mock response instead of returning error
            response = self._mock_ai_response(prompt)
            try:
                result = json.loads(response)
            except:
                result = {"feedback_items": []}
        else:
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
        """Invoke AWS Bedrock for AI analysis with App Runner configuration"""
        # In App Runner, credentials are provided via IAM role
        # Check for App Runner environment or local credentials
        is_app_runner = os.environ.get('FLASK_ENV') == 'production'
        has_local_credentials = (
            os.environ.get('AWS_ACCESS_KEY_ID') or 
            os.environ.get('AWS_PROFILE') or
            os.path.exists(os.path.expanduser('~/.aws/credentials')) or
            os.path.exists(os.path.expanduser('~/.aws/config'))
        )
        
        if not is_app_runner and not has_local_credentials:
            return self._mock_ai_response(user_prompt)
            
        try:
            # Get configuration from App Runner environment variables
            model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-7-sonnet-20250219-v1:0')
            region = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            max_tokens = int(os.environ.get('BEDROCK_MAX_TOKENS', '8192'))
            temperature = float(os.environ.get('BEDROCK_TEMPERATURE', '0.7'))
            reasoning_enabled = os.environ.get('REASONING_ENABLED', 'true').lower() == 'true'
            reasoning_budget = int(os.environ.get('REASONING_BUDGET_TOKENS', '2000'))
            
            print(f"Using Bedrock model: {model_id} in region: {region}")
            
            # Create Bedrock client with explicit region
            runtime = boto3.client(
                'bedrock-runtime',
                region_name=region
            )
            
            # Handle different model formats
            if 'claude-v2' in model_id:
                # Legacy Claude v2 format
                body = json.dumps({
                    "prompt": f"\n\nHuman: {system_prompt}\n\n{user_prompt}\n\nAssistant:",
                    "max_tokens_to_sample": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                })
            else:
                # Claude 3+ format with reasoning support
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
                
                # Add reasoning configuration if enabled and supported
                if reasoning_enabled and 'sonnet' in model_id and '20250219' in model_id:
                    request_body["reasoning"] = {
                        "enabled": True,
                        "budget_tokens": reasoning_budget
                    }
                    print(f"Reasoning enabled with budget: {reasoning_budget} tokens")
                
                body = json.dumps(request_body)
            
            response = runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Handle different response formats
            if 'claude-v2' in model_id:
                return response_body.get('completion', '')
            else:
                # Extract content from Claude 3+ response
                content = response_body.get('content', [])
                if content and len(content) > 0:
                    return content[0].get('text', '')
                else:
                    return response_body.get('completion', '')
            
        except Exception as e:
            print(f"Bedrock error: {str(e)}")
            
            # Enhanced error handling for App Runner
            error_details = str(e).lower()
            if 'credentials' in error_details or 'access' in error_details:
                if is_app_runner:
                    error_msg = "App Runner IAM role missing Bedrock permissions. Please check IAM configuration."
                else:
                    error_msg = "AWS credentials not configured. Please set up AWS credentials or IAM role."
            elif 'region' in error_details:
                error_msg = f"AWS region issue. Current region: {region}"
            elif 'model' in error_details or 'not found' in error_details:
                error_msg = f"Model access issue. Model ID: {model_id}. Please check model availability in {region}."
            elif 'throttling' in error_details or 'rate' in error_details:
                error_msg = f"Rate limiting encountered. Please try again in a moment."
            else:
                error_msg = f"Bedrock service error: {str(e)}"
            
            print(f"AI Error: {error_msg}")
            
            # Return error in expected format
            return json.dumps({"error": error_msg})
    
    def _mock_ai_response(self, user_prompt):
        """Mock AI response for local development"""
        return json.dumps({
            "feedback_items": [
                {
                    "id": "mock_001",
                    "type": "critical",
                    "category": "Investigation Process",
                    "description": "Critical gap in investigation methodology - missing evidence validation steps that could impact case outcome.",
                    "suggestion": "Implement comprehensive evidence validation protocol with multiple verification points.",
                    "example": "Include timestamps, data sources, chain of custody, and independent verification steps.",
                    "questions": [
                        "What specific investigation steps were taken?",
                        "How was the evidence validated?",
                        "Who verified the findings?"
                    ],
                    "hawkeye_refs": [2, 11, 13],
                    "risk_level": "High",
                    "confidence": 0.95
                },
                {
                    "id": "mock_002",
                    "type": "important",
                    "category": "Root Cause Analysis",
                    "description": "Root cause analysis lacks depth - process gaps not fully identified or addressed.",
                    "suggestion": "Conduct deeper 5-whys analysis to identify systemic issues.",
                    "example": "Trace back through decision points to find underlying process failures.",
                    "questions": [
                        "What systemic issues contributed to this case?",
                        "How can similar cases be prevented?"
                    ],
                    "hawkeye_refs": [11, 12],
                    "risk_level": "Medium",
                    "confidence": 0.85
                },
                {
                    "id": "mock_003",
                    "type": "suggestion",
                    "category": "Documentation and Reporting",
                    "description": "Documentation appears complete but could be enhanced with additional context for clarity.",
                    "suggestion": "Add more background information to help readers understand the full context.",
                    "example": "Include relevant policy references and historical context where applicable.",
                    "questions": [
                        "Is sufficient context provided for new readers?"
                    ],
                    "hawkeye_refs": [13],
                    "risk_level": "Low",
                    "confidence": 0.75
                },
                {
                    "id": "mock_004",
                    "type": "important",
                    "category": "Customer Impact",
                    "description": "Customer experience impact assessment needs more detailed analysis of trust and satisfaction metrics.",
                    "suggestion": "Include specific customer feedback and satisfaction scores where available.",
                    "example": "Reference customer complaints, satisfaction surveys, or trust metrics.",
                    "questions": [
                        "How did this impact customer trust?",
                        "What was the customer satisfaction impact?"
                    ],
                    "hawkeye_refs": [1, 10],
                    "risk_level": "Medium",
                    "confidence": 0.80
                },
                {
                    "id": "mock_005",
                    "type": "positive",
                    "category": "Preventative Actions",
                    "description": "Excellent preventative action plan with clear ownership and timelines.",
                    "suggestion": "Consider adding success metrics to track effectiveness.",
                    "example": "Define KPIs to measure prevention success over time.",
                    "questions": [
                        "How will success be measured?"
                    ],
                    "hawkeye_refs": [12, 18],
                    "risk_level": "Low",
                    "confidence": 0.90
                }
            ]
        })
    
    def _mock_chat_response(self, query, context):
        """Generate mock chat responses for local development"""
        query_lower = query.lower()
        current_section = context.get('current_section', 'current section')
        
        if 'help' in query_lower or 'how' in query_lower:
            return f"I'm AI-Prism, your AI assistant. For the {current_section}, I recommend focusing on the Hawkeye framework criteria. Key areas to review include investigation process, documentation quality, and risk assessment. I can help guide you through the analysis process."
        elif 'hawkeye' in query_lower or 'framework' in query_lower:
            return f"The Hawkeye framework includes 20 key checkpoints for thorough investigation. For {current_section}, focus on checkpoints #2 (Investigation Process), #11 (Root Cause Analysis), and #13 (Documentation). I can provide specific guidance based on your document content."
        elif 'risk' in query_lower:
            return f"Risk assessment should consider customer impact, process gaps, and compliance issues. For {current_section}, evaluate High/Medium/Low risk levels based on potential business impact. I can help you assess the risk levels appropriately."
        elif 'feedback' in query_lower or 'comment' in query_lower:
            return f"When reviewing feedback for {current_section}, accept items that add value and reject generic comments. Focus on actionable suggestions with clear Hawkeye references. I can help you evaluate the quality of feedback items."
        else:
            return f"I understand you're asking about \"{query}\" in relation to {current_section}. I can help with document analysis, Hawkeye framework guidance, and review processes. What specific aspect would you like guidance on?"


    def process_chat_query(self, query, context):
        """Process chat queries with AI-Prism focused on guidelines and document analysis"""
        # Check for App Runner environment or local credentials
        is_app_runner = os.environ.get('FLASK_ENV') == 'production'
        has_local_credentials = (
            os.environ.get('AWS_ACCESS_KEY_ID') or 
            os.environ.get('AWS_PROFILE') or
            os.path.exists(os.path.expanduser('~/.aws/credentials')) or
            os.path.exists(os.path.expanduser('~/.aws/config'))
        )
        
        if not is_app_runner and not has_local_credentials:
            return self._mock_chat_response(query, context)
            
        try:
            context_info = f"""
            Current Section: {context.get('current_section', 'Current section')}
            Document Type: Full Write-up Investigation
            Hawkeye Framework: 20-point comprehensive checklist
            Session Progress: {context.get('session_progress', 'In progress')}
            Guidelines Preference: {context.get('guidelines_preference', 'both')}
            """
            
            prompt = f"""You are AI-Prism, an AI assistant for document analysis using the Hawkeye framework.
            
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
            
            system_prompt = """You are AI-Prism, a professional AI assistant specialized in document analysis using the Hawkeye framework. 
            You provide clear, direct guidance on document review processes, compliance requirements, and quality standards.
            Focus on being helpful, accurate, and professional in all responses."""
            
            response = self._invoke_bedrock(system_prompt, prompt)
            
            # Check if response contains error
            if response.startswith('{"error"'):
                return self._mock_chat_response(query, context)
            
            return response
        except Exception as e:
            print(f"Chat error: {str(e)}")
            return self._mock_chat_response(query, context)