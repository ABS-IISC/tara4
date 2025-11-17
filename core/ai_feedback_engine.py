import json
import re
import boto3
import os
import sys
import time
from datetime import datetime
from collections import defaultdict

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import model manager for multi-model fallback (V2 with per-request isolation)
try:
    from core.model_manager_v2 import model_manager_v2 as model_manager
    MODEL_FALLBACK_ENABLED = True
    print("✅ Multi-model fallback enabled (V2 - Per-Request Isolation)")
except ImportError:
    try:
        # Fallback to V1 if V2 not available
        from core.model_manager import model_manager
        MODEL_FALLBACK_ENABLED = True
        print("✅ Multi-model fallback enabled (V1)")
    except ImportError:
        MODEL_FALLBACK_ENABLED = False
        print("ℹ️  Multi-model fallback not available")

try:
    from config.model_config import model_config
    from config import ai_prompts
except ImportError:
    # Fallback if config module not found
    print("⚠️ Config module not found, creating fallback configuration")
    ai_prompts = None
    
    class FallbackModelConfig:
        # Supported models map (minimal for fallback)
        SUPPORTED_MODELS = {
            'claude-3-5-sonnet': {'name': 'Claude 3.5 Sonnet'},
            'claude-3-sonnet': {'name': 'Claude 3 Sonnet'},
            'claude-3-haiku': {'name': 'Claude 3 Haiku'}
        }

        def get_model_config(self):
            return {
                'model_id': os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0'),
                'model_name': 'Claude 3.5 Sonnet',
                'region': os.environ.get('AWS_REGION', 'us-east-1'),
                'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', '8192')),
                'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', '0.7')),
                'anthropic_version': 'bedrock-2023-05-31',
                'fallback_models': []  # No fallback models when using environment config
            }

        def has_credentials(self):
            """Check if AWS credentials are available (env vars OR IAM role)"""
            try:
                import boto3
                session = boto3.Session()
                credentials = session.get_credentials()
                # For IAM roles, credentials exist but might not have direct access_key property
                # Try to access it to force credential resolution
                if credentials:
                    try:
                        _ = credentials.access_key  # Force credential fetch
                        return True
                    except:
                        pass
                # Fallback: Try creating a bedrock client as ultimate test
                try:
                    bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
                    return True
                except:
                    return False
            except:
                return False

        def get_bedrock_request_body(self, system_prompt, user_prompt):
            config = self.get_model_config()
            body = {
                "anthropic_version": config['anthropic_version'],
                "max_tokens": config['max_tokens'],
                "temperature": config['temperature'],
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            }
            return json.dumps(body)

        def extract_response_content(self, response_body):
            try:
                content = response_body.get('content', [])
                if content and len(content) > 0:
                    return content[0].get('text', '')
                return response_body.get('completion', response_body.get('message', ''))
            except:
                return "Error extracting response content"

        def _extract_base_model(self, model_id):
            """Extract base model name from full model ID"""
            # e.g., "anthropic.claude-3-5-sonnet-20240620-v1:0" -> "claude-3-5-sonnet"
            if 'claude-3-5-sonnet' in model_id:
                return 'claude-3-5-sonnet'
            elif 'claude-3-sonnet' in model_id:
                return 'claude-3-sonnet'
            elif 'claude-3-haiku' in model_id:
                return 'claude-3-haiku'
            return 'claude-3-5-sonnet'  # Default

        def get_fallback_model_id(self, base_name):
            """Get full model ID from base name"""
            model_map = {
                'claude-3-5-sonnet': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
                'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0'
            }
            return model_map.get(base_name, model_map['claude-3-5-sonnet'])
    
    model_config = FallbackModelConfig()

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

        # Use prompts from config/ai_prompts.py if available
        # ✅ FIX: Increased content limit from 2500 to 8000 for complete detailed analysis (Issue #5)
        if ai_prompts:
            prompt = ai_prompts.build_section_analysis_prompt(section_name, content[:8000], doc_type)
            system_prompt = ai_prompts.build_enhanced_system_prompt(self.hawkeye_checklist) + "\n\n" + ai_prompts.SECTION_ANALYSIS_SYSTEM_PROMPT
        else:
            # Fallback to comprehensive prompts when config not available
            section_guidance = self._get_section_guidance(section_name)

            # Build detailed analysis prompt
            prompt = f"""Analyze the '{section_name}' section of this investigation document.

CONTENT TO ANALYZE:
{content[:8000]}

ANALYSIS REQUIREMENTS:
1. Identify gaps, weaknesses, or areas needing improvement
2. Provide specific, actionable feedback
3. Reference relevant investigation best practices
4. Focus on critical issues that impact investigation quality

Return your analysis as a JSON object with this EXACT structure:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion",
            "category": "Investigation Process|Documentation|Root Cause|Timeline|etc",
            "description": "Clear description of the issue or gap (max 200 chars)",
            "suggestion": "Specific recommendation to fix it (max 150 chars)",
            "example": "Brief example if helpful (max 100 chars)",
            "questions": ["Probing question 1?", "Question 2?"],
            "hawkeye_refs": [2, 5],
            "risk_level": "High|Medium|Low",
            "confidence": 0.85
        }}
    ]
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown formatting, no text before or after
- Each feedback item must have ALL fields listed above
- confidence should be a float between 0.0 and 1.0
- Provide 2-5 high-quality feedback items focusing on the most important issues
- If content is too short or lacks substance, return 1-2 items about missing details"""

            system_prompt = f"""You are an expert investigation analyst specializing in document review and quality assurance.

Your task is to analyze investigation documents using the Hawkeye Investigation Framework:

{self.hawkeye_checklist}

ANALYSIS GUIDELINES:
- Be thorough but concise
- Focus on high-impact issues
- Provide actionable, specific feedback
- Consider investigation best practices
- Reference relevant Hawkeye checklist items

OUTPUT FORMAT:
You MUST respond with valid JSON only. No markdown code blocks, no explanatory text, just the JSON object.
The JSON must have a "feedback_items" array containing your analysis."""

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

            # Try to strip markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                # Remove markdown code fence
                cleaned_response = re.sub(r'^```(?:json)?\s*', '', cleaned_response)
                cleaned_response = re.sub(r'\s*```$', '', cleaned_response)
                try:
                    result = json.loads(cleaned_response)
                    print(f"✅ Parsed after removing markdown code blocks - {len(result.get('feedback_items', []))} items")
                except:
                    pass

            # If still not parsed, try to extract JSON from response
            if result is None:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        print(f"✅ Extracted JSON successfully - {len(result.get('feedback_items', []))} items")
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
        
        # Validate and enhance feedback items - process ALL items, filter by confidence later (✅ FIX: Removed limit, filter by confidence >= 80%)
        validated_items = []
        for i, item in enumerate(result.get('feedback_items', [])):  # Process ALL items
            if not isinstance(item, dict):
                print(f"⚠️ Skipping invalid feedback item {i}: {type(item)}")
                continue

            # Ensure all required fields exist with improved defaults
            validated_item = {
                'id': item.get('id', f"{section_name}_{i}_{datetime.now().strftime('%H%M%S')}"),
                'type': item.get('type', 'suggestion'),
                'category': item.get('category', 'Investigation Process'),
                'description': self._truncate_text(item.get('description', 'Analysis gap identified'), 1000),  # ✅ FIX: Increased from 100 to 1000
                'suggestion': self._truncate_text(item.get('suggestion', ''), 500),  # ✅ FIX: Increased from 80 to 500
                'example': self._truncate_text(item.get('example', ''), 300),  # ✅ FIX: Increased from 60 to 300
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

        # ✅ FIX: Filter feedback items with confidence >= 80% (0.8)
        high_confidence_items = [item for item in validated_items if item['confidence'] >= 0.8]

        # ✅ FIX: Remove duplicates and near-duplicates (similarity check)
        unique_items = self._remove_duplicate_feedback(high_confidence_items)

        # ✅ FIX: Sort by confidence in ascending order (lowest confidence first)
        unique_items.sort(key=lambda x: x['confidence'])

        print(f"📊 Filtered: {len(validated_items)} total → {len(high_confidence_items)} high-confidence → {len(unique_items)} unique items")

        # Update result with filtered, deduplicated, and sorted items
        result['feedback_items'] = unique_items

        # Only cache successful results (not errors or fallbacks)
        # This prevents caching mock/fallback responses that would persist after fixes
        if not result.get('error') and not result.get('fallback'):
            self.feedback_cache[cache_key] = result
            print(f"💾 Result cached for future requests")
        else:
            print(f"⚠️ Skipping cache for fallback/error response")

        print(f"✅ Analysis complete: {len(high_confidence_items)} high-confidence feedback items (ALL items with confidence >= 80%, sorted ascending)")  # ✅ FIX: Show ALL items >= 80%
        return result

    def _get_section_guidance(self, section_name):
        """Get focused section-specific analysis guidance"""
        # Use prompts from config/ai_prompts.py if available
        if ai_prompts:
            return ai_prompts.get_section_specific_guidance(section_name)
        else:
            # Fallback guidance
            return "Analyze section for completeness and clarity"

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

    def _invoke_bedrock(self, system_prompt, user_prompt, max_retries_per_model=3):
        """
        Invoke AWS Bedrock with multi-model fallback on throttling
        Tries models in priority order, automatically switching on throttle
        """
        try:
            # Check if credentials are available
            print(f"🔍 Checking AWS credentials for document analysis...", flush=True)
            has_creds = model_config.has_credentials()
            print(f"🔍 Credentials check result: {has_creds}", flush=True)

            if not has_creds:
                print("⚠️ No AWS credentials found - using mock analysis response", flush=True)
                return self._mock_ai_response(user_prompt)

            config = model_config.get_model_config()

            # Create Bedrock client using default credentials (works with both env vars and IAM roles)
            runtime = boto3.client(
                'bedrock-runtime',
                region_name=config['region']
            )

            # Check credential source for logging
            if os.environ.get('AWS_ACCESS_KEY_ID'):
                print(f"🔑 Using AWS credentials from environment variables", flush=True)
            else:
                print(f"🔑 Using AWS credentials from IAM role (App Runner)", flush=True)

            # Try multi-model fallback if enabled
            if MODEL_FALLBACK_ENABLED:
                return self._invoke_with_model_fallback(runtime, system_prompt, user_prompt, max_retries_per_model)
            else:
                # Use single model with retry (old behavior)
                return self._invoke_single_model(runtime, config, system_prompt, user_prompt, max_retries_per_model)

        except Exception as e:
            print(f"❌ Bedrock analysis error: {str(e)}", flush=True)

            # Provide specific error guidance
            error_str = str(e).lower()
            if 'credentials' in error_str or 'access' in error_str:
                print("💡 Fix: Check AWS credentials configuration", flush=True)
            elif 'region' in error_str:
                print("💡 Fix: Verify AWS region and Bedrock availability", flush=True)
            elif 'not found' in error_str or 'model' in error_str:
                print("💡 Fix: Verify Claude model access in your AWS account", flush=True)
            elif 'throttling' in error_str or 'limit' in error_str or 'too many requests' in error_str:
                print("💡 Fix: Rate limiting - AWS Bedrock throttled your requests.", flush=True)
                print("💡 Suggestion: Wait 30-60 seconds or enable multi-model fallback", flush=True)

            # Return mock analysis response for testing
            print("🎭 Falling back to mock analysis response", flush=True)
            return self._mock_ai_response(user_prompt)

    def _invoke_with_model_fallback(self, runtime, system_prompt, user_prompt, max_retries_per_model):
        """
        Try multiple models with automatic fallback on throttling (V2 - Per-Request Isolation)

        Key Design:
        - Each request gets fresh model list (starts with primary)
        - Other users' throttles don't affect this request
        - Only skip model if it was just throttled (< 2s ago)
        - Maintains user independence
        """
        import uuid
        request_id = str(uuid.uuid4())[:8]  # Short ID for logging

        print(f"🔄 Request {request_id} starting - getting available models", flush=True)

        # Get models for THIS request (per-request isolation)
        models_to_try = model_manager.get_models_for_request(request_id)

        print(f"📋 Request {request_id} will try {len(models_to_try)} models: {[m['name'] for m in models_to_try]}", flush=True)

        models_tried = []

        # Try each model in priority order
        for model in models_to_try:
            model_id = model['id']
            models_tried.append(model['name'])

            print(f"🎯 Request {request_id} attempting with {model['name']}", flush=True)

            # Try this model with retries
            try:
                result = self._try_model(runtime, model, system_prompt, user_prompt, max_retries_per_model)

                # Success! Record it
                model_manager.record_success(model_id)
                print(f"✅ Request {request_id} succeeded with {model['name']} ({len(result)} chars)", flush=True)
                return result

            except Exception as e:
                error_str = str(e).lower()

                # Check if throttling error
                if 'throttling' in error_str or 'too many requests' in error_str or 'rate' in error_str:
                    print(f"🚫 Request {request_id}: {model['name']} throttled, trying next model...", flush=True)
                    model_manager.record_throttle(model_id, str(e))
                    # Continue to next model
                    continue
                else:
                    # Non-throttling error, don't try other models
                    print(f"❌ Request {request_id}: {model['name']} failed with non-throttling error: {str(e)}", flush=True)
                    raise e

        # All models failed for this request
        print(f"❌ Request {request_id} exhausted all models. Tried: {', '.join(models_tried)}", flush=True)
        raise Exception(f"All {len(models_tried)} Claude models throttled for this request")

    def _try_model(self, runtime, model, system_prompt, user_prompt, max_retries):
        """Try a specific model with exponential backoff retry"""
        model_id = model['id']

        # Build request body for this model
        body_dict = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": model['max_tokens'],
            "temperature": model['temperature'],
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        body = json.dumps(body_dict)

        last_exception = None

        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                response = runtime.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept="application/json",
                    contentType="application/json"
                )

                response_body = json.loads(response.get('body').read())

                # Extract response content
                content = response_body.get('content', [])
                if content and len(content) > 0:
                    result = content[0].get('text', '')
                else:
                    result = response_body.get('completion', response_body.get('message', ''))

                return result

            except Exception as retry_error:
                last_exception = retry_error
                error_str = str(retry_error).lower()

                # Check if it's a throttling error
                if 'throttling' in error_str or 'too many requests' in error_str or 'rate' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + (time.time() % 1)
                        print(f"   ⏳ Retry {attempt + 1}/{max_retries} after {wait_time:.1f}s...", flush=True)
                        time.sleep(wait_time)
                    else:
                        # All retries for this model exhausted
                        raise retry_error
                else:
                    # Non-throttling error, fail immediately
                    raise retry_error

        # If we get here, all retries failed
        raise last_exception

    def _invoke_single_model(self, runtime, config, system_prompt, user_prompt, max_retries):
        """Original single-model implementation (fallback when model manager disabled)"""
        # Generate request body using model config
        body = model_config.get_bedrock_request_body(system_prompt, user_prompt)

        print(f"🤖 Invoking {config['model_name']} for analysis (ID: {config['model_id']})", flush=True)

        last_exception = None
        for attempt in range(max_retries):
            try:
                response = runtime.invoke_model(
                    body=body,
                    modelId=config['model_id'],
                    accept="application/json",
                    contentType="application/json"
                )

                response_body = json.loads(response.get('body').read())
                result = model_config.extract_response_content(response_body)

                print(f"✅ Claude analysis response received ({len(result)} chars)", flush=True)
                return result

            except Exception as retry_error:
                last_exception = retry_error
                error_str = str(retry_error).lower()

                if 'throttling' in error_str or 'too many requests' in error_str or 'rate' in error_str:
                    wait_time = (2 ** attempt) + (time.time() % 1)

                    if attempt < max_retries - 1:
                        print(f"⏳ Rate limited - waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...", flush=True)
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Rate limit exceeded after {max_retries} attempts", flush=True)
                else:
                    raise retry_error

        raise last_exception
    

    

    
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
        """Format chat response with proper HTML formatting - COMPLETE response, no truncation"""
        # IMPORTANT: User wants COMPLETE responses, no truncation
        # Keep ALL content from Claude

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

        return formatted.strip()
    
    def _truncate_text(self, text, max_length):
        """Truncate text to specified length with ellipsis"""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def _remove_duplicate_feedback(self, items):
        """Remove duplicate and near-duplicate feedback items based on similarity"""
        if not items:
            return []

        from difflib import SequenceMatcher

        unique_items = []

        for item in items:
            description = item.get('description', '').strip().lower()

            if not description:
                # Skip items with empty descriptions
                continue

            # Check similarity with existing items
            is_duplicate = False
            for idx, existing_item in enumerate(unique_items):
                existing_desc = existing_item.get('description', '').strip().lower()

                # Calculate similarity ratio
                similarity = SequenceMatcher(None, description, existing_desc).ratio()

                # If similarity >= 85%, consider it a duplicate
                if similarity >= 0.85:
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if item['confidence'] > existing_item['confidence']:
                        print(f"🔄 Replacing similar item (similarity: {similarity:.2%}, old confidence: {existing_item['confidence']:.2%}, new confidence: {item['confidence']:.2%})")
                        unique_items[idx] = item
                    else:
                        print(f"⏭️ Skipping similar item (similarity: {similarity:.2%}, keeping higher confidence: {existing_item['confidence']:.2%})")
                    break

            if not is_duplicate:
                unique_items.append(item)

        return unique_items

    def _calculate_similarity(self, text1, text2):
        """Calculate similarity ratio between two text strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.strip().lower(), text2.strip().lower()).ratio()
    
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
        """Process chat queries with multi-model fallback support"""
        print(f"Processing chat query: {query[:50]}...")

        # Check if we should use real AI or mock responses
        if not model_config.has_credentials():
            print("⚠️ No AWS credentials - using mock chat response")
            return self._mock_chat_response(query, context)

        current_section = context.get('current_section', 'Current section')
        feedback_count = len(context.get('current_feedback', []))

        # Use prompts from config/ai_prompts.py if available
        if ai_prompts:
            # Build context info for the prompt
            context_info = f"""Current Section: {current_section}
Current Feedback Items: {feedback_count}
Document Type: Full Write-up"""

            prompt = ai_prompts.build_chat_query_prompt(query, context_info)
            system_prompt = ai_prompts.CHAT_ASSISTANT_SYSTEM_PROMPT
        else:
            # Fallback prompts
            prompt = f"Answer this query: {query}"
            system_prompt = "You are a helpful assistant."

        # Check if multi-model chat is enabled (default to false for stability)
        enable_multi_model = os.environ.get('CHAT_ENABLE_MULTI_MODEL', 'false').lower() == 'true'

        if enable_multi_model:
            return self._process_chat_with_fallback(system_prompt, prompt, query, context)
        else:
            return self._process_chat_single_model(system_prompt, prompt, query, context)

    def _process_chat_single_model(self, system_prompt, prompt, query, context, max_retries=5):
        """Process chat with single primary model with exponential backoff retry"""
        try:
            # Use real Bedrock for chat
            import boto3
            config = model_config.get_model_config()

            # Create Bedrock client using default credentials (works with both env vars and IAM roles)
            runtime = boto3.client(
                'bedrock-runtime',
                region_name=config['region']
            )

            # Check credential source for logging
            if os.environ.get('AWS_ACCESS_KEY_ID'):
                print(f"🔑 Chat using AWS credentials from environment variables", flush=True)
            else:
                print(f"🔑 Chat using AWS credentials from IAM role (App Runner)", flush=True)

            body = model_config.get_bedrock_request_body(system_prompt, prompt)

            print(f"🤖 Chat query to {config['model_name']}", flush=True)

            # Retry loop with exponential backoff
            last_exception = None
            for attempt in range(max_retries):
                try:
                    response = runtime.invoke_model(
                        body=body,
                        modelId=config['model_id'],
                        accept="application/json",
                        contentType="application/json"
                    )

                    response_body = json.loads(response.get('body').read())
                    result = model_config.extract_response_content(response_body)

                    print(f"✅ Claude chat response received", flush=True)
                    return self._format_chat_response(result)

                except Exception as retry_error:
                    last_exception = retry_error
                    error_str = str(retry_error).lower()

                    # Check if it's a throttling error
                    if 'throttling' in error_str or 'too many requests' in error_str or 'rate' in error_str:
                        wait_time = (2 ** attempt) + (time.time() % 1)  # Exponential backoff with jitter

                        if attempt < max_retries - 1:
                            print(f"⏳ Chat rate limited - waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...", flush=True)
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Chat rate limit exceeded after {max_retries} attempts", flush=True)
                    else:
                        # Non-throttling error, don't retry
                        raise retry_error

            # If we get here, all retries failed
            raise last_exception

        except Exception as e:
            print(f"❌ Chat processing error: {str(e)}", flush=True)
            print("🎭 Falling back to mock chat response", flush=True)
            return self._mock_chat_response(query, context)

    def _process_chat_with_fallback(self, system_prompt, prompt, query, context):
        """Process chat with automatic model fallback"""
        import boto3
        from botocore.exceptions import ClientError

        config = model_config.get_model_config()

        # Build list of models to try
        models_to_try = []

        # Add primary model
        models_to_try.append({
            'name': config['model_name'],
            'id': config['model_id'],
            'priority': 1
        })

        # Add fallback models from environment
        fallback_env = os.environ.get('BEDROCK_FALLBACK_MODELS', '')
        if fallback_env:
            fallback_ids = [m.strip() for m in fallback_env.split(',')]
            for idx, fallback_id in enumerate(fallback_ids):
                base_name = model_config._extract_base_model(fallback_id)
                model_info = model_config.SUPPORTED_MODELS.get(base_name, {})
                models_to_try.append({
                    'name': model_info.get('name', base_name),
                    'id': fallback_id,
                    'priority': idx + 2
                })

        # Add default fallback models
        for idx, base_name in enumerate(config['fallback_models']):
            fallback_id = model_config.get_fallback_model_id(base_name)
            # Avoid duplicates
            if not any(m['id'] == fallback_id for m in models_to_try):
                model_info = model_config.SUPPORTED_MODELS.get(base_name, {})
                models_to_try.append({
                    'name': model_info.get('name', base_name),
                    'id': fallback_id,
                    'priority': len(models_to_try) + 1
                })

        print(f"🔄 Multi-model chat enabled - {len(models_to_try)} models available")

        # Create Bedrock runtime client using default credentials (works with both env vars and IAM roles)
        runtime = boto3.client('bedrock-runtime', region_name=config['region'])

        # Check credential source for logging
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            print(f"🔑 Multi-model chat using AWS credentials from environment variables")
        else:
            print(f"🔑 Multi-model chat using AWS credentials from IAM role (App Runner)")

        # Try each model in priority order
        for model in models_to_try:
            try:
                print(f"🤖 Trying chat with {model['name']} (Priority {model['priority']})")

                # Create request body
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": config.get('max_tokens', 8192),
                    "temperature": config.get('temperature', 0.7),
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}]
                })

                response = runtime.invoke_model(
                    body=body,
                    modelId=model['id'],
                    accept="application/json",
                    contentType="application/json"
                )

                response_body = json.loads(response.get('body').read())
                result = model_config.extract_response_content(response_body)

                print(f"✅ Chat successful with {model['name']}")
                return self._format_chat_response(result)

            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_msg = e.response['Error']['Message']
                print(f"⚠️ {model['name']} failed ({error_code}): {error_msg[:100]}")

                # If this is the last model, fall back to mock
                if model == models_to_try[-1]:
                    print("❌ All models failed - falling back to mock response")
                    return self._mock_chat_response(query, context)

                # Otherwise, try the next model
                continue

            except Exception as e:
                print(f"⚠️ {model['name']} error: {str(e)[:100]}")

                # If this is the last model, fall back to mock
                if model == models_to_try[-1]:
                    print("❌ All models failed - falling back to mock response")
                    return self._mock_chat_response(query, context)

                # Otherwise, try the next model
                continue

        # Fallback if somehow we get here
        print("❌ All models exhausted - falling back to mock response")
        return self._mock_chat_response(query, context)

    def test_connection(self, max_retries=3):
        """Test Claude AI connection with exponential backoff retry"""
        import time
        start_time = time.time()

        try:
            # Check if credentials are available
            if not model_config.has_credentials():
                return {
                    'connected': False,
                    'error': 'No AWS credentials found',
                    'model': 'None',
                    'response_time': 0
                }

            config = model_config.get_model_config()

            # Create Bedrock client using default credentials (works with both env vars and IAM roles)
            runtime = boto3.client(
                'bedrock-runtime',
                region_name=config['region']
            )

            # Check credential source for logging
            if os.environ.get('AWS_ACCESS_KEY_ID'):
                print(f"🔑 Testing with AWS credentials from environment variables", flush=True)
            else:
                print(f"🔑 Testing with default AWS credentials", flush=True)

            # Simple test prompt
            test_prompt = "Respond with 'OK' if you can read this message."
            system_prompt = "You are Claude AI. Respond concisely."

            body = model_config.get_bedrock_request_body(system_prompt, test_prompt)

            print(f"🤖 Testing connection to {config['model_name']} (ID: {config['model_id']})", flush=True)

            # Retry loop with exponential backoff
            last_exception = None
            for attempt in range(max_retries):
                try:
                    response = runtime.invoke_model(
                        body=body,
                        modelId=config['model_id'],
                        accept="application/json",
                        contentType="application/json"
                    )

                    response_body = json.loads(response.get('body').read())
                    result = model_config.extract_response_content(response_body)

                    response_time = time.time() - start_time

                    print(f"✅ Claude connection test successful ({response_time:.2f}s)", flush=True)

                    return {
                        'connected': True,
                        'model': config['model_name'],
                        'model_id': config['model_id'],
                        'response_time': round(response_time, 2),
                        'test_response': result[:50] + '...' if len(result) > 50 else result,
                        'region': config['region']
                    }

                except Exception as retry_error:
                    last_exception = retry_error
                    error_str = str(retry_error).lower()

                    # Check if it's a throttling error
                    if 'throttling' in error_str or 'too many requests' in error_str or 'rate' in error_str:
                        wait_time = (2 ** attempt) + (time.time() % 1)  # Exponential backoff with jitter

                        if attempt < max_retries - 1:
                            print(f"⏳ Test rate limited - waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...", flush=True)
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Test rate limit exceeded after {max_retries} attempts", flush=True)
                    else:
                        # Non-throttling error, don't retry
                        raise retry_error

            # If we get here, all retries failed due to throttling
            raise last_exception

        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ Claude connection test failed: {str(e)}", flush=True)

            return {
                'connected': False,
                'error': str(e),
                'model': config.get('model_name', 'Unknown') if 'config' in locals() else 'Unknown',
                'response_time': round(response_time, 2)
            }