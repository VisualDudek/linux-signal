#!/bin/bash

HANDLER_COUNT=0
# A slow handler function designed to take 3 seconds
function signal_handler() {
    HANDLER_COUNT=$((HANDLER_COUNT + 1))
    echo -e "\n--- [HANDLER START] Signal received. Total handled: $HANDLER_COUNT. Sleeping 3s..."
    sleep 3 
    echo "--- [HANDLER END] Finished handling."
}

# Trap SIGUSR1 (Signal 10) to call our function
trap 'signal_handler' SIGUSR1

echo "My PID is: $$" # $$ is the PID of the current shell script

for i in {1..10}; do
    echo "Main loop running ($i)..."
    sleep 1
done

echo "Script finished. Handled $HANDLER_COUNT signals."