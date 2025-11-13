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
        """Analyze section with enhanced Hawkeye framework - focused and actionable"""
        cache_key = f"{section_name}_{hash(content)}"
        if cache_key in self.feedback_cache:
            return self.feedback_cache[cache_key]

        # Get section-specific guidance
        section_guidance = self._get_section_guidance(section_name)
        
        prompt = f"""TASK: Analyze "{section_name}" for CT EE investigation quality.

{section_guidance}

CONTENT:
{content[:2000]}

REQUIREMENTS:
• Find 2-3 specific gaps only (not generic issues)
• Focus on missing critical elements
• Provide direct, actionable fixes
• Reference Hawkeye checkpoints
• Be concise - max 1-2 sentences per item

FORMAT:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion",
            "category": "Investigation|Root Cause|Documentation|Timeline|Evidence",
            "description": "Specific missing element or gap (max 100 chars)",
            "suggestion": "Direct action to fix (max 80 chars)",
            "questions": ["Key question to address?"],
            "hawkeye_refs": [checkpoint_numbers],
            "risk_level": "High|Medium|Low",
            "confidence": 0.85
        }}
    ]
}}"""

        system_prompt = f"""You are a CT EE investigation specialist. Provide focused, actionable analysis.

{self.hawkeye_checklist}

RULES:
• Maximum 3 feedback items
• Each item must be specific to this content
• Focus on critical gaps only
• Keep descriptions under 100 characters
• Suggestions must be actionable
• Reference relevant Hawkeye checkpoints

AVOID:
• Generic advice
• Lengthy explanations
• Minor issues
• Repetitive points"""

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
        
        # Validate and enhance feedback items - limit to top 3
        validated_items = []
        for i, item in enumerate(result.get('feedback_items', [])[:3]):  # Limit to 3 items
            if not isinstance(item, dict):
                print(f"⚠️ Skipping invalid feedback item {i}: {type(item)}")
                continue
                
            # Ensure all required fields exist with improved defaults
            validated_item = {
                'id': item.get('id', f"{section_name}_{i}_{datetime.now().strftime('%H%M%S')}"),
                'type': item.get('type', 'suggestion'),
                'category': item.get('category', 'Investigation Process'),
                'description': self._truncate_text(item.get('description', 'Analysis gap identified'), 100),
                'suggestion': self._truncate_text(item.get('suggestion', ''), 80),
                'example': self._truncate_text(item.get('example', ''), 60),
                'questions': item.get('questions', [])[:2] if isinstance(item.get('questions'), list) else [],  # Limit to 2 questions
                'hawkeye_refs': item.get('hawkeye_refs', [])[:3] if isinstance(item.get('hawkeye_refs'), list) else [],  # Limit to 3 refs
                'risk_level': item.get('risk_level', 'Low'),
                'confidence': float(item.get('confidence', 0.8)) if isinstance(item.get('confidence'), (int, float)) else 0.8
            }
            
            # Add hawkeye references if missing
            if not validated_item['hawkeye_refs']:
                validated_item['hawkeye_refs'] = self._get_hawkeye_references(
                    validated_item['category'], 
                    validated_item['description']
                )[:2]  # Limit to 2 references
            
            # Classify risk level if not provided or invalid
            if validated_item['risk_level'] not in ['High', 'Medium', 'Low']:
                validated_item['risk_level'] = self._classify_risk_level(validated_item)
            
            validated_items.append(validated_item)
        
        # Update result with validated items
        result['feedback_items'] = validated_items
        
        # Cache the result
        self.feedback_cache[cache_key] = result
        
        print(f"✅ Analysis complete: {len(validated_items)} focused feedback items (max 3)")
        return result

    def _get_section_guidance(self, section_name):
        """Get focused section-specific analysis guidance"""
        section_lower = section_name.lower()
        
        if "timeline" in section_lower:
            return """TIMELINE FOCUS:
• Missing timestamps (DD-MMM-YYYY format)
• Gaps >24hrs without explanation
• Unclear event ownership
• Critical events missing"""
        elif "resolving action" in section_lower:
            return """RESOLVING ACTIONS FOCUS:
• Incomplete resolution steps
• Missing validation evidence
• Unclear ownership/dates
• No impact assessment"""
        elif "root cause" in section_lower or "preventative action" in section_lower:
            return """ROOT CAUSE FOCUS:
• Lacks 5-whys depth
• Addresses symptoms not causes
• Vague preventative actions
• Missing success metrics"""
        elif "executive summary" in section_lower or "summary" in section_lower:
            return """SUMMARY FOCUS:
• Missing quantified impact
• Unclear root cause statement
• Incomplete action summary
• Not executive-ready"""
        elif "background" in section_lower:
            return """BACKGROUND FOCUS:
• Context unclear/irrelevant
• Missing key milestones
• Process maturity unclear
• No policy references"""
        else:
            return """GENERAL FOCUS:
• Information gaps
• Evidence quality issues
• Unclear accountability
• Missing customer impact"""

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
        """Invoke AWS Bedrock using model configuration - FOR ANALYSIS ONLY"""
        try:
            # Check if credentials are available
            if not model_config.has_credentials():
                print("⚠️ No AWS credentials found - using mock analysis response")
                return self._mock_ai_response(user_prompt)
            
            config = model_config.get_model_config()
            
            # Try to create Bedrock client with profile first, then fallback to default
            runtime = None
            try:
                # Try with admin-abhsatsa profile
                session = boto3.Session(profile_name='admin-abhsatsa')
                runtime = session.client(
                    'bedrock-runtime',
                    region_name=config['region']
                )
                print(f"🔑 Using AWS profile: admin-abhsatsa")
            except Exception as profile_error:
                print(f"⚠️ Profile error: {profile_error}")
                # Fallback to default session
                runtime = boto3.client(
                    'bedrock-runtime',
                    region_name=config['region']
                )
                print(f"🔑 Using default AWS credentials")
            
            # Generate request body using model config
            body = model_config.get_bedrock_request_body(system_prompt, user_prompt)
            
            print(f"🤖 Invoking {config['model_name']} for analysis (ID: {config['model_id']})")
            
            response = runtime.invoke_model(
                body=body,
                modelId=config['model_id'],
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            result = model_config.extract_response_content(response_body)
            
            print(f"✅ Claude analysis response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            print(f"❌ Bedrock analysis error: {str(e)}")
            
            # Provide specific error guidance
            error_str = str(e).lower()
            if 'credentials' in error_str or 'access' in error_str:
                print("💡 Fix: Check AWS credentials configuration")
            elif 'region' in error_str:
                print("💡 Fix: Verify AWS region and Bedrock availability")
            elif 'not found' in error_str or 'model' in error_str:
                print("💡 Fix: Verify Claude model access in your AWS account")
            elif 'throttling' in error_str or 'limit' in error_str:
                print("💡 Fix: Rate limiting - try again in a moment")
            
            # Return mock analysis response for testing
            print("🎭 Falling back to mock analysis response")
            return self._mock_ai_response(user_prompt)
    

    

    
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
                        "id": f"mock_timeline_{int(time.time())}",
                        "type": "important",
                        "category": "Timeline",
                        "description": "Missing timestamps and >24hr gaps unexplained",
                        "suggestion": "Add DD-MMM-YYYY HH:MM format and gap explanations",
                        "questions": ["Who owned each timeline entry?"],
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
                        "id": f"mock_rootcause_{int(time.time())}",
                        "type": "critical",
                        "category": "Root Cause",
                        "description": "Analysis lacks 5-whys depth, addresses symptoms not causes",
                        "suggestion": "Apply 5-whys to identify systemic root causes",
                        "questions": ["What process failures enabled this?"],
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
                        "id": f"mock_summary_{int(time.time())}",
                        "type": "important",
                        "category": "Documentation",
                        "description": "Missing quantified customer/business impact metrics",
                        "suggestion": "Add specific impact numbers and affected customer count",
                        "questions": ["What was the measurable business impact?"],
                        "hawkeye_refs": [1, 13],
                        "risk_level": "Medium",
                        "confidence": 0.85
                    }
                ]
            })
        else:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"mock_general_{int(time.time())}",
                        "type": "important",
                        "category": "Investigation",
                        "description": "Lacks independent evidence verification sources",
                        "suggestion": "Add cross-verification and validation methodology",
                        "questions": ["How was evidence independently verified?"],
                        "hawkeye_refs": [2, 15],
                        "risk_level": "Medium",
                        "confidence": 0.85
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
    
    def _truncate_text(self, text, max_length):
        """Truncate text to specified length with ellipsis"""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _mock_chat_response(self, query, context):
        """Generate concise, focused mock chat responses"""
        # Simulate processing delay
        time.sleep(0.5)
        
        query_lower = query.lower()
        current_section = context.get('current_section', 'current section')
        
        if 'help' in query_lower or 'how' in query_lower:
            return f"""**Quick Help for {current_section}**

• **Analysis**: Review against Hawkeye checkpoints
• **Feedback**: Accept specific, actionable items
• **Risk**: Assess High/Medium/Low impact
• **Questions**: Ask about specific gaps or improvements

**What specific aspect needs clarification?**"""
        
        elif 'hawkeye' in query_lower or 'framework' in query_lower:
            return f"""**Hawkeye for {current_section}**

**Key Checkpoints:**
• #2: Investigation methodology
• #11: Root cause depth
• #13: Documentation quality
• #15: Evidence validation

**Which checkpoint needs explanation?**"""
        
        elif 'risk' in query_lower:
            return f"""**Risk Assessment**

• **High**: Customer safety, legal issues, major impact
• **Medium**: Process gaps, operational issues
• **Low**: Documentation improvements

**Current section risk factors?**"""
        
        elif 'feedback' in query_lower or 'comment' in query_lower:
            return """**Feedback Guidelines**

**Accept if:**
• Specific and actionable
• References Hawkeye checkpoints
• Addresses real gaps

**Reject if:**
• Generic or vague
• No clear action
• Outside scope

**Which feedback item needs evaluation?**"""
        
        elif 'improve' in query_lower or 'enhance' in query_lower:
            return f"""**Improvement Areas for {current_section}**

• **Evidence**: Add verification sources
• **Impact**: Quantify business effects
• **Actions**: Specify owners and dates
• **Process**: Document methodology

**Which area to focus on?**"""
        
        elif 'timeline' in query_lower:
            return """**Timeline Standards**

• **Format**: DD-MMM-YYYY HH:MM
• **Gaps**: Explain >24hr delays
• **Ownership**: Who did what
• **Sequence**: Chronological order

**Specific timeline issue?**"""
        
        else:
            return f"""**AI-Prism for {current_section}**

**I can help with:**
• Gap analysis
• Risk assessment
• Hawkeye compliance
• Evidence validation

**What specific question do you have?**"""


    def process_chat_query(self, query, context):
        """Process chat queries with focused, concise responses"""
        print(f"Processing chat query: {query[:50]}...")
        
        # Check if we should use real AI or mock responses
        if not model_config.has_credentials():
            print("⚠️ No AWS credentials - using mock chat response")
            return self._mock_chat_response(query, context)
        
        current_section = context.get('current_section', 'Current section')
        feedback_count = len(context.get('current_feedback', []))
        
        prompt = f"""QUESTION: {query}
SECTION: {current_section}
FEEDBACK ITEMS: {feedback_count}

HAWKEYE CHECKPOINTS:
{self.hawkeye_checklist[:500]}...

RESPONSE RULES:
• Max 100 words
• Use bullet points
• Be specific to the question
• Reference 1-2 Hawkeye checkpoints if relevant
• End with one follow-up question
• No lengthy explanations

FORMAT:
**[Topic]**
• Point 1
• Point 2
**Next:** Follow-up question?"""
        
        system_prompt = """You are AI-Prism providing concise CT EE investigation guidance.
        
        Rules:
        - Maximum 100 words
        - Bullet points only
        - Direct answers
        - One follow-up question
        - Professional tone"""
        
        try:
            # Use real Bedrock for chat
            import boto3
            config = model_config.get_model_config()
            
            # Try to create Bedrock client with profile first, then fallback to default
            runtime = None
            try:
                # Try with admin-abhsatsa profile
                session = boto3.Session(profile_name='admin-abhsatsa')
                runtime = session.client(
                    'bedrock-runtime',
                    region_name=config['region']
                )
                print(f"🔑 Chat using AWS profile: admin-abhsatsa")
            except Exception as profile_error:
                print(f"⚠️ Profile error: {profile_error}")
                # Fallback to default session
                runtime = boto3.client(
                    'bedrock-runtime',
                    region_name=config['region']
                )
                print(f"🔑 Chat using default AWS credentials")
            
            body = model_config.get_bedrock_request_body(system_prompt, prompt)
            
            print(f"🤖 Chat query to {config['model_name']}")
            
            response = runtime.invoke_model(
                body=body,
                modelId=config['model_id'],
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            result = model_config.extract_response_content(response_body)
            
            print(f"✅ Claude chat response received")
            return self._format_chat_response(result)
            
        except Exception as e:
            print(f"❌ Chat processing error: {str(e)}")
            print("🎭 Falling back to mock chat response")
            return self._mock_chat_response(query, context)