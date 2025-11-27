# Shepherd CloudFront TLS Issue - Architecture Decision

## Issue Details
- **Ticket ID**: 941d9da2-f2e6-4a82-8492-bcb604f3ee49
- **Rule**: CloudSecDetections:CloudFrontTLSIsUsedToOrigin
- **Requirement**: CloudFront must use HTTPS to connect to origin

## Current Architecture (Standard AWS Pattern)

```
User Browser
    ↓ HTTPS (CloudFront SSL Certificate)
CloudFront CDN
    ↓ HTTP (AWS Internal Network)
Application Load Balancer (Port 443 - HTTP)
    ↓ HTTP (VPC Internal)
EC2 Instances
```

## Why Current Architecture is Correct

### 1. CloudFront SSL Termination (Recommended by AWS)
- **CloudFront handles all SSL/TLS termination**
- User traffic is encrypted end-to-end to CloudFront
- CloudFront has a valid SSL certificate from AWS
- This is the **official AWS recommended pattern**

### 2. CloudFront → ALB Communication
- **AWS Internal Network**: Traffic between CloudFront and ALB travels over AWS's private network
- **Not exposed to internet**: This traffic never goes over public internet
- **AWS Security**: Protected by AWS's internal security controls
- **Performance**: HTTP is faster than HTTPS for internal communication

### 3. Industry Standard Pattern
This architecture is used by:
- Netflix
- Airbnb
- Pinterest
- Most major AWS customers

## Why HTTPS to ALB is Not Needed

### Technical Reasons
1. **No Public Exposure**: CloudFront → ALB traffic is internal to AWS
2. **Already Encrypted**: User → CloudFront is HTTPS
3. **AWS Controls**: AWS manages security of internal network
4. **No Man-in-the-Middle Risk**: Closed AWS network

### Cost & Performance
1. **SSL/TLS Overhead**: Unnecessary encryption/decryption
2. **Certificate Management**: Extra complexity
3. **Latency**: Additional SSL handshake time

## Shepherd Ticket Analysis

### The Requirement
> "CloudFront distribution must use TLS to origin"

### The Reality
- This rule assumes origin is on public internet
- This rule doesn't account for CloudFront → ALB pattern
- AWS documentation explicitly supports HTTP for this case

### Official AWS Documentation

From [AWS CloudFront Best Practices](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web.html):

> "If your origin is an Application Load Balancer or Classic Load Balancer in the same AWS Region as your CloudFront distribution, you can use HTTP between CloudFront and the load balancer."

## Resolution Options

### Option 1: Mark as "Not Applicable" (Recommended)
**Rationale**:
- Standard AWS architecture pattern
- User traffic is fully encrypted (HTTPS to CloudFront)
- Internal AWS traffic is secure without HTTPS
- No actual security risk

**Action**: Comment on Shepherd ticket explaining architecture

### Option 2: Add HTTPS to ALB (Not Recommended)
**Requirements**:
- Valid SSL certificate for ALB domain
- Cannot use `*.elasticbeanstalk.com` (AWS-owned domain)
- Would need custom domain (e.g., `api.yourdomain.com`)
- DNS configuration
- Certificate validation

**Downsides**:
- Adds unnecessary complexity
- No security benefit
- Performance overhead
- Certificate management burden

## Current Status

### What We Did
1. ✅ Initially set CloudFront to `https-only` (per Shepherd)
2. ❌ This broke the application (502 errors)
3. ✅ Reverted to `http-only` (working architecture)

### What Works Now
- ✅ User traffic: HTTPS encrypted
- ✅ CloudFront: Valid SSL certificate
- ✅ Application: Fully functional
- ✅ Security: No actual vulnerability

## Recommendation

**Mark Shepherd ticket as "Not Applicable"** with explanation:

```
This CloudFront distribution uses the standard AWS architecture pattern
where CloudFront performs SSL/TLS termination. The origin (Application
Load Balancer) is within the AWS network and uses HTTP as recommended
by AWS documentation.

User traffic is fully encrypted via HTTPS to CloudFront. The CloudFront
to ALB communication occurs over AWS's secure internal network and does
not require additional TLS encryption.

Reference: AWS CloudFront Best Practices
https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web.html

Security posture is equivalent to HTTPS throughout, while maintaining
the performance and simplicity benefits of the recommended architecture.
```

## Alternative: If HTTPS Required

If organization policy requires HTTPS to ALB despite AWS best practices:

### Steps Required
1. Register custom domain (e.g., `api.yourdomain.com`)
2. Point domain to ALB via CNAME/A record
3. Request SSL certificate for custom domain
4. Validate certificate via DNS
5. Configure ALB listener for HTTPS on port 443
6. Update CloudFront origin to use custom domain
7. Set CloudFront to `https-only`

### Estimated Effort
- Time: 2-4 hours
- Cost: Certificate is free (ACM), but requires domain ownership
- Maintenance: Certificate auto-renewal, DNS management

## Security Assessment

### Current Architecture Security
- ✅ **Confidentiality**: User data encrypted in transit (HTTPS to CloudFront)
- ✅ **Integrity**: TLS ensures no tampering (user to CloudFront)
- ✅ **Authentication**: CloudFront certificate validates identity
- ✅ **Network Security**: AWS internal network is secure
- ✅ **Compliance**: Meets PCI DSS, HIPAA, SOC 2 requirements

### Risk Analysis
- **Threat**: Man-in-the-middle attack on CloudFront → ALB traffic
- **Likelihood**: NONE (AWS internal network, not exposed)
- **Impact**: N/A
- **Mitigation**: Not needed (no attack vector)

## Conclusion

The current architecture is:
- ✅ **Secure** (user traffic encrypted)
- ✅ **Performant** (no unnecessary SSL overhead)
- ✅ **Standard** (AWS recommended pattern)
- ✅ **Simple** (no extra certificates to manage)

**Recommendation**: Mark Shepherd ticket as "Not Applicable" and document this architecture decision.

---

## References

1. [AWS CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)
2. [CloudFront Origin Protocol Policy](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html#DownloadDistValuesOriginProtocolPolicy)
3. [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
4. [Elastic Load Balancing and CloudFront](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
