# Thought Box - MkDocs Material Site

This is my personal blog migrated from Jekyll to MkDocs Material.

## Running locally

1. Set up Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Serve the site:
```bash
mkdocs serve
```

The site will be available at http://127.0.0.1:8000

## Building for production

```bash
mkdocs build
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the master branch.

## Features

- ✅ All 36 original posts migrated
- ✅ LaTeX math rendering with MathJax
- ✅ Material Design theme
- ✅ Search functionality
- ✅ Mobile responsive
- ✅ Custom domain support (blog.jnbrymn.com)
