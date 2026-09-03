#!/bin/bash
# Run DRISHTI-X MVP locally without Docker

echo "Starting DRISHTI-X Backend (Port 8000)..."
cd backend-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Starting DRISHTI-X Frontend (Port 3000)..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "DRISHTI-X is running! Access the dashboard at http://localhost:3000"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
