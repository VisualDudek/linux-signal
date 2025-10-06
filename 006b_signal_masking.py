import signal
import time
import threading
import os

# Solution 2: Using thread references and join()
COORDINATED_SIGNALS = {signal.SIGINT, signal.SIGTERM}

def signal_waiter_thread(worker_thread_ref):
    """This thread waits for blocked signals and runs cleanup."""
    print(f"\n[HANDLER THREAD] Waiting for signals: {COORDINATED_SIGNALS}")
    
    signum = signal.sigwait(COORDINATED_SIGNALS)
    print(f"\n[HANDLER] Received coordinated signal {signum}. Initiating cleanup...")
    
    # --- WAIT FOR CRITICAL TASK USING join() ---
    print("[HANDLER] Waiting for critical task to complete...")
    worker_thread_ref.join()  # Wait for worker thread to finish
    print("[HANDLER] Critical task completed. Proceeding with cleanup.")
    
    print("--- Safely running critical cleanup (5s) ---")
    time.sleep(5)
    print("--- Cleanup complete. Forcing process exit.")
    os._exit(0)

def critical_task_thread():
    """This thread runs the main application logic."""
    print("[WORKER THREAD] Running critical task...")
    i = 0
    while True:
        i += 1
        print(f"Worker running... ({i})")
        time.sleep(1)
        if i >= 10: 
            print("Worker finished naturally.")
            break
            
if __name__ == '__main__':
    signal.pthread_sigmask(signal.SIG_BLOCK, COORDINATED_SIGNALS)
    print(f"Main thread blocked {COORDINATED_SIGNALS}. Signals are now held.")
    
    worker_thread = threading.Thread(target=critical_task_thread)
    # Pass worker thread reference to handler
    handler_thread = threading.Thread(target=signal_waiter_thread, args=(worker_thread,))
    
    handler_thread.start()
    worker_thread.start()
    
    worker_thread.join()
    print("\nProgram finished naturally (worker completed).")