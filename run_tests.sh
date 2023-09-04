#!/bin/bash
# Run with: chmod +x ./run_tests.sh && ./run_tests.sh

python3 -m src.server &
FLASK_PID=$!
python3 -m pytest $1
kill $FLASK_PID
rm data.db

