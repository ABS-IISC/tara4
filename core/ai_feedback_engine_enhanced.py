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
        """Analyze section with enhanced comprehensive Hawkeye framework"""
        cache_key = f"{section_name}_{hash(content)}"
        if cache_key in self.feedback_cache:
            return self.feedback_cache[cache_key]

        # Get enhanced section-specific guidance
        section_guidance = self._get_enhanced_section_guidance(section_name)
        
        prompt = f"""COMPREHENSIVE DOCUMENT ANALYSIS TASK:
Conduct detailed analysis of section "{section_name}" from a CT EE investigation writeup using enhanced Hawkeye framework standards.

{section_guidance}

SECTION CONTENT:
{content[:3000]}

COMPREHENSIVE ANALYSIS FRAMEWORK:

1. PRECISION ANALYSIS:
   - Identify specific missing information that impacts investigation validity
   - Assess accuracy and verifiability of all claims and statements
   - Evaluate completeness against professional investigation standards
   - Check for vague language that should be quantified or specified

2. EVIDENCE VALIDATION:
   - Verify that all claims are supported by appropriate evidence
   - Identify assertions that lack supporting documentation
   - Assess whether evidence sources are credible and independent
   - Check for gaps in evidence chain or validation methodology

3. ACCOUNTABILITY ASSESSMENT:
   - Ensure clear ownership and responsibility for all actions and decisions
   - Verify that decision authority is properly documented
   - Check for gaps in approval chains or escalation procedures
   - Assess whether roles and responsibilities are clearly defined

4. IMPACT QUANTIFICATION:
   - Evaluate whether impacts are properly quantified with specific metrics
   - Check for customer, business, and operational impact assessment
   - Verify that financial implications are documented where relevant
   - Assess whether regulatory or compliance impacts are addressed

5. PROCESS RIGOR:
   - Assess whether proper investigation methodology was followed
   - Check for systematic analysis approach (5-whys, fishbone, etc.)
   - Verify that alternative scenarios were considered
   - Evaluate whether cross-validation was performed

6. COMMUNICATION EFFECTIVENESS:
   - Assess clarity and accessibility for intended audiences
   - Check for appropriate level of technical detail
   - Verify that key information is prominently presented
   - Evaluate whether visual aids or structure improvements are needed

CRITICAL FOCUS AREAS:
- Timeline precision and verification gaps
- Root cause analysis depth and systemic thinking
- Preventative action specificity and measurability
- Evidence quality and independent validation
- Stakeholder impact assessment and quantification
- Accountability and ownership clarity
- Compliance with investigation standards and best practices

Return detailed, actionable feedback in JSON format with enhanced specificity:
{{
    "feedback_items": [
        {{
            "id": "unique_id",
            "type": "critical|important|suggestion",
            "category": "specific Hawkeye investigation area",
            "description": "Precise, detailed gap or issue with specific examples from content",
            "suggestion": "Concrete, actionable steps to address the gap with implementation details",
            "example": "Specific example of how to improve the content",
            "questions": ["Targeted questions that must be answered to address the gap"],
            "hawkeye_refs": [relevant_checkpoint_numbers],
            "risk_level": "High|Medium|Low",
            "confidence": 0.95
        }}
    ]
}}

Ensure each feedback item is:
- SPECIFIC: References exact content issues, not generic observations
- ACTIONABLE: Provides clear steps for improvement
- MEASURABLE: Includes criteria for success where applicable
- EVIDENCE-BASED: Supported by analysis of actual content
- RISK-APPROPRIATE: Classified based on impact to investigation quality"""

        system_prompt = f"""You are a senior CT EE investigation specialist with expertise in comprehensive document analysis and quality assurance. Your role is to conduct rigorous, detailed analysis that ensures investigation documents meet the highest professional standards.

{self.hawkeye_checklist}

EXPERTISE AREAS:
- Investigation methodology and evidence validation
- Root cause analysis and systemic thinking
- Risk assessment and impact quantification
- Stakeholder communication and documentation standards
- Compliance with regulatory and audit requirements
- Process improvement and preventative action design

ANALYSIS STANDARDS:
- PRECISION: Identify specific, concrete gaps rather than general observations
- EVIDENCE-BASED: Ground all feedback in actual content analysis
- ACTIONABLE: Provide clear, implementable recommendations
- RISK-FOCUSED: Prioritize issues that impact investigation validity
- COMPREHENSIVE: Consider all aspects of investigation quality
- PROFESSIONAL: Maintain high standards for business documentation

FEEDBACK QUALITY REQUIREMENTS:
- Each item must reference specific content issues with examples
- Suggestions must be concrete and implementable
- Risk levels must reflect actual impact on investigation quality
- Questions must be targeted and answerable
- Hawkeye references must be relevant and accurate

FOCUS ON HIGH-IMPACT ISSUES:
- Missing critical information that affects conclusions
- Insufficient evidence validation or verification
- Gaps in accountability, ownership, or decision authority
- Inadequate quantification of impacts or metrics
- Weak root cause analysis or preventative actions
- Timeline inaccuracies or unexplained gaps
- Compliance issues with investigation standards

Provide feedback that transforms good documents into excellent ones by addressing substantive quality gaps, not cosmetic issues."""

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
            # Use enhanced mock response instead of returning error
            response = self._enhanced_mock_ai_response(prompt)
        
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
                validated_item['risk_level'] = self._enhanced_classify_risk_level(validated_item)
            
            validated_items.append(validated_item)
        
        # Update result with validated items
        result['feedback_items'] = validated_items
        
        # Cache the result
        self.feedback_cache[cache_key] = result
        
        print(f"✅ Enhanced analysis complete: {len(validated_items)} validated feedback items")
        return result

    def _get_enhanced_section_guidance(self, section_name):
        """Get enhanced section-specific analysis guidance based on comprehensive investigation standards"""
        section_lower = section_name.lower()
        
        if "timeline" in section_lower:
            return """
            TIMELINE ANALYSIS - COMPREHENSIVE REQUIREMENTS:
            
            CRITICAL ELEMENTS:
            - PRECISION: All timestamps must be exact (DD-MMM-YYYY HH:MM format) with timezone specification
            - VERIFICATION: Each timestamp independently verified through system logs, emails, or witness accounts
            - SEQUENCE VALIDATION: Chronological order verified with no logical inconsistencies
            - GAP ANALYSIS: Any time gap >2 hours requires explicit explanation and justification
            - EVENT CATEGORIZATION: Distinguish between detection, escalation, investigation, and resolution events
            
            INVESTIGATION DEPTH:
            - FIRST DETECTION: Who first identified the issue? What triggered the detection?
            - ESCALATION PATH: Document each escalation step with decision rationale
            - DECISION POINTS: Identify key decision moments and alternative paths considered
            - PARALLEL ACTIVITIES: Account for simultaneous actions by different teams
            - EXTERNAL DEPENDENCIES: Note any external factors affecting timeline
            
            ACCOUNTABILITY FRAMEWORK:
            - OWNERSHIP: Each event must have identified DRI (Directly Responsible Individual)
            - DECISION AUTHORITY: Clarify who had authority to make each decision
            - COMMUNICATION: Document how information flowed between stakeholders
            - APPROVAL CHAINS: Identify required approvals and actual approval timeline
            
            QUALITY VALIDATION:
            - CROSS-REFERENCE: Verify timeline against multiple independent sources
            - STAKEHOLDER CONFIRMATION: Key participants should validate their involvement
            - SYSTEM CORRELATION: Align with system logs, monitoring alerts, and automated actions
            - IMPACT CORRELATION: Link timeline events to customer impact and business metrics
            """
        elif "resolving action" in section_lower:
            return """
            RESOLVING ACTIONS - COMPREHENSIVE ANALYSIS:
            
            ACTION COMPLETENESS:
            - IMMEDIATE RESPONSE: Document all actions taken within first 4 hours
            - SHORT-TERM FIXES: Temporary solutions implemented to stop immediate harm
            - LONG-TERM SOLUTIONS: Permanent fixes addressing root causes
            - VALIDATION STEPS: How was effectiveness of each action verified?
            - ROLLBACK PLANS: What contingency plans existed if actions failed?
            
            STAKEHOLDER IMPACT:
            - CUSTOMER COMMUNICATION: How were affected customers notified and updated?
            - INTERNAL COORDINATION: Which teams were involved and how were they coordinated?
            - EXTERNAL PARTNERS: Were suppliers, vendors, or partners affected or involved?
            - REGULATORY NOTIFICATION: Were any regulatory bodies informed as required?
            
            EFFECTIVENESS MEASUREMENT:
            - SUCCESS METRICS: Specific KPIs used to measure resolution effectiveness
            - MONITORING SETUP: Ongoing monitoring established to prevent recurrence
            - FEEDBACK LOOPS: Mechanisms to capture stakeholder feedback on resolution
            - PERFORMANCE VALIDATION: How was restored service performance verified?
            
            DOCUMENTATION REQUIREMENTS:
            - DECISION RATIONALE: Why was each specific action chosen over alternatives?
            - RESOURCE ALLOCATION: Personnel, time, and budget resources utilized
            - APPROVAL DOCUMENTATION: Required approvals obtained and documented
            - COMPLETION VERIFICATION: Independent verification of action completion
            """
        elif "root cause" in section_lower or "preventative action" in section_lower:
            return """
            ROOT CAUSE & PREVENTATIVE ACTIONS - DEEP ANALYSIS:
            
            ROOT CAUSE METHODOLOGY:
            - 5 WHYS IMPLEMENTATION: Each "why" must be supported by evidence and lead to deeper understanding
            - FISHBONE ANALYSIS: Consider People, Process, Technology, Environment, and Management factors
            - SYSTEMIC vs SYMPTOMATIC: Clearly distinguish between immediate triggers and underlying causes
            - CONTRIBUTING FACTORS: Identify all factors that enabled or amplified the issue
            - FAILURE MODE ANALYSIS: Understand how normal processes failed or were bypassed
            
            PROCESS GAP IDENTIFICATION:
            - CONTROL FAILURES: Which existing controls failed and why?
            - DETECTION GAPS: Why wasn't the issue detected earlier by existing monitoring?
            - ESCALATION FAILURES: Were escalation procedures followed? If not, why?
            - COMMUNICATION BREAKDOWNS: Where did information flow break down?
            - TRAINING DEFICIENCIES: Were skill or knowledge gaps contributing factors?
            
            PREVENTATIVE ACTION FRAMEWORK:
            - SPECIFICITY: Each action must be concrete, measurable, and time-bound
            - OWNERSHIP: Clear DRI assigned with explicit accountability measures
            - EFFECTIVENESS METRICS: How will success be measured and monitored?
            - IMPLEMENTATION TIMELINE: Realistic dates with milestone checkpoints
            - RESOURCE REQUIREMENTS: Personnel, budget, and technology needs identified
            
            SYSTEMIC IMPROVEMENTS:
            - PROCESS REDESIGN: How will processes be modified to prevent recurrence?
            - CONTROL ENHANCEMENTS: New controls or monitoring to be implemented
            - TRAINING PROGRAMS: Skill development to address knowledge gaps
            - TECHNOLOGY SOLUTIONS: System improvements or new tools required
            - ORGANIZATIONAL CHANGES: Structural changes to improve accountability
            
            VALIDATION REQUIREMENTS:
            - PILOT TESTING: How will preventative actions be tested before full implementation?
            - SUCCESS CRITERIA: Specific metrics to validate effectiveness
            - MONITORING PLAN: Ongoing monitoring to ensure sustained improvement
            - REVIEW SCHEDULE: Regular reviews to assess continued effectiveness
            """
        elif "executive summary" in section_lower or "summary" in section_lower:
            return """
            EXECUTIVE SUMMARY - COMPREHENSIVE REQUIREMENTS:
            
            IMPACT QUANTIFICATION:
            - CUSTOMER IMPACT: Number of customers affected, duration of impact, severity levels
            - BUSINESS IMPACT: Revenue impact, operational disruption, reputation considerations
            - FINANCIAL IMPACT: Direct costs, opportunity costs, recovery expenses
            - REGULATORY IMPACT: Compliance implications, potential penalties, reporting requirements
            
            CRITICAL FINDINGS:
            - PRIMARY ROOT CAUSE: Single, clear statement of the fundamental cause
            - CONTRIBUTING FACTORS: 2-3 key factors that enabled or amplified the issue
            - SYSTEMIC ISSUES: Broader organizational or process issues identified
            - IMMEDIATE TRIGGERS: Specific events that precipitated the incident
            
            RESPONSE EFFECTIVENESS:
            - DETECTION TIME: How quickly was the issue identified?
            - RESPONSE TIME: Time from detection to initial response
            - RESOLUTION TIME: Total time to full resolution
            - COMMUNICATION EFFECTIVENESS: How well were stakeholders informed?
            
            FORWARD-LOOKING ELEMENTS:
            - PREVENTION STRATEGY: High-level approach to preventing recurrence
            - ORGANIZATIONAL LEARNING: Key lessons learned and how they'll be applied
            - PROCESS IMPROVEMENTS: Major process changes being implemented
            - MONITORING ENHANCEMENTS: New monitoring or controls being established
            
            ACCOUNTABILITY FRAMEWORK:
            - INCIDENT OWNERSHIP: Who was responsible for the incident response?
            - IMPROVEMENT OWNERSHIP: Who is accountable for implementing preventative actions?
            - EXECUTIVE SPONSORSHIP: Senior leadership commitment to improvements
            - REVIEW SCHEDULE: When and how progress will be reviewed
            """
        elif "background" in section_lower:
            return """
            BACKGROUND SECTION - COMPREHENSIVE CONTEXT:
            
            HISTORICAL CONTEXT:
            - SERVICE HISTORY: How long has this service/process been operational?
            - PREVIOUS INCIDENTS: Any related incidents or issues in the past?
            - EVOLUTION: How has the service/process changed over time?
            - LESSONS LEARNED: Previous improvements or changes made
            
            OPERATIONAL CONTEXT:
            - BUSINESS CRITICALITY: How critical is this service to business operations?
            - CUSTOMER DEPENDENCY: How many customers rely on this service?
            - INTEGRATION POINTS: What other services or systems are connected?
            - PEAK USAGE PATTERNS: When is the service most heavily utilized?
            
            TECHNICAL CONTEXT:
            - ARCHITECTURE: High-level system architecture and key components
            - DEPENDENCIES: Critical dependencies on other systems or services
            - MONITORING: Existing monitoring and alerting capabilities
            - MAINTENANCE: Regular maintenance schedules and procedures
            
            ORGANIZATIONAL CONTEXT:
            - TEAM STRUCTURE: Which teams are responsible for different aspects?
            - ESCALATION PROCEDURES: Standard escalation paths and procedures
            - DECISION AUTHORITY: Who has authority to make different types of decisions?
            - COMMUNICATION PROTOCOLS: Standard communication procedures during incidents
            
            REGULATORY CONTEXT:
            - COMPLIANCE REQUIREMENTS: Relevant regulatory or compliance obligations
            - REPORTING OBLIGATIONS: Required reporting to regulators or stakeholders
            - AUDIT CONSIDERATIONS: How this incident might affect audit findings
            - POLICY ALIGNMENT: Alignment with internal policies and procedures
            """
        else:
            return """
            GENERAL SECTION ANALYSIS - COMPREHENSIVE FRAMEWORK:
            
            CONTENT COMPLETENESS:
            - INFORMATION SUFFICIENCY: Is all necessary information present and detailed?
            - EVIDENCE QUALITY: Are claims supported by appropriate evidence?
            - STAKEHOLDER PERSPECTIVES: Are all relevant viewpoints represented?
            - CONTEXT ADEQUACY: Is sufficient context provided for understanding?
            
            ANALYTICAL RIGOR:
            - METHODOLOGY: Is the analytical approach sound and appropriate?
            - OBJECTIVITY: Is the analysis objective and free from bias?
            - VALIDATION: Are findings independently validated where possible?
            - ALTERNATIVE SCENARIOS: Are alternative explanations considered?
            
            COMMUNICATION EFFECTIVENESS:
            - CLARITY: Is the content clear and easily understood?
            - STRUCTURE: Is information logically organized and presented?
            - AUDIENCE APPROPRIATENESS: Is content appropriate for intended audience?
            - ACTION ORIENTATION: Are clear next steps and recommendations provided?
            
            COMPLIANCE ALIGNMENT:
            - POLICY ADHERENCE: Does content align with relevant policies?
            - STANDARD COMPLIANCE: Are industry standards and best practices followed?
            - REGULATORY REQUIREMENTS: Are regulatory obligations addressed?
            - AUDIT READINESS: Is documentation sufficient for audit purposes?
            
            QUALITY ASSURANCE:
            - ACCURACY: Are facts, figures, and statements accurate?
            - CONSISTENCY: Is information consistent throughout the document?
            - COMPLETENESS: Are all required elements present?
            - PROFESSIONAL STANDARDS: Does content meet professional documentation standards?
            """

    def _enhanced_mock_ai_response(self, user_prompt):
        """Enhanced mock AI response with detailed, precise feedback based on comprehensive analysis standards"""
        # Simulate processing delay
        time.sleep(2)
        
        # Generate contextual mock responses based on prompt content
        prompt_lower = user_prompt.lower()
        
        if "timeline" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"timeline_precision_{int(time.time())}",
                        "type": "critical",
                        "category": "Timeline Documentation",
                        "description": "Timeline entries lack precision and independent verification. Timestamps are inconsistent (mixing formats like 'morning' vs '14:30') and several critical events show unexplained gaps >4 hours without justification.",
                        "suggestion": "Standardize all timestamps to DD-MMM-YYYY HH:MM format with timezone. Verify each timestamp through system logs, email records, or witness statements. Explain any gaps >2 hours with specific rationale.",
                        "example": "Replace '19-Oct-2011 morning' with '19-Oct-2011 09:15 EST - Initial customer complaint received (verified via CRM ticket #12345)'",
                        "questions": [
                            "Can each timestamp be independently verified through system logs or documentation?",
                            "What specific events occurred during the 6-hour gap between detection and escalation?",
                            "Who had decision authority at each critical timeline point?",
                            "Were parallel activities happening that should be documented?"
                        ],
                        "hawkeye_refs": [2, 13, 15],
                        "risk_level": "High",
                        "confidence": 0.94
                    },
                    {
                        "id": f"timeline_accountability_{int(time.time())}",
                        "type": "important",
                        "category": "Investigation Process",
                        "description": "Timeline lacks clear accountability and decision authority documentation. Multiple events show actions taken without identifying who made decisions or had authority to act.",
                        "suggestion": "For each timeline entry, specify: (1) DRI (Directly Responsible Individual), (2) Decision authority level, (3) Communication method used, (4) Approval chain if required.",
                        "example": "'14:30 - Service degradation detected by monitoring (DRI: John Smith, L5 SDE). Escalated to on-call manager per SOP-123 (Authority: Sarah Johnson, L6 Manager). Approval for emergency fix obtained via Slack #incident-response.'",
                        "questions": [
                            "Who had authority to make each critical decision?",
                            "Were proper approval chains followed for emergency actions?",
                            "How was information communicated between stakeholders?"
                        ],
                        "hawkeye_refs": [2, 14, 17],
                        "risk_level": "Medium",
                        "confidence": 0.89
                    }
                ]
            })
        elif "root cause" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"rootcause_depth_{int(time.time())}",
                        "type": "critical",
                        "category": "Root Cause Analysis",
                        "description": "Root cause analysis stops at symptomatic level without reaching true systemic causes. Current analysis identifies 'human error' as root cause but fails to examine why the error was possible, what controls failed, and what organizational factors enabled it.",
                        "suggestion": "Apply rigorous 5-whys methodology with evidence for each level. Use fishbone analysis to examine People, Process, Technology, Environment, and Management factors. Distinguish between immediate triggers, contributing factors, and systemic root causes.",
                        "example": "Instead of 'RC: Human error in configuration', use: 'RC1: Configuration change deployed without peer review (Why: Review process bypassed due to time pressure. Why: No escalation process for urgent changes. Why: Change management policy unclear on emergency procedures. Why: Policy last updated 3 years ago without operational input.)'",
                        "questions": [
                            "What organizational or process factors made this human error possible?",
                            "Which existing controls failed and why weren't they effective?",
                            "What would have prevented this error even if the same conditions existed?",
                            "Are there similar vulnerabilities in other processes?"
                        ],
                        "hawkeye_refs": [11, 12, 15],
                        "risk_level": "High",
                        "confidence": 0.96
                    },
                    {
                        "id": f"preventative_specificity_{int(time.time())}",
                        "type": "critical",
                        "category": "Preventative Actions",
                        "description": "Preventative actions are vague and unmeasurable. Items like 'improve training' and 'enhance monitoring' lack specific implementation details, success metrics, timelines, and accountability measures.",
                        "suggestion": "Each preventative action must include: (1) Specific implementation steps, (2) Measurable success criteria, (3) DRI with contact info, (4) Completion date with milestones, (5) Budget/resource requirements, (6) Validation method.",
                        "example": "PA1: Implement mandatory peer review for all production configuration changes. Implementation: Update change management system to require 2-person approval for prod changes by 15-Mar-2024. Success metric: 100% of prod changes have documented peer review. DRI: Alex Chen (alex@company.com). Validation: Monthly audit of change logs.",
                        "questions": [
                            "How will you measure whether each preventative action is successful?",
                            "What specific resources (people, budget, tools) are needed for implementation?",
                            "How will you validate that preventative actions remain effective over time?",
                            "What happens if preventative actions don't achieve desired results?"
                        ],
                        "hawkeye_refs": [12, 16, 18],
                        "risk_level": "High",
                        "confidence": 0.93
                    }
                ]
            })
        elif "executive summary" in prompt_lower or "summary" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"summary_impact_{int(time.time())}",
                        "type": "critical",
                        "category": "Impact Assessment",
                        "description": "Executive summary lacks quantified impact metrics. Statements like 'some customers affected' and 'business impact occurred' provide no actionable information for executives to understand severity or make resource allocation decisions.",
                        "suggestion": "Quantify all impacts with specific metrics: number of customers affected, duration of impact, revenue impact, operational disruption metrics, and reputation/regulatory implications. Include both immediate and potential long-term impacts.",
                        "example": "Customer Impact: 15,847 customers experienced service degradation for avg 3.2 hours. Business Impact: Est. $127K revenue loss, 23% increase in support tickets. Regulatory: Potential SLA breach affecting 3 enterprise contracts worth $2.1M annually.",
                        "questions": [
                            "How many customers were affected and for how long?",
                            "What is the estimated financial impact including opportunity costs?",
                            "Are there regulatory or compliance implications?",
                            "What are the potential long-term reputation impacts?"
                        ],
                        "hawkeye_refs": [1, 8, 19],
                        "risk_level": "High",
                        "confidence": 0.91
                    },
                    {
                        "id": f"summary_accountability_{int(time.time())}",
                        "type": "important",
                        "category": "Accountability Framework",
                        "description": "Executive summary lacks clear accountability structure for both incident response and ongoing improvements. No clear ownership or executive sponsorship identified for preventative actions.",
                        "suggestion": "Specify: (1) Incident response owner and their performance, (2) DRI for each major preventative action, (3) Executive sponsor for improvement program, (4) Review schedule with specific dates and participants.",
                        "example": "Incident Owner: Sarah Johnson (performed well, followed escalation procedures). Improvement DRI: Mike Chen (Infrastructure). Executive Sponsor: VP Engineering. Next Review: 30-day progress review scheduled for 15-Apr-2024 with CTO.",
                        "questions": [
                            "Who is accountable for ensuring preventative actions are completed?",
                            "What executive sponsorship exists for the improvement program?",
                            "How will progress be tracked and reviewed?"
                        ],
                        "hawkeye_refs": [14, 16, 18],
                        "risk_level": "Medium",
                        "confidence": 0.87
                    }
                ]
            })
        elif "resolving action" in prompt_lower:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"resolving_validation_{int(time.time())}",
                        "type": "critical",
                        "category": "Resolution Validation",
                        "description": "Resolving actions lack validation methodology and effectiveness measurement. Actions are listed as 'completed' without evidence of actual resolution or verification that customer impact was eliminated.",
                        "suggestion": "For each resolving action, document: (1) Validation method used, (2) Success metrics achieved, (3) Independent verification performed, (4) Customer impact confirmation, (5) Monitoring established to prevent recurrence.",
                        "example": "Action 3: Database connection pool increased from 50 to 200. Validation: Connection timeout errors reduced from 150/hour to 0/hour over 48-hour monitoring period. Customer verification: Support ticket volume returned to baseline. Monitoring: Added CloudWatch alarm for connection pool utilization >80%.",
                        "questions": [
                            "How was the effectiveness of each action independently verified?",
                            "What specific metrics confirm that customer impact was eliminated?",
                            "What monitoring is in place to detect if the issue recurs?",
                            "Were any actions ineffective and require additional measures?"
                        ],
                        "hawkeye_refs": [2, 15, 18],
                        "risk_level": "High",
                        "confidence": 0.92
                    }
                ]
            })
        else:
            return json.dumps({
                "feedback_items": [
                    {
                        "id": f"analysis_depth_{int(time.time())}",
                        "type": "important",
                        "category": "Investigation Rigor",
                        "description": "Analysis lacks sufficient depth and evidence validation for investigation standards. Claims are made without supporting evidence, alternative scenarios aren't considered, and stakeholder perspectives are missing.",
                        "suggestion": "Strengthen analysis by: (1) Providing evidence for all claims, (2) Considering alternative explanations, (3) Including multiple stakeholder perspectives, (4) Cross-referencing findings with independent sources, (5) Documenting analytical methodology used.",
                        "example": "Instead of 'System performance was degraded', use: 'System response time increased from baseline 200ms to 2.3s (verified via APM logs). Customer impact confirmed by 347% increase in timeout-related support tickets. Alternative causes (network issues, database problems) ruled out through systematic elimination.'",
                        "questions": [
                            "What evidence supports each key finding or conclusion?",
                            "Have alternative explanations been considered and ruled out?",
                            "Are multiple stakeholder perspectives represented?",
                            "How was the analytical methodology validated?"
                        ],
                        "hawkeye_refs": [2, 11, 15],
                        "risk_level": "Medium",
                        "confidence": 0.88
                    },
                    {
                        "id": f"stakeholder_communication_{int(time.time())}",
                        "type": "suggestion",
                        "category": "Communication Standards",
                        "description": "Content structure and clarity could be enhanced for different stakeholder audiences. Technical details may not be accessible to business stakeholders, while executives may need more strategic context.",
                        "suggestion": "Improve stakeholder communication by: (1) Adding executive summary for senior leadership, (2) Including technical appendix for detailed analysis, (3) Providing glossary for technical terms, (4) Using visual aids (charts, diagrams) to illustrate complex concepts.",
                        "example": "Add section: 'Executive Summary (2-minute read)' with key impacts, root cause, and actions. Include 'Technical Details (Appendix A)' for implementation specifics. Use timeline diagram to show event sequence visually.",
                        "questions": [
                            "Will all intended audiences understand the content at their required level?",
                            "Are technical concepts explained in business terms where appropriate?",
                            "Would visual aids help communicate complex information more effectively?"
                        ],
                        "hawkeye_refs": [13, 17],
                        "risk_level": "Low",
                        "confidence": 0.82
                    }
                ]
            })

    def _enhanced_classify_risk_level(self, feedback_item):
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
        """Process chat queries with enhanced AI-Prism focused on guidelines and document analysis"""
        print(f"Processing enhanced chat query: {query[:50]}...")
        
        context_info = f"""
        Current Section: {context.get('current_section', 'Current section')}
        Document Type: Full Write-up Investigation
        Hawkeye Framework: 20-point comprehensive checklist
        Current Feedback Count: {context.get('current_feedback', [])}
        Accepted Items: {context.get('accepted_count', 0)}
        Rejected Items: {context.get('rejected_count', 0)}
        """
        
        prompt = f"""ENHANCED DOCUMENT ANALYSIS GUIDANCE REQUEST:
        
        CONTEXT:
        {context_info}
        
        USER QUESTION: {query}
        
        HAWKEYE FRAMEWORK REFERENCE:
        {self.hawkeye_checklist}
        
        ENHANCED RESPONSE REQUIREMENTS:
        1. Structure your response with clear sections using bullet points
        2. Use professional, guidelines-oriented language with specific examples
        3. Reference specific Hawkeye checkpoints with detailed explanations
        4. Provide concrete, actionable recommendations with implementation steps
        5. Use proper formatting with line breaks and clear organization
        6. Include specific examples and case studies when helpful
        7. End with targeted follow-up questions to continue the conversation
        8. Focus on practical, implementable guidance
        
        Format your response as:
        **[Main Topic]**
        
        • Key Point 1: [Detailed explanation with specific examples]
        • Key Point 2: [Detailed explanation with implementation steps]
        
        **Hawkeye References:**
        • Checkpoint #X: [Specific relevance and application]
        
        **Recommended Actions:**
        • Action 1: [Specific step with timeline and ownership]
        • Action 2: [Specific step with success criteria]
        
        **Follow-up Question:** [Engaging question to continue discussion]
        
        Provide helpful, specific guidance that references the Hawkeye guidelines with practical examples. Be professional, structured, and highly actionable."""
        
        system_prompt = """You are AI-Prism Enhanced, a senior CT EE investigation specialist providing expert guidance on document analysis and compliance. 
        
        Your responses must be:
        - Structured with clear bullet points and detailed sections
        - Professional and guidelines-oriented with specific examples
        - Actionable with concrete, implementable recommendations
        - Referenced to Hawkeye framework with detailed explanations
        - Formatted for easy reading with proper organization
        - Concluded with targeted follow-up questions
        - Focused on practical, real-world application
        
        Always maintain a professional tone while being highly helpful and providing specific, actionable guidance."""
        
        try:
            response = self._invoke_bedrock(system_prompt, prompt)
            return self._format_chat_response(response)
        except Exception as e:
            print(f"Enhanced chat processing error: {str(e)}")
            return self._enhanced_mock_chat_response(query, context)

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

    def _enhanced_mock_chat_response(self, query, context):
        """Generate enhanced structured mock chat responses for development/testing"""
        # Simulate processing delay
        time.sleep(1)
        
        query_lower = query.lower()
        current_section = context.get('current_section', 'current section')
        
        if 'help' in query_lower or 'how' in query_lower:
            return f"""**Enhanced AI-Prism Document Analysis Assistance**

• **Current Focus**: Comprehensive analysis of '{current_section}' section using advanced Hawkeye framework methodology
• **Core Capabilities**: Deep investigation quality assessment, compliance validation, risk evaluation with quantified metrics
• **Framework Application**: 20-point comprehensive checklist with enhanced specificity and actionable recommendations

**Key Areas I Can Help With:**
• Investigation methodology and evidence validation with specific verification techniques
• Risk assessment and classification protocols with detailed impact analysis
• Documentation quality and compliance standards with audit-ready requirements
• Stakeholder communication and reporting clarity with audience-specific guidance

**Enhanced Hawkeye References:**
• Checkpoint #2: Investigation Process - Advanced methodology validation with cross-verification
• Checkpoint #15: Quality Control - Comprehensive standards compliance with independent validation

**Recommended Next Steps:**
• Identify specific areas needing improvement in current section with measurable criteria
• Apply relevant Hawkeye checkpoints for comprehensive analysis with evidence requirements
• Establish success metrics and validation methods for each improvement area

**Follow-up Question:** What particular aspect of '{current_section}' would you like me to analyze in detail with specific improvement recommendations?"""
        
        elif 'hawkeye' in query_lower or 'framework' in query_lower:
            return f"""**Enhanced Hawkeye Framework Application**

• **Framework Overview**: Comprehensive 20-point investigation checklist with enhanced specificity ensuring thorough document analysis
• **Current Section Relevance**: '{current_section}' requires specific checkpoint validation for compliance with detailed implementation guidance
• **Quality Assurance**: Systematic approach to investigation documentation and reporting with audit-ready standards

**Most Relevant Checkpoints for '{current_section}':**
• Checkpoint #2: Investigation Process - Ensure thorough methodology and evidence validation with independent verification
• Checkpoint #11: Root Cause Analysis - Identify systemic issues and underlying causes using 5-whys and fishbone analysis
• Checkpoint #13: Documentation & Reporting - Maintain professional quality standards with stakeholder-appropriate communication
• Checkpoint #15: Quality Control - Validate findings and ensure accuracy through cross-verification and independent review

**Enhanced Implementation Guidelines:**
• Apply systematic review process for each checkpoint with specific validation criteria
• Document evidence supporting compliance with each standard using measurable metrics
• Identify gaps requiring additional investigation or clarification with specific remediation steps
• Establish monitoring and review processes to ensure sustained compliance

**Recommended Actions:**
• Review current section against applicable checkpoints with detailed assessment criteria
• Document compliance status for each relevant standard with evidence and validation methods
• Create improvement plan with specific timelines, ownership, and success metrics

**Follow-up Question:** Which specific Hawkeye checkpoint would you like me to explain in greater detail with practical implementation examples?"""
        
        else:
            return f"""**Enhanced AI-Prism Analysis Guidance**

• **Query Understanding**: Comprehensive analysis request for "{query}" regarding '{current_section}' section
• **Expertise Areas**: Advanced document analysis, quality assessment, compliance validation, risk evaluation with quantified impact
• **Framework Application**: Enhanced Hawkeye methodology for comprehensive investigation review with actionable recommendations

**Available Assistance Areas:**
• **Document Analysis**: Comprehensive quality assessment and compliance validation with specific improvement recommendations
• **Hawkeye Framework**: Application of 20-point investigation checklist with detailed implementation guidance
• **Risk Evaluation**: Classification and impact assessment protocols with quantified metrics and validation methods
• **Evidence Validation**: Verification techniques and quality standards with independent cross-verification
• **Stakeholder Communication**: Professional reporting and clarity enhancement with audience-specific guidance

**Enhanced Analysis Approach:**
• Systematic review using established quality standards with measurable criteria
• Evidence-based assessment with supporting documentation and independent validation
• Risk-focused evaluation with clear classification criteria and impact quantification
• Actionable recommendations with implementation guidance, timelines, and success metrics

**Hawkeye References:**
• Multiple checkpoints applicable based on specific analysis requirements with detailed implementation guidance
• Framework provides comprehensive quality assurance methodology with validation protocols

**Recommended Next Steps:**
• Clarify specific analysis requirements for targeted guidance with measurable outcomes
• Identify priority areas for detailed investigation with resource allocation and timeline planning
• Establish success criteria and validation methods for each improvement area

**Follow-up Question:** What specific aspect of '{current_section}' analysis would be most helpful for your current needs, and what level of detail would you like in the recommendations?"""