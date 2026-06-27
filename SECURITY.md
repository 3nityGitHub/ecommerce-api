# Security Notes

## Vulnerability Scanning

This image is scanned with Trivy:

    trivy image ecommerce-api-api:latest

## Known Accepted Risks

### CVE-2025-62727 - Starlette DoS via Range header merging
- **Severity:** HIGH
- **Component:** starlette==0.41.3 (transitive dependency via fastapi==0.115.6)
- **Fixed in:** starlette==0.49.1
- **Status:** Accepted, not remediated yet
- **Reasoning:** FastAPI 0.115.x caps its Starlette dependency below 0.42.0, so
  this cannot be patched without a major FastAPI version bump. That upgrade
  carries breaking-change risk and has not yet been regression-tested against
  this service.
- **Risk assessment:** Denial-of-service class issue (malformed Range headers),
  not remote code execution or data exposure. Mitigated in part by the
  application not serving large file ranges or static file responses.
- **Remediation plan:** Track FastAPI's Starlette compatibility range; upgrade
  and re-test when a non-breaking path to Starlette 0.49.1+ is available.

## Remediated

### CVE-2024-47874 - Starlette DoS via multipart/form-data
- **Fixed by:** Upgrading fastapi from 0.115.0 to 0.115.6, which pulled
  starlette from 0.38.6 to 0.41.3.
