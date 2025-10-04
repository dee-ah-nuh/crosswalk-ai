#!/bin/bash
# Script to start both backend and frontend in parallel

# Start backend (using project venv and uvicorn)
cd backend
../crosswalk/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Backend started with PID $BACKEND_PID. Logs: backend.log"

# Start frontend
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Frontend started with PID $FRONTEND_PID. Logs: frontend.log"

echo "Both servers are running in the background. Use 'tail -f backend.log' or 'tail -f frontend.log' to view logs."
