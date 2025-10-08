#!/bin/bash
# shutdown.sh - Stop all frontend and backend processes running on common dev ports

# Define ports (customize if needed)
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Find and kill processes on backend port
BACKEND_PIDS=$(lsof -ti tcp:$BACKEND_PORT)
if [ -n "$BACKEND_PIDS" ]; then
  echo "Stopping backend processes on port $BACKEND_PORT: $BACKEND_PIDS"
  kill $BACKEND_PIDS
else
  echo "No backend process found on port $BACKEND_PORT."
fi

# Find and kill processes on frontend port
FRONTEND_PIDS=$(lsof -ti tcp:$FRONTEND_PORT)
if [ -n "$FRONTEND_PIDS" ]; then
  echo "Stopping frontend processes on port $FRONTEND_PORT: $FRONTEND_PIDS"
  kill $FRONTEND_PIDS
else
  echo "No frontend process found on port $FRONTEND_PORT."
fi

echo "Shutdown complete."
