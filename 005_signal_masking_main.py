import signal
import time
import sys

CRITICAL_SIGNAL = signal.SIGINT
BLOCKED_SIGNALS = {CRITICAL_SIGNAL}

def main_program():
    print(f"Main Thread PID: {sys.argv[0]}...")
    print(f"Press Ctrl+C NOW (it will EXIT) - Signal is UNBLOCKED.")
    time.sleep(2)

    # --- CRITICAL SECTION START ---
    print("\n[CRITICAL SECTION START]")
    print(f"Blocking {CRITICAL_SIGNAL} for 5 seconds...")
    
    # Block SIGINT in the current thread (the main thread)
    signal.pthread_sigmask(signal.SIG_BLOCK, BLOCKED_SIGNALS)
    
    try:
        # If you press Ctrl+C now, the signal will remain PENDING
        print("--- Modifying sensitive data... (5 seconds)")
        time.sleep(5)
        print("--- Sensitive data modification complete.")
        
    finally:
        # Unblock the signal. If Ctrl+C was pressed, it is delivered NOW.
        print(f"[CRITICAL SECTION END] Unblocking {CRITICAL_SIGNAL}...")
        signal.pthread_sigmask(signal.SIG_UNBLOCK, BLOCKED_SIGNALS)
    # --- CRITICAL SECTION END ---

    print("Program finished gracefully after critical section.")
    time.sleep(1) 

if __name__ == "__main__":
    try:
        main_program()
    except KeyboardInterrupt:
        print("\n*Program EXIT due to PENDING SIGINT delivery*")

# The only difference in this code is that it is all synchronous in the main thread.
# This ensures the pthread_sigmask call controls the only thread receiving the signal.