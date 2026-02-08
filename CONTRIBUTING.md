# Contributing to GBP Audit Bot

Thank you for your interest in contributing to GBP Audit Bot! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Backend Development**:
   - Python 3.10+
   - PostgreSQL 14+
   - Virtual environment tools (venv or virtualenv)
   - API keys for testing (ScaleSERP, OpenAI)

2. **Frontend Development**:
   - Node.js 18+
   - npm 9+
   - Basic knowledge of React and Next.js

3. **Tools**:
   - Git
   - Code editor (VS Code recommended)
   - PostgreSQL client (pgAdmin, DBeaver, etc.)

### Setting Up Development Environment

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/gbp.git
   cd gbp
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   copy .env.example .env
   # Edit .env with your test credentials
   python init_db.py
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## 🔄 Development Workflow

### Branch Naming Convention

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test additions or modifications

### Development Process

1. **Create an Issue** (if one doesn't exist)
   - Describe the feature or bug
   - Wait for approval from maintainers

2. **Develop Your Changes**
   - Write clean, documented code
   - Follow coding standards (see below)
   - Add tests for new functionality

3. **Test Thoroughly**
   - Run existing tests
   - Add new tests for your changes
   - Test manually in development environment

4. **Commit Your Changes**
   - Follow commit message guidelines
   - Keep commits atomic and focused

5. **Push and Create Pull Request**
   - Push to your fork
   - Create a PR against the `main` branch
   - Fill out the PR template completely

## 💻 Coding Standards

### Python (Backend)

#### Style Guide
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Maximum line length: **88 characters** (Black formatter default)

#### Code Formatting
```bash
# Install development tools
pip install black flake8 mypy

# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

#### Example Code Style
```python
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

async def calculate_metrics(
    scan_id: UUID,
    points: List[ScanPoint]
) -> Optional[Decimal]:
    """
    Calculate average rank position for a scan.
    
    Args:
        scan_id: UUID of the scan
        points: List of scan point results
        
    Returns:
        Average rank as Decimal, or None if no valid points
    """
    valid_ranks = [p.rank_position for p in points if p.rank_position]
    
    if not valid_ranks:
        return None
        
    return Decimal(sum(valid_ranks)) / Decimal(len(valid_ranks))
```

#### Documentation
- Use **docstrings** for all functions, classes, and modules
- Follow **Google-style** or **NumPy-style** docstring format
- Include type information in docstrings

### TypeScript/React (Frontend)

#### Style Guide
- Use **TypeScript** for all new code
- Follow **Airbnb React/JSX Style Guide**
- Use **functional components** with hooks

#### Code Formatting
```bash
# Run linter
npm run lint

# Format code (if configured)
npm run format
```

#### Example Code Style
```typescript
import { useState, useEffect } from 'react';
import type { Project, Scan } from '@/types';

interface ProjectCardProps {
  project: Project;
  onScanComplete?: (scan: Scan) => void;
}

export function ProjectCard({ project, onScanComplete }: ProjectCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Effect logic here
  }, [project.id]);

  const handleScan = async () => {
    setIsLoading(true);
    try {
      // Scan logic
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="project-card">
      {/* Component JSX */}
    </div>
  );
}
```

#### Component Guidelines
- One component per file
- Use named exports for components
- Keep components small and focused
- Extract reusable logic into custom hooks

### Database Migrations

When modifying database schema:

1. **Create Migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Review Migration**:
   - Check generated migration file
   - Ensure both `upgrade()` and `downgrade()` are correct

3. **Test Migration**:
   ```bash
   # Apply migration
   alembic upgrade head
   
   # Test rollback
   alembic downgrade -1
   alembic upgrade head
   ```

## 🧪 Testing

### Backend Testing

#### Running Tests
```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_geogrid.py

# Specific test
pytest tests/test_geogrid.py::test_generate_grid_5x5
```

#### Writing Tests
```python
import pytest
from app.services.geogrid import generate_grid

def test_generate_grid_5x5():
    """Test 5x5 grid generation."""
    points = generate_grid(
        lat=40.7128,
        lng=-74.0060,
        radius_km=5.0,
        grid_size=5
    )
    
    assert len(points) == 25
    assert points[12]['label'] == 'C3'  # Center point
    assert points[12]['x'] == 2
    assert points[12]['y'] == 2

@pytest.mark.asyncio
async def test_serp_search():
    """Test SERP API integration."""
    # Test implementation
    pass
```

#### Test Coverage Requirements
- **Minimum coverage**: 80%
- All new features must include tests
- Bug fixes should include regression tests

### Frontend Testing

```bash
cd frontend

# Run tests (when configured)
npm test

# Run tests in watch mode
npm test -- --watch
```

## 📝 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples

```bash
# Feature
git commit -m "feat(search): add support for 7x7 grid size"

# Bug fix
git commit -m "fix(pdf): correct heatmap aspect ratio in reports"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Refactor
git commit -m "refactor(geogrid): optimize coordinate calculation algorithm"
```

### Commit Best Practices

- **Atomic commits**: One logical change per commit
- **Clear messages**: Describe what and why, not how
- **Present tense**: "Add feature" not "Added feature"
- **Reference issues**: Include issue number when applicable

## 🔀 Pull Request Process

### Before Submitting

1. ✅ **Code compiles** without errors
2. ✅ **All tests pass**
3. ✅ **Code is formatted** according to style guide
4. ✅ **Documentation updated** (if applicable)
5. ✅ **No merge conflicts** with main branch

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer reviews
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges to main branch

### After Merge

- Delete your feature branch
- Update your local main branch
- Close related issues

## 📁 Project Structure

### Backend Structure
```
backend/app/
├── models/          # Database models (SQLAlchemy)
├── routers/         # API endpoints (FastAPI)
├── services/        # Business logic
│   ├── geogrid.py   # Grid generation
│   ├── serp.py      # SERP API integration
│   ├── ai_analysis.py  # OpenAI integration
│   ├── pdf_report.py   # PDF generation
│   ├── whatsapp.py     # WhatsApp integration
│   └── scheduler.py    # Cron jobs
├── auth.py          # Authentication utilities
├── config.py        # Configuration management
├── database.py      # Database connection
└── schemas.py       # Pydantic models
```

### Frontend Structure
```
frontend/src/
├── app/             # Next.js pages (App Router)
├── components/      # Reusable React components
├── contexts/        # React contexts (Auth, etc.)
└── lib/             # Utility functions
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional grid sizes (9x9, 11x11)
- [ ] Export formats (Excel, CSV)
- [ ] Advanced filtering and search
- [ ] Performance optimizations
- [ ] Mobile responsiveness improvements

### Medium Priority
- [ ] Dark mode support
- [ ] Multi-language support (i18n)
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Batch project operations

### Documentation
- [ ] API endpoint examples
- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] Deployment guides
- [ ] Troubleshooting guide

## 🤔 Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Review documentation
3. Ask in project discussions
4. Contact maintainers

## 🙏 Thank You!

Your contributions make GBP Audit Bot better for everyone. We appreciate your time and effort!

---

**Happy Coding! 🚀**
