# AI CV Assistant Frontend

This is a React frontend for the AI CV Assistant backend. It provides two modes:
1. **Candidate Mode**: Upload a CV (PDF) to get an analysis (score, strengths, weaknesses, recommendations, etc.)
2. **HR Mode**: Upload a CV (PDF) and provide a job description to get a match analysis.

## Prerequisites

- Node.js (>=16) and npm (or yarn)
- The backend API running (see backend README for setup)

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (the default backend URL) during development.
If your backend runs on a different URL, update `vite.config.js`:

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

Start the development server:
```bash
npm run dev
```
The app will be available at `http://localhost:5173`.

## Building for Production

To create a production build:
```bash
npm run build
```
The output will be in the `dist` directory.

## Usage

1. Ensure the backend is running (default: `http://localhost:8000`).
2. Start the frontend dev server (`npm run dev`).
3. Open `http://localhost:5173` in your browser.
4. Choose between Candidate Mode and HR Mode.
5. Upload a PDF CV (and for HR mode, provide a job description).
6. Click the analyze button and view the results.

## Features

- File validation (PDF only, size limit handled by backend)
- Loading states
- Error handling
- Display of LLM analysis and deterministic basic scores
- Responsive design

## Notes

- The frontend uses Vite for fast development builds.
- It uses React hooks for state management.
- Styling is done with plain CSS for simplicity.

## Backend Integration

The frontend communicates with the following endpoints:
- `POST /api/v1/analyze-resume` (Candidate Mode)
- `POST /api/v1/hr/analyze-candidate` (HR Mode)

Make sure the backend is running and accessible from the frontend (CORS is configured in the backend).

## Troubleshooting

- If you see CORS errors, ensure the backend CORS middleware includes the frontend origin.
- If the API calls fail, check the browser console and backend logs.
- For file upload issues, verify the file is a PDF and within the size limit set in the backend.

Enjoy using the AI CV Assistant!