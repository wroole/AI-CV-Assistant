# AI CV Assistant Frontend

A React (Vite) frontend for the AI CV Assistant backend. It includes user
authentication, a CV analysis workspace (Candidate + HR modes), and a
subscription page with a simulated purchase flow.

## Prerequisites

- Node.js (>=16) and npm
- The backend API running (see the backend README for setup)

## Installation

```bash
cd frontend
npm install
```

## Configuration

The frontend proxies `/api` requests to `http://localhost:8000` (the default
backend URL) during development. If your backend runs elsewhere, update
`vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'YOUR_BACKEND_URL',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

## Development

```bash
npm run dev
```

The app is available at `http://localhost:5173`.

## Building for Production

```bash
npm run build
```

The output is in the `dist` directory.

## Architecture

- **Routing**: `react-router-dom` v6. `/login` and `/register` are public;
  `/` (analyze) and `/subscription` are protected by `ProtectedRoute`, which
  redirects unauthenticated users to `/login` while remembering their
  destination.
- **Auth**: `AuthContext` (`src/context/AuthContext.jsx`) owns the current
  user. On first load it hydrates the session from stored tokens (with a
  single refresh attempt on an expired access token). Login/register store
  access + refresh JWTs in `localStorage`.
- **API client**: `src/api/index.js` attaches the bearer token to every
  request and transparently refreshes it on a `401` (exactly once, then logs
  out). All app requests go through `apiGet` / `apiPostForm` so the token is
  always attached.

## Features

- **Authentication**: register, login, logout, protected routes.
- **Candidate Mode**: upload a CV (PDF) for an analysis (score, strengths,
  weaknesses, recommendations).
- **HR Mode**: upload a CV (PDF) and a job description (text, URL, or PDF) for
  a candidate-fit analysis.
- **Subscription**: view plans and the current subscription. A "Simulate
  purchase" button grants a plan with no real payment processing.
- Loading states, error handling, and a responsive design.

## Backend Integration

The frontend uses these endpoints:

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/v1/auth/register` | public | create account, returns tokens |
| `POST /api/v1/auth/login` | public | sign in, returns tokens |
| `POST /api/v1/auth/refresh` | public | refresh the token pair |
| `GET  /api/v1/auth/me` | required | current user |
| `POST /api/v1/analyze-resume` | required | Candidate CV analysis |
| `POST /api/v1/hr/analyze-candidate` | required | HR candidate analysis |
| `GET  /api/v1/subscriptions/plans` | public | plan catalog |
| `GET  /api/v1/subscriptions/me` | required | current subscription |
| `POST /api/v1/subscriptions/subscribe` | required | simulate purchase |
| `POST /api/v1/subscriptions/cancel` | required | cancel subscription |

## Troubleshooting

- If API calls fail with `401`, sign in — the analysis endpoints now require
  authentication.
- If you see CORS errors, ensure the backend CORS middleware includes the
  frontend origin (`http://localhost:5173`).
- For file upload issues, verify the file is a PDF and within the 10 MB limit.

## Notes

- Vite for development builds, plain CSS for styling (no UI framework).
- React hooks for state; `react-router-dom` for navigation.
