import signal
import time
import threading
import os # Used for os._exit to force closure after cleanup

# The signals we want to catch and handle safely
COORDINATED_SIGNALS = {signal.SIGINT, signal.SIGTERM} 

def signal_waiter_thread():
    """This thread waits for blocked signals and runs cleanup."""
    print(f"\n[HANDLER THREAD] Waiting for signals: {COORDINATED_SIGNALS}")
    
    # sigwait pauses this thread until one of the blocked signals arrives.
    signum = signal.sigwait(COORDINATED_SIGNALS)
    
    # When sigwait returns, we know the signal was safely caught and delivered.
    print(f"\n[HANDLER] Received coordinated signal {signum}. Initiating cleanup...")
    
    # --- CRITICAL CLEANUP TASK ---
    print("--- Safely running critical cleanup (5s) ---")
    time.sleep(5)
    print("--- Cleanup complete. Forcing process exit.")
    # Use os._exit(0) to exit the process without waiting for other threads
    os._exit(0) 

def critical_task_thread():
    """This thread runs the main application logic."""
    print("[WORKER THREAD] Running critical task...")
    i = 0
    while True:
        i += 1
        print(f"Worker running... ({i})")
        time.sleep(1)
        # Added a natural exit condition for testing purposes
        if i >= 10: 
            print("Worker finished naturally.")
            break
            
if __name__ == '__main__':
    # --- CRITICAL STEP 1: BLOCK signals in the main thread MASK ---
    # This MUST be the first thing the main thread does. It blocks these signals 
    # across the entire process group *before* worker threads inherit the mask.
    signal.pthread_sigmask(signal.SIG_BLOCK, COORDINATED_SIGNALS)
    print(f"Main thread blocked {COORDINATED_SIGNALS}. Signals are now held.")
    
    # --- CRITICAL STEP 2 & 3: Start the dedicated handler and the worker ---
    handler_thread = threading.Thread(target=signal_waiter_thread)
    worker_thread = threading.Thread(target=critical_task_thread)
    
    handler_thread.start()
    worker_thread.start()
    
    # The main thread waits for the worker to finish
    worker_thread.join()
    
    print("\nProgram finished naturally (worker completed).")
    # If the worker finishes naturally, the program can exit without the handler's help