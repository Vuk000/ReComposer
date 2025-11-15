# ReCompose Frontend - React + TypeScript + Tailwind

Modern React frontend for ReCompose AI, built with the Violet Bloom design system.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** with Violet Bloom design system
- **React Router** for routing
- **Axios** for API calls
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd frontend-react
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Environment Variables

Create a `.env` file:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── ui/          # Reusable UI components (Button, Card, Input, etc.)
│   ├── layout/      # Layout components (Navbar, Sidebar, AppLayout)
│   ├── auth/        # Authentication components
│   └── shared/      # Shared components (Toast, Modal)
├── pages/
│   ├── Landing.tsx  # Landing/marketing page
│   ├── auth/        # Auth pages (Signup, Login, etc.)
│   └── app/         # App pages (Dashboard, Rewrite, Campaigns, Settings)
├── hooks/           # Custom React hooks
├── lib/             # Utilities and API client
├── types/           # TypeScript type definitions
└── contexts/        # React contexts (Toast)
```

## Design System

The app uses the **Violet Bloom** design system with:
- Primary color: `#8c5cff` (purple)
- Dark theme with card backgrounds
- Rounded corners (1.4rem radius)
- Plus Jakarta Sans font family

## Features

- ✅ Landing page with hero, features, pricing
- ✅ Authentication (signup, login, password reset)
- ✅ Email rewriter with tone selection
- ✅ Campaign management (Pro plan)
- ✅ Settings and billing
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Toast notifications
- ✅ Protected routes

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default. All API calls are handled through:
- `src/lib/api.ts` - Axios instance with auth interceptors
- Custom hooks in `src/hooks/` - React hooks for API calls

## Development Notes

- The old `frontend/` directory is kept as backup
- All components are fully typed with TypeScript
- Mobile-responsive from the start
- Toast notifications use React Context

