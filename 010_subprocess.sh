#! /bin/bash

echo "Script PID: $$"

# Set up signal handler for SIGWINCH in the script
trap 'echo "Script received SIGWINCH (window resize)"' WINCH

# Start sleep in background and get its PID
sleep 30 &
SLEEP_PID=$!
echo "Sleep PID: $SLEEP_PID"

# Check process groups
echo "Script PGID: $(ps -o pgid= -p $$)"
echo "Sleep PGID: $(ps -o pgid= -p $SLEEP_PID)"

echo "Now resize your terminal window to test SIGWINCH..."
echo "The script should receive SIGWINCH, but sleep won't."

# Wait for sleep to finish
wait $SLEEP_PID
echo "Sleep completed."