# Code Review Checklist

Key items to check during MR code review.

## 1. Architecture & Design

- [ ] Do changes follow project architecture?
- [ ] Is layer separation correct? (Controller/Service/Repository)
- [ ] Is dependency direction correct?
- [ ] Is single responsibility principle followed?
- [ ] Is there no unnecessary complexity?

## 2. Code Quality

- [ ] Are variable/function/class names clear?
- [ ] Are magic numbers/strings defined as constants?
- [ ] Is there no duplicate code?
- [ ] Are functions not too long? (30 lines or less recommended)
- [ ] Are complex logic sections properly commented?

## 3. Error Handling

- [ ] Are exceptions handled appropriately?
- [ ] Are error messages clear?
- [ ] Is try-catch used appropriately?
- [ ] Are errors properly logged?
- [ ] Are user-friendly error messages provided?

## 4. Security

- [ ] Is there no SQL Injection risk?
- [ ] Are there no XSS vulnerabilities?
- [ ] Is sensitive information (API keys, passwords) not hardcoded?
- [ ] Is authentication/authorization properly implemented?
- [ ] Is input validation sufficient?

## 5. Performance

- [ ] Is there no N+1 query problem?
- [ ] Are there no unnecessary database calls?
- [ ] Is there no memory leak potential?
- [ ] Are there no inefficient loops?
- [ ] Is caching used appropriately?

## 6. Testing

- [ ] Are tests added for new features?
- [ ] Do tests cover success/failure/edge cases?
- [ ] Do existing tests still pass?
- [ ] Is test coverage sufficient?
- [ ] Are mocks used appropriately?

## 7. Readability & Maintainability

- [ ] Is code easy to read?
- [ ] Is consistent coding style followed?
- [ ] Are imports properly organized?
- [ ] Is unused code removed?
- [ ] Are TODO/FIXME properly managed?

## 8. Business Logic

- [ ] Are requirements met?
- [ ] Are edge cases handled?
- [ ] Are business rules correctly implemented?
- [ ] Is data consistency maintained?
- [ ] Is transaction handling appropriate?

## Severity Criteria

### 🔴 Critical (Must Fix)
- Security vulnerabilities
- Data loss risk
- Production failure possibility
- Severe performance issues

### 🟡 High Priority (Strongly Recommended to Fix)
- Bug possibility
- Code quality degradation
- Maintenance difficulty
- Missing tests

### 🟢 Medium Priority (Improvement Recommended)
- Naming improvements
- Duplicate code removal
- Adding comments
- Refactoring suggestions
