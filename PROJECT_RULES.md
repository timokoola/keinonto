# Project Development Rules and Guidelines

## Schema-Driven Development Principles

### 1. Data Schema First
- All data structures must be defined using Pydantic models
- Schema definitions should be placed in a dedicated `schemas/` directory
- Every schema must include type hints and field validations
- Use descriptive field names and include field descriptions in docstrings

### 2. API Contract Definition
- All API endpoints must have corresponding request/response schemas
- Use OpenAPI/Swagger for API documentation
- Implement strict validation for all incoming data
- Define clear error responses and status codes

### 3. Code Organization
```python
project_root/
├── schemas/          # All Pydantic models and data schemas
├── api/              # API endpoints and routing
├── services/         # Business logic and service layer
├── repositories/     # Data access layer
├── tests/           # Test suites
└── utils/           # Utility functions and helpers
```

### 4. Testing Requirements
- All schemas must have corresponding test cases
- Test coverage must be maintained above 80%
- Integration tests must validate schema compliance
- Use pytest for testing framework

## Project-Specific Design Principles

### 1. Code Quality Standards
- Use Black for code formatting (line length: 88 characters)
- Implement Flake8 for code linting
- Use isort for import sorting
- Maintain pylint score above 9.0

### 2. Documentation Requirements
- All functions must have docstrings (Google style)
- README must be kept up-to-date
- Include examples for complex functionality
- Document all configuration options

### 3. Development Workflow
- Feature branches must follow pattern: `feature/description`
- Commits must follow conventional commits specification
- Pull requests require at least one reviewer
- CI must pass before merge

### 4. Error Handling
- Use custom exception classes
- Implement proper error logging
- Include error context in responses
- Handle edge cases explicitly

### 5. Security Practices
- No secrets in code
- Use environment variables for configuration
- Implement input sanitization
- Regular dependency updates

### 6. Performance Guidelines
- Cache expensive operations
- Use async operations where appropriate
- Implement pagination for large datasets
- Monitor and optimize database queries

### 7. Maintainability
- Keep functions small and focused
- Maximum complexity per function: 10
- Use dependency injection
- Implement interface segregation

## Version Control Guidelines

### 1. Commit Messages
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```
Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### 2. Branch Strategy
- main: Production-ready code
- develop: Integration branch
- feature/*: New features
- bugfix/*: Bug fixes
- release/*: Release preparation

## Development Environment Setup
- Use virtual environments
- Install development dependencies
- Configure pre-commit hooks
- Set up linting and formatting tools

## Review Process
1. Code Review Checklist
   - Schema compliance
   - Test coverage
   - Documentation
   - Performance considerations
   - Security implications

2. Quality Gates
   - All tests passing
   - Coverage requirements met
   - No linting errors
   - Documentation updated 