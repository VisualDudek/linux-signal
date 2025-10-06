import signal
import time
import threading

# Define the signal we want to block (Ctrl+C)
CRITICAL_SIGNAL = signal.SIGINT

# This set contains the signals we wish to block
BLOCKED_SIGNALS = {CRITICAL_SIGNAL}

def critical_task():
    print(f"\n[CRITICAL SECTION START] Blocking {CRITICAL_SIGNAL}...")
    
    # 1. Block the signal (add it to the process's signal mask)
    # The kernel will hold any incoming SIGINT signals until unblocked.
    signal.pthread_sigmask(signal.SIG_BLOCK, BLOCKED_SIGNALS)
    
    try:
        # Simulate a task that must not be interrupted
        print("--- Modifying sensitive data... (5 seconds)")
        time.sleep(5)
        print("--- Sensitive data modification complete.")
        
    finally:
        # 2. Unblock the signal (remove it from the signal mask)
        # Any pending SIGINT signals will be delivered immediately here.
        print(f"[CRITICAL SECTION END] Unblocking {CRITICAL_SIGNAL}...")
        signal.pthread_sigmask(signal.SIG_UNBLOCK, BLOCKED_SIGNALS)


def main():
    print("Main program started.")
    print(f"Press Ctrl+C NOW (it will be blocked) and wait 5 seconds...")

    # Run the critical task in a thread (optional, but a common pattern)
    thread = threading.Thread(target=critical_task)
    thread.start()
    thread.join()

    # The program can now run normally again
    print("\nProgram finished gracefully.")


if __name__ == "__main__":
    # Ensure SIGINT is not set to a default handler before we block it
    # We are relying on the *default* action of SIGINT if it is NOT blocked.
    main()