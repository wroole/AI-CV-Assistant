# AI CV Assistant

A backend service that analyzes CVs (PDFs) using LLMs and provides deterministic scoring. Includes a React frontend for two modes: Candidate and HR.

## Project Structure

- `app/` - Backend FastAPI application
- `frontend/` - React frontend (Vite)

## Backend

### Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set up environment variables (copy `.env.example` to `.env` and adjust):
   ```bash
   cp .env.example .env
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### API Endpoints

- `POST /api/v1/analyze-resume` - Analyze a CV for candidates
- `POST /api/v1/hr/analyze-candidate` - Analyze a CV against a job description for HR
- `GET /health` - Health check

### Features

- PDF text extraction (PyMuPDF)
- Text cleaning
- LLM analysis (Ollama or OpenAI API)
- Deterministic scoring (sections, bullet points, achievements)
- Basic error handling and validation

## Frontend

### Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

### Features

- Two modes: Candidate and HR
- File upload (PDF only)
- Provider selection (Local Ollama or OpenAI API)
- Loading states)
- Display of LLM analysis and deterministic scores
- Error handling and responsive design

### Building for Production

```bash
npm run build
```
The output will be in the `dist` folder.

## Running Both

1. Start the backend (as described above).
2. In a new terminal, start the frontend (as described above).
3. Access the frontend at `http://localhost:5173` - it will proxy API requests to the backend.

## Notes

- The backend includes CORS middleware to allow the frontend dev server (default Vite port 5173).
- The frontend is configured to proxy `/api` requests to `http://localhost:8000` during development.
- For production, you can build the frontend and serve it via the backend or a separate web server.

## License

MIT

## Acknowledgements

- Built with FastAPI, React, Vite, and Ollama/OpenAI.