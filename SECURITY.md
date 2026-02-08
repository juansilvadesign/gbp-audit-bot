# Security Policy

## 🔒 Security Overview

The security of GBP Audit Bot is a top priority. This document outlines our security practices, how to report vulnerabilities, and security best practices for deployment.

## 📋 Table of Contents

- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [Security Best Practices](#security-best-practices)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [API Security](#api-security)
- [Infrastructure Security](#infrastructure-security)
- [Known Security Considerations](#known-security-considerations)

## 🛡️ Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## 🚨 Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public issue
2. **DO NOT** disclose the vulnerability publicly until it has been addressed
3. Email the security team at: **security@locuz.com** (or your designated security email)

### What to Include

Please provide the following information in your report:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and severity
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Proof of Concept**: Code or screenshots demonstrating the vulnerability
- **Suggested Fix**: If you have ideas for remediation
- **Your Contact Information**: For follow-up questions

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - **Critical**: 1-7 days
  - **High**: 7-14 days
  - **Medium**: 14-30 days
  - **Low**: 30-90 days

### Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide regular updates on our progress
- We will notify you when the vulnerability is fixed
- We will publicly disclose the vulnerability after a fix is released (with your permission)
- We may credit you in our security acknowledgments (if desired)

## 🔐 Security Best Practices

### For Deployment

#### 1. Environment Variables

**NEVER** commit sensitive information to version control:

```bash
# ❌ WRONG - Never do this
DATABASE_URL=postgresql://user:password@localhost/db

# ✅ CORRECT - Use environment variables
DATABASE_URL=${DATABASE_URL}
```

**Always use strong, unique values:**

```bash
# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use in .env
SECRET_KEY=your_generated_secure_key_here
```

#### 2. Database Security

- Use **strong passwords** for database users
- Restrict database access to **specific IP addresses**
- Enable **SSL/TLS** for database connections
- Regularly **backup** your database
- Use **read-only replicas** for reporting queries

```python
# Production database URL with SSL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

#### 3. API Key Management

- Store API keys in **environment variables** or **secret management systems**
- Rotate API keys **regularly**
- Use **different keys** for development, staging, and production
- Monitor API key usage for **anomalies**

#### 4. HTTPS/TLS

**Always use HTTPS in production:**

```python
# Force HTTPS in production
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

#### 5. CORS Configuration

**Restrict CORS to specific origins:**

```python
# ❌ WRONG - Too permissive
allow_origins=["*"]

# ✅ CORRECT - Specific origins
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

#### 6. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login():
    # Login logic
    pass
```

## 🔑 Authentication & Authorization

### JWT Token Security

#### Token Configuration

```python
# Use strong secret key
SECRET_KEY = os.getenv("SECRET_KEY")  # 32+ characters
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Consider shorter expiration for sensitive operations
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### Token Best Practices

1. **Store tokens securely** on the client:
   - Use `httpOnly` cookies (preferred)
   - Or secure localStorage with XSS protection

2. **Implement token refresh** mechanism:
   - Short-lived access tokens (15-60 minutes)
   - Long-lived refresh tokens (7-30 days)

3. **Validate tokens** on every request:
   - Check expiration
   - Verify signature
   - Validate user still exists and is active

### Password Security

#### Password Requirements

- **Minimum length**: 8 characters
- **Complexity**: Mix of uppercase, lowercase, numbers, special characters
- **No common passwords**: Check against known password lists

#### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increase for higher security
)

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed)
```

### Authorization

Implement **role-based access control (RBAC)**:

```python
from app.auth import get_current_user, require_role

@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the project
    project = await get_project(project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete project
    await delete_project(project_id)
```

## 🛡️ Data Protection

### Sensitive Data

#### What We Store

- User credentials (hashed passwords)
- API keys (encrypted)
- Business location data
- Search history
- SERP results

#### Data Protection Measures

1. **Encryption at Rest**:
   ```sql
   -- Use PostgreSQL encryption
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   
   -- Encrypt sensitive columns
   INSERT INTO api_keys (user_id, encrypted_key)
   VALUES (user_id, pgp_sym_encrypt(api_key, encryption_key));
   ```

2. **Encryption in Transit**:
   - Use TLS 1.2+ for all connections
   - Enable SSL for database connections
   - Use HTTPS for all API requests

3. **Data Minimization**:
   - Only store necessary data
   - Regularly purge old scan data
   - Anonymize data when possible

### GDPR Compliance

For EU users, implement:

1. **Right to Access**: Provide user data export
2. **Right to Erasure**: Allow account deletion
3. **Data Portability**: Export data in standard formats
4. **Consent Management**: Track user consent

```python
@app.get("/api/user/export")
async def export_user_data(current_user: User = Depends(get_current_user)):
    """Export all user data (GDPR compliance)."""
    data = {
        "user": user_to_dict(current_user),
        "projects": [p.to_dict() for p in current_user.projects],
        "scans": await get_user_scans(current_user.id)
    }
    return JSONResponse(content=data)

@app.delete("/api/user/account")
async def delete_account(current_user: User = Depends(get_current_user)):
    """Delete user account and all associated data."""
    await delete_user_cascade(current_user.id)
    return {"message": "Account deleted successfully"}
```

## 🌐 API Security

### Input Validation

**Always validate and sanitize input:**

```python
from pydantic import BaseModel, Field, validator

class ProjectCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    target_keyword: str = Field(..., min_length=2, max_length=255)
    central_lat: float = Field(..., ge=-90, le=90)
    central_lng: float = Field(..., ge=-180, le=180)
    
    @validator('business_name', 'target_keyword')
    def sanitize_string(cls, v):
        # Remove potentially dangerous characters
        return v.strip()
```

### SQL Injection Prevention

**Use parameterized queries:**

```python
# ✅ CORRECT - SQLAlchemy ORM (safe)
projects = db.query(Project).filter(Project.user_id == user_id).all()

# ✅ CORRECT - Parameterized query
db.execute(
    "SELECT * FROM projects WHERE user_id = :user_id",
    {"user_id": user_id}
)

# ❌ WRONG - String concatenation (vulnerable)
db.execute(f"SELECT * FROM projects WHERE user_id = '{user_id}'")
```

### XSS Prevention

**Sanitize output in frontend:**

```typescript
// Use React's built-in XSS protection
<div>{project.business_name}</div>  // Safe

// For HTML content, use DOMPurify
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ 
  __html: DOMPurify.sanitize(htmlContent) 
}} />
```

### CSRF Protection

For state-changing operations:

```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/projects")
async def create_project(
    project: ProjectCreate,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    # Create project
```

## 🏗️ Infrastructure Security

### Server Hardening

1. **Keep software updated**:
   ```bash
   # Regular updates
   apt update && apt upgrade -y
   pip install --upgrade -r requirements.txt
   npm audit fix
   ```

2. **Firewall configuration**:
   ```bash
   # Allow only necessary ports
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

3. **Disable unnecessary services**:
   ```bash
   systemctl disable <unused-service>
   ```

### Monitoring & Logging

**Log security-relevant events:**

```python
import logging

logger = logging.getLogger(__name__)

# Log authentication attempts
logger.info(f"Login attempt for user: {email}")
logger.warning(f"Failed login attempt for user: {email}")

# Log authorization failures
logger.warning(f"Unauthorized access attempt by user {user_id} to project {project_id}")

# Log suspicious activity
logger.error(f"Potential SQL injection attempt: {query}")
```

**Monitor for:**
- Failed login attempts
- Unusual API usage patterns
- Database query anomalies
- High resource usage

### Backup & Recovery

1. **Regular backups**:
   ```bash
   # Daily database backup
   pg_dump gbp_check > backup_$(date +%Y%m%d).sql
   ```

2. **Test recovery procedures** regularly

3. **Store backups securely** (encrypted, off-site)

## ⚠️ Known Security Considerations

### Third-Party APIs

**ScaleSERP API**:
- API key transmitted in requests
- Rate limiting applied
- Monitor for unusual usage

**OpenAI API**:
- API key stored in environment
- Data sent to external service
- Consider data privacy implications

**WhatsApp API**:
- Secure webhook endpoints
- Validate incoming requests
- Encrypt sensitive messages

### Credit System

**Prevent credit abuse:**

```python
# Implement transaction locking
from sqlalchemy import select, update

async def deduct_credits(user_id: UUID, amount: int):
    async with db.begin():
        # Lock user row
        user = await db.execute(
            select(User)
            .where(User.id == user_id)
            .with_for_update()
        )
        
        if user.credits_balance < amount:
            raise InsufficientCreditsError()
        
        # Deduct credits
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(credits_balance=User.credits_balance - amount)
        )
```

### File Upload (Future Feature)

If implementing file uploads:

1. **Validate file types**
2. **Limit file sizes**
3. **Scan for malware**
4. **Store outside web root**
5. **Use unique filenames**

## 📚 Security Resources

### Tools

- **OWASP ZAP**: Web application security scanner
- **Bandit**: Python security linter
- **npm audit**: Node.js dependency scanner
- **SQLMap**: SQL injection testing

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## 🔄 Security Updates

We regularly review and update our security practices. Check this document periodically for updates.

**Last Updated**: February 2026

---

**Security is everyone's responsibility. Stay vigilant! 🛡️**
