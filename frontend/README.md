# ReComposer Frontend

Static HTML/CSS/JavaScript frontend for ReComposer SaaS application.

## Quick Start

### Option 1: Using npm (requires Node.js)

```bash
npm install
npm run dev
```

This will start a local server at `http://localhost:3000` and open it in your browser.

### Option 2: Using Python (no Node.js needed)

```bash
# Python 3
python -m http.server 3000

# Then open http://localhost:3000 in your browser
```

### Option 3: Using VS Code Live Server Extension

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### Option 4: Direct File Access

You can also open `index.html` directly in your browser, but note:
- API calls may fail due to CORS if backend CORS_ORIGINS doesn't include `file://`
- Some features may not work without a proper HTTP server

## Backend Connection

The frontend connects to the backend API at `http://localhost:8000`.

**Important:** Make sure your backend is running and CORS is configured:

1. Start the backend server (see `recompose_backend/README.md`)
2. Set `CORS_ORIGINS` environment variable in backend to include your frontend URL:
   - For npm/http-server: `CORS_ORIGINS=http://localhost:3000`
   - For Python server: `CORS_ORIGINS=http://localhost:3000`
   - For Live Server: Check the port Live Server uses and add it

## Project Structure

```
frontend/
├── index.html          # Landing page
├── login.html          # Login page
├── signup.html         # Signup page
├── dashboard.html      # Dashboard page
├── css/
│   └── styles.css      # All styles
└── js/
    ├── api.js          # API client
    ├── auth.js         # Authentication utilities
    ├── utils.js        # Utility functions
    └── dashboard.js    # Dashboard functionality
```

## Features

- Landing page with pricing, testimonials, FAQ
- Authentication (login/signup)
- Email Assistant with AI rewriting
- Contacts management
- Campaign management
- Responsive design
- Full accessibility (ARIA labels)

## Development

The frontend is pure HTML/CSS/JavaScript - no build process required. Just edit the files and refresh your browser.

