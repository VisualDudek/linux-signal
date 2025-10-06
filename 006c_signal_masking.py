import signal
import time
import threading
import os

# Solution 3: Using a shared state variable with Lock
COORDINATED_SIGNALS = {signal.SIGINT, signal.SIGTERM}

class SharedState:
    def __init__(self):
        self.critical_task_running = True
        self.lock = threading.Lock()
    
    def mark_task_finished(self):
        with self.lock:
            self.critical_task_running = False
    
    def is_task_running(self):
        with self.lock:
            return self.critical_task_running

shared_state = SharedState()

def signal_waiter_thread():
    """This thread waits for blocked signals and runs cleanup."""
    print(f"\n[HANDLER THREAD] Waiting for signals: {COORDINATED_SIGNALS}")
    
    signum = signal.sigwait(COORDINATED_SIGNALS)
    print(f"\n[HANDLER] Received coordinated signal {signum}. Initiating cleanup...")
    
    # --- WAIT FOR CRITICAL TASK USING POLLING ---
    print("[HANDLER] Waiting for critical task to complete...")
    while shared_state.is_task_running():
        time.sleep(0.1)  # Check every 100ms
    print("[HANDLER] Critical task completed. Proceeding with cleanup.")
    
    print("--- Safely running critical cleanup (5s) ---")
    time.sleep(5)
    print("--- Cleanup complete. Forcing process exit.")
    os._exit(0)

def critical_task_thread():
    """This thread runs the main application logic."""
    print("[WORKER THREAD] Running critical task...")
    try:
        i = 0
        while True:
            i += 1
            print(f"Worker running... ({i})")
            time.sleep(1)
            if i >= 10: 
                print("Worker finished naturally.")
                break
    finally:
        shared_state.mark_task_finished()
        print("[WORKER THREAD] Marked task as finished.")
            
if __name__ == '__main__':
    signal.pthread_sigmask(signal.SIG_BLOCK, COORDINATED_SIGNALS)
    print(f"Main thread blocked {COORDINATED_SIGNALS}. Signals are now held.")
    
    handler_thread = threading.Thread(target=signal_waiter_thread)
    worker_thread = threading.Thread(target=critical_task_thread)
    
    handler_thread.start()
    worker_thread.start()
    
    worker_thread.join()
    print("\nProgram finished naturally (worker completed).")