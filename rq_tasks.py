"""
RQ Tasks for AI-Prism Document Analysis
Simplified replacement for celery_tasks_enhanced.py (792 lines → ~250 lines)

Key Improvements over Celery:
- No signature expiration issues
- No complex S3 result backend
- Results stored directly in Redis
- Simple Python functions (no decorators, no base classes)
- 75% less code

Usage:
    from rq_config import get_queue
    from rq_tasks import analyze_section_task

    queue = get_queue('analysis')
    job = queue.enqueue(analyze_section_task, args=(...), job_timeout=300)
"""

import os
import sys
import json
import time
import re
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime
from botocore.config import Config

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.bedrock_prompt_templates import BedrockPromptTemplate
from config.model_config_enhanced import get_primary_model, FEEDBACK_MIN_CONFIDENCE


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_bedrock_client():
    """
    Create AWS Bedrock client with optimized configuration

    Returns:
        boto3.client: Configured Bedrock Runtime client
    """
    boto_config = Config(
        connect_timeout=15,
        read_timeout=240,
        retries={'max_attempts': 3, 'mode': 'standard'},
        max_pool_connections=50
    )

    bedrock_region = os.environ.get('BEDROCK_REGION', 'us-east-2')

    return boto3.client(
        'bedrock-runtime',
        region_name=bedrock_region,
        config=boto_config
    )


def invoke_bedrock_model(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Invoke AWS Bedrock Claude model with prompts

    Args:
        system_prompt: System instruction prompt
        user_prompt: User query/task prompt

    Returns:
        Dict with result, model_used, and tokens

    Raises:
        Exception: If invocation fails
    """
    bedrock_client = get_bedrock_client()
    model_config = get_primary_model()

    request_body = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': model_config.max_tokens,
        'temperature': model_config.temperature,
        'system': system_prompt,
        'messages': [
            {
                'role': 'user',
                'content': user_prompt
            }
        ]
    }

    response = bedrock_client.invoke_model(
        modelId=model_config.id,
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())

    # Extract text from content blocks
    content_blocks = response_body.get('content', [])
    result_text = ''
    for block in content_blocks:
        if block.get('type') == 'text':
            result_text += block.get('text', '')

    # Get usage stats
    usage = response_body.get('usage', {})

    return {
        'success': True,
        'result': result_text,
        'model_used': model_config.name,
        'tokens': {
            'input': usage.get('input_tokens', 0),
            'output': usage.get('output_tokens', 0)
        }
    }


def load_hawkeye_checklist() -> str:
    """
    Load Hawkeye framework checklist

    Returns:
        Checklist content as string
    """
    try:
        checklist_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'hawkeye_checklist.txt'
        )

        if os.path.exists(checklist_path):
            with open(checklist_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback to basic checklist
            return """Hawkeye 20-Point Investigation Checklist:
1. Initial Assessment - Proper incident categorization and priority
2. Investigation Process - Systematic evidence collection
3. Seller Classification - Accurate account classification
4. Enforcement - Appropriate enforcement actions
5. Verification - Evidence validation and verification
6. Appeals - Fair appeals handling process
7. Security - Security measures and data protection
8. Funds - Financial impact assessment
9. Outreach - Stakeholder communication
10. Sentiment - Customer sentiment analysis
11. Root Cause - Root cause identification
12. Prevention - Preventive measures
13. Documentation - Complete documentation
14. Collaboration - Cross-team collaboration
15. Quality Control - QC review process
16. Improvement - Continuous improvement
17. Communication - Clear communication
18. Metrics - Performance metrics tracking
19. Legal - Legal compliance
20. Launch - Implementation and rollout"""
    except Exception as e:
        print(f"⚠️ Could not load Hawkeye checklist: {e}")
        return "Hawkeye Investigation Framework - Standard investigation checklist"


def get_hawkeye_sections() -> Dict[int, str]:
    """
    Get Hawkeye framework section checkpoints

    Returns:
        Dict mapping checkpoint numbers to descriptions
    """
    return {
        1: "Initial Assessment",
        2: "Investigation Process",
        3: "Seller Classification",
        4: "Enforcement",
        5: "Verification",
        6: "Appeals",
        7: "Security",
        8: "Funds",
        9: "Outreach",
        10: "Sentiment",
        11: "Root Cause",
        12: "Prevention",
        13: "Documentation",
        14: "Collaboration",
        15: "Quality Control",
        16: "Improvement",
        17: "Communication",
        18: "Metrics",
        19: "Legal",
        20: "Launch"
    }


# ============================================================================
# RQ TASK 1: DOCUMENT SECTION ANALYSIS
# ============================================================================

def analyze_section_task(
    section_name: str,
    content: str,
    doc_type: str = "Investigation Report",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a document section using AWS Bedrock Claude

    This is a REGULAR PYTHON FUNCTION - RQ handles all the task magic!
    No decorators, no complex base classes, just return the result.

    Args:
        section_name: Section name to analyze
        content: Section content text
        doc_type: Document type (default: "Investigation Report")
        session_id: Session ID for tracking (optional)

    Returns:
        Dict with:
            - success: bool
            - feedback_items: List of feedback items (confidence >= 0.80)
            - section: Section name
            - duration: Processing time in seconds
            - model_used: AI model name
            - tokens: Token usage stats
            - feedback_count: Number of feedback items
    """
    start_time = time.time()

    try:
        print(f"📝 [RQ] Analyzing section: {section_name}")

        # Build prompts using AWS Bedrock templates
        hawkeye_checkpoints = get_hawkeye_sections()
        hawkeye_guidelines = load_hawkeye_checklist()

        system_prompt = BedrockPromptTemplate.build_system_prompt(
            role="Senior Investigation Analyst",
            expertise=[
                "Hawkeye investigation framework",
                "Document quality assessment",
                "Risk analysis and compliance",
                "Investigation best practices"
            ],
            guidelines=hawkeye_guidelines
        )

        user_prompt = BedrockPromptTemplate.build_analysis_prompt(
            section_name=section_name,
            content=content,
            framework_checkpoints=hawkeye_checkpoints,
            doc_type=doc_type,
            max_feedback_items=10
        )

        # Invoke Bedrock API
        result = invoke_bedrock_model(system_prompt, user_prompt)

        if not result['success']:
            raise Exception("Bedrock invocation failed")

        # Parse response
        response_text = result['result']

        # Clean up response (remove markdown if present)
        cleaned = response_text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        # Parse JSON
        try:
            analysis_result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"Response preview: {response_text[:500]}")

            # Try to extract JSON
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group(0))
            else:
                raise Exception(f"Failed to parse AI response: {e}")

        # Validate and filter feedback
        feedback_items = analysis_result.get('feedback_items', [])

        # Filter by confidence >= 0.80 (configurable via FEEDBACK_MIN_CONFIDENCE)
        high_quality_items = [
            item for item in feedback_items
            if isinstance(item, dict) and item.get('confidence', 0) >= FEEDBACK_MIN_CONFIDENCE
        ]

        duration = time.time() - start_time

        print(f"✅ [RQ] Complete: {len(high_quality_items)} items ({duration:.2f}s)")

        return {
            'success': True,
            'feedback_items': high_quality_items,
            'section': section_name,
            'duration': round(duration, 2),
            'model_used': result['model_used'],
            'tokens': result['tokens'],
            'feedback_count': len(high_quality_items)
        }

    except Exception as e:
        error_msg = str(e)
        duration = time.time() - start_time

        print(f"❌ [RQ] Error analyzing {section_name}: {error_msg}")

        return {
            'success': False,
            'error': error_msg,
            'section': section_name,
            'duration': round(duration, 2)
        }


# ============================================================================
# RQ TASK 2: CHAT PROCESSING
# ============================================================================

def process_chat_task(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process chat message with Claude

    Again - just a regular function! RQ stores the result automatically.

    Args:
        query: User query text
        context: Chat context dict (history, session info, etc.)

    Returns:
        Dict with:
            - success: bool
            - response: Chat response text
            - duration: Processing time
            - model_used: AI model name
            - tokens: Token usage stats
    """
    start_time = time.time()

    try:
        print(f"💬 [RQ] Processing chat: {query[:50]}...")

        # Build prompts
        framework_overview = """Hawkeye 20-Point Investigation Checklist covering:
Initial Assessment, Investigation Process, Seller Classification, Enforcement,
Verification, Appeals, Security, Funds, Outreach, Sentiment, Root Cause,
Prevention, Documentation, Collaboration, QC, Improvement, Communication,
Metrics, Legal, Launch."""

        system_prompt = BedrockPromptTemplate.build_system_prompt(
            role="Hawkeye Framework Expert",
            expertise=[
                "Investigation framework guidance",
                "Document review assistance",
                "Best practices consulting"
            ]
        )

        user_prompt = BedrockPromptTemplate.build_chat_prompt(
            user_query=query,
            context=context,
            framework_overview=framework_overview
        )

        # Invoke Bedrock
        result = invoke_bedrock_model(system_prompt, user_prompt)

        if not result['success']:
            raise Exception("Bedrock invocation failed")

        duration = time.time() - start_time

        print(f"✅ [RQ] Chat complete ({duration:.2f}s)")

        return {
            'success': True,
            'response': result['result'],
            'duration': round(duration, 2),
            'model_used': result['model_used'],
            'tokens': result['tokens']
        }

    except Exception as e:
        error_msg = str(e)
        duration = time.time() - start_time

        print(f"❌ [RQ] Chat error: {error_msg}")

        return {
            'success': False,
            'error': error_msg,
            'duration': round(duration, 2)
        }


# ============================================================================
# RQ TASK 3: HEALTH MONITORING
# ============================================================================

def monitor_health() -> Dict[str, Any]:
    """
    Simple health check task

    Can be scheduled with RQ Scheduler for periodic health monitoring

    Returns:
        Dict with health status and timestamp
    """
    try:
        from core.async_request_manager import get_async_request_manager

        # Get stats from request manager
        async_manager = get_async_request_manager()
        stats = async_manager.get_stats()

        print("=" * 60)
        print("📊 SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Failed: {stats['failed_requests']}")
        print(f"Throttled: {stats['throttled_requests']}")
        print(f"Active: {stats['active_requests']}")
        print(f"Requests/min: {stats['requests_last_minute']}")
        print(f"Tokens/min: {stats['tokens_last_minute']}")
        print(f"Avg Response: {stats['avg_response_time']:.2f}s")
        print("=" * 60)

        return {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }

    except Exception as e:
        print(f"❌ Health check error: {e}")

        return {
            'success': False,
            'status': 'degraded',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


# ============================================================================
# TASK PROGRESS TRACKING (Optional)
# ============================================================================

def update_job_progress(job, progress: int, status: str):
    """
    Update RQ job progress metadata

    Args:
        job: RQ Job instance
        progress: Progress percentage (0-100)
        status: Status message
    """
    if job:
        job.meta['progress'] = progress
        job.meta['status'] = status
        job.save_meta()


# ============================================================================
# MODULE INFO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RQ Tasks for AI-Prism")
    print("=" * 70)
    print("\nAvailable Tasks:")
    print("  1. analyze_section_task(section_name, content, doc_type, session_id)")
    print("  2. process_chat_task(query, context)")
    print("  3. monitor_health()")
    print("\nUsage:")
    print("  from rq_config import get_queue")
    print("  from rq_tasks import analyze_section_task")
    print("")
    print("  queue = get_queue('analysis')")
    print("  job = queue.enqueue(analyze_section_task, args=(...), job_timeout=300)")
    print("  result = job.result  # When job.is_finished")
    print("\nBenefits over Celery:")
    print("  ✅ No AWS signature expiration")
    print("  ✅ No S3 result backend polling")
    print("  ✅ 75% less code (250 lines vs 792)")
    print("  ✅ Simple Python functions")
    print("  ✅ Results stored in Redis")
    print("=" * 70)
