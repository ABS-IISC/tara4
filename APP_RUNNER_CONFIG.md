# AI-Prism App Runner Configuration

## Environment Variables

The following environment variables are configured in AWS App Runner:

### Core Configuration
- `AWS_REGION = us-east-1` - AWS region for Bedrock service
- `AWS_DEFAULT_REGION = us-east-1` - Fallback AWS region
- `FLASK_ENV = production` - Flask environment mode
- `PORT = 8080` - Application port (App Runner standard)

### Bedrock AI Configuration
- `BEDROCK_MODEL_ID = anthropic.claude-3-7-sonnet-20250219-v1:0` - Claude 3.7 Sonnet model with reasoning
- `BEDROCK_MAX_TOKENS = 8192` - Maximum tokens per request
- `BEDROCK_TEMPERATURE = 0.7` - AI response creativity (0.0-1.0)

### Reasoning Configuration (Claude 3.7 Sonnet)
- `REASONING_ENABLED = true` - Enable Claude's reasoning capabilities
- `REASONING_BUDGET_TOKENS = 2000` - Tokens allocated for reasoning process

## Model Features

### Claude 3.7 Sonnet (20250219-v1:0)
- **Reasoning**: Advanced step-by-step thinking process
- **Context**: Up to 8192 tokens for comprehensive document analysis
- **Performance**: Optimized for complex analytical tasks
- **Accuracy**: Enhanced reasoning leads to better feedback quality

## IAM Requirements

The App Runner service requires an IAM role with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0"
            ]
        }
    ]
}
```

## Configuration Validation

The application will log the following on startup:
- Environment mode (production/development)
- AWS region configuration
- Bedrock model ID
- Reasoning enablement status

## Troubleshooting

### Common Issues
1. **Model Access**: Ensure the IAM role has access to Claude 3.7 Sonnet
2. **Region**: Verify the model is available in us-east-1
3. **Reasoning**: Only supported on Claude 3.7 Sonnet (20250219-v1:0) and later
4. **Token Limits**: Monitor usage against the 8192 token limit

### Error Messages
- "Model access issue": Check IAM permissions for Bedrock
- "AWS region issue": Verify region configuration
- "Rate limiting": Implement retry logic or reduce request frequency

## Performance Optimization

### Reasoning Budget
- **2000 tokens**: Balanced reasoning depth and response speed
- **Higher values**: More thorough analysis but slower responses
- **Lower values**: Faster responses but less detailed reasoning

### Temperature Setting
- **0.7**: Good balance of creativity and consistency
- **Lower (0.1-0.5)**: More deterministic responses
- **Higher (0.8-1.0)**: More creative but potentially inconsistent

## Monitoring

Monitor the following metrics:
- Token usage per request
- Response times
- Error rates
- Reasoning token consumption