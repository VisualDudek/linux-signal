#!/bin/bash

# Define the trap handler function
function resize_handler() {
    echo -e "\n--- SIGWINCH RECEIVED! Redrawing interface... ---"
    # The 'stty size' command retrieves the new dimensions from the kernel
    echo "New Dimensions: Rows $(tput lines), Columns $(tput cols)"
}

# Trap the SIGWINCH signal (Signal 28)
trap 'resize_handler' SIGWINCH

echo "Waiting for terminal resize (SIGWINCH)..."
echo "My PID is: $$"

# Loop indefinitely to keep the script running
while true; do
    # PLAY WITH THIS
    sleep 1
done