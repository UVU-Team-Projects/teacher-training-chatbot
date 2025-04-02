# Templates Directory Guide

This directory contains all HTML templates and UI components for the Utah Elementary Teacher Training Assistant (UTAH-TTA). It follows a modular structure for maintainable and reusable frontend components.

## 📋 Table of Contents
- [Directory Structure](#directory-structure)
- [Layout Templates](#layout-templates)
- [Component Templates](#component-templates)
- [Page Templates](#page-templates)
- [Email Templates](#email-templates)
- [Development Guidelines](#development-guidelines)

## Directory Structure

```
templates/
├── layouts/                    # Base layout templates
│   ├── base.html             # Main layout template
│   ├── auth.html            # Authentication layout
│   └── error.html           # Error page layout
│
├── components/                 # Reusable components
│   ├── chat/                # Chat components
│   │   ├── message.html    # Message bubble
│   │   ├── input.html     # Chat input
│   │   └── feedback.html  # Feedback display
│   │
│   ├── navigation/          # Navigation components
│   │   ├── header.html    # Header navigation
│   │   ├── sidebar.html   # Sidebar navigation
│   │   └── footer.html    # Footer content
│   │
│   └── forms/               # Form components
│       ├── login.html      # Login form
│       └── feedback.html   # Feedback form
│
├── pages/                     # Page templates
│   ├── dashboard.html        # Dashboard page
│   ├── scenarios.html       # Scenarios list
│   ├── practice.html        # Practice session
│   └── profile.html         # User profile
│
├── emails/                    # Email templates
│   ├── welcome.html         # Welcome email
│   ├── feedback.html        # Feedback email
│   └── report.html          # Progress report
│
└── macros/                    # Jinja2 macros
    ├── forms.html           # Form macros
    ├── alerts.html         # Alert macros
    └── utils.html          # Utility macros
```

## Layout Templates

### Base Layout (`layouts/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    {% block head %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}UTAH-TTA{% endblock %}</title>
    {% endblock %}
</head>
<body>
    {% include 'components/navigation/header.html' %}
    <main>
        {% block content %}{% endblock %}
    </main>
    {% include 'components/navigation/footer.html' %}
</body>
</html>
```

## Component Templates

### Chat Components
- **Message Bubble** (`components/chat/message.html`)
  ```html
  <div class="message {% if is_user %}user{% else %}bot{% endif %}">
      <div class="message-content">{{ content }}</div>
      <div class="message-time">{{ timestamp }}</div>
  </div>
  ```

### Navigation Components
- **Header** (`components/navigation/header.html`)
- **Sidebar** (`components/navigation/sidebar.html`)
- **Footer** (`components/navigation/footer.html`)

### Form Components
- **Login Form** (`components/forms/login.html`)
- **Feedback Form** (`components/forms/feedback.html`)

## Page Templates

### Dashboard (`pages/dashboard.html`)
```html
{% extends "layouts/base.html" %}

{% block content %}
<div class="dashboard">
    <h1>Welcome, {{ user.name }}</h1>
    <div class="stats">{% include "components/dashboard/stats.html" %}</div>
    <div class="recent">{% include "components/dashboard/recent.html" %}</div>
</div>
{% endblock %}
```

## Email Templates

### Welcome Email (`emails/welcome.html`)
```html
{% extends "layouts/email.html" %}

{% block content %}
<h1>Welcome to UTAH-TTA</h1>
<p>Dear {{ user.name }},</p>
<p>Welcome to the Utah Elementary Teacher Training Assistant...</p>
{% endblock %}
```

## Development Guidelines

### Template Structure
1. **Extend Base Templates**
   ```html
   {% extends "layouts/base.html" %}
   ```

2. **Use Blocks**
   ```html
   {% block content %}
   <!-- Content here -->
   {% endblock %}
   ```

3. **Include Components**
   ```html
   {% include "components/navigation/header.html" %}
   ```

### Best Practices

1. **Component Organization**
   - Keep components modular
   - Use meaningful names
   - Document dependencies
   - Maintain consistency

2. **Styling**
   - Use CSS classes
   - Avoid inline styles
   - Follow BEM naming
   - Maintain responsiveness

3. **JavaScript**
   - Use data attributes
   - Keep scripts modular
   - Handle errors gracefully
   - Document interactions

4. **Accessibility**
   - Add ARIA labels
   - Use semantic HTML
   - Ensure keyboard navigation
   - Test with screen readers

## Template Macros

### Form Macros (`macros/forms.html`)
```html
{% macro input(name, label, type="text", required=false) %}
<div class="form-group">
    <label for="{{ name }}">{{ label }}</label>
    <input type="{{ type }}" id="{{ name }}" name="{{ name }}"
           {% if required %}required{% endif %}>
</div>
{% endmacro %}
```

## Additional Resources

- [Frontend Guide](../docs/technical/frontend_guide.md)
- [Style Guide](../docs/technical/style_guide.md)
- [Component Library](../docs/technical/components.md)
- [Accessibility Guide](../docs/technical/accessibility.md)

## Support

For template-related issues:
1. Check component documentation
2. Review style guide
3. Contact frontend team
4. Create template-related issues 