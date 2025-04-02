# Example Pull Request

This is an example of a well-written pull request. Notice how it provides clear information and follows all guidelines.

```markdown
# Pull Request: Add Login Page with Google Authentication

## Description
I've created a new login page that allows users to sign in with their Google account. This is part of the authentication system we discussed in issue #123.

Key changes:
- Created new `LoginPage` component
- Added Google OAuth integration
- Implemented user session management
- Added loading states and error handling
- Created tests for the login flow

## Type of Change
- [x] New feature (non-breaking change that adds functionality)
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update

## Related Issues
- Implements #123 (Add user authentication)
- Related to #124 (User profile page)

## Testing
### Unit Tests
- [x] Added tests for LoginPage component
- [x] Added tests for authentication service
- [x] All tests pass

### Manual Testing
1. Tested login flow with valid Google account
2. Verified error handling with invalid credentials
3. Tested on Chrome, Firefox, and Safari
4. Verified mobile responsiveness
5. Checked loading states and animations

## Checklist
- [x] My code follows the project's coding standards
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes

## Screenshots
### Desktop View
![Desktop Login Page](https://example.com/desktop-screenshot.png)

### Mobile View
![Mobile Login Page](https://example.com/mobile-screenshot.png)

### Error State
![Error Handling](https://example.com/error-screenshot.png)

## Additional Notes
- The Google OAuth credentials are stored in environment variables
- Added documentation for setting up OAuth in the README
- Used the new design system components
- Followed accessibility guidelines (WCAG 2.1)

## Reviewer Guidelines
Please check:
- Security of OAuth implementation
- Error handling completeness
- Mobile responsiveness
- Accessibility compliance
- Test coverage
```

## Why This is a Good Example

### 1. Clear Description
- Explains what was done and why
- Lists key changes
- Easy to understand

### 2. Proper Testing
- Both unit and manual testing covered
- Clear test scenarios
- Multiple browsers tested

### 3. Visual Evidence
- Screenshots included
- Different views shown
- Error states documented

### 4. Complete Checklist
- All items addressed
- Nothing overlooked
- Shows attention to detail

### 5. Additional Context
- Environment details included
- Documentation updates noted
- Clear guidelines for reviewers

## Common Mistakes This Example Avoids

1. ❌ Vague descriptions
2. ❌ Missing test information
3. ❌ No screenshots
4. ❌ Incomplete checklist
5. ❌ No context for reviewers

## How to Use This Example

1. Use it as a template for your own PRs
2. Adapt the sections to your changes
3. Include similar level of detail
4. Add relevant screenshots
5. Check all items in the checklist 