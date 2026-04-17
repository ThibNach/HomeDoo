#!/bin/bash

cd core/backend
poetry run python app.py &
BACKEND_PID=$!

cd ../../core/frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo "Backend running on http://127.0.0.1:5000 (PID: $BACKEND_PID)"
echo "Frontend running on http://127.0.0.1:3000 (PID: $FRONTEND_PID)"
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait