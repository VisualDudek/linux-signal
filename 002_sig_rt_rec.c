#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

// Use the minimum available Real-Time signal
#define RT_SIGNAL SIGRTMIN

// --- Signal Handler Function ---
// The handler must accept three arguments to access the siginfo_t structure
void rt_handler(int sig, siginfo_t *info, void *ucontext) {
    printf("\n[Receiver Handler] Signal %d received.\n", sig);

    // CRITICAL STEP: Access the integer payload via the si_value union
    int received_value = info->si_value.sival_int;
    
    printf("[Receiver Handler] Received Payload Data (si_value): %d\n", received_value);
    
    // Exit after handling the signal
    exit(0);
}

int main() {
    struct sigaction sa;

    // 1. Get PID and display it
    pid_t pid = getpid();
    printf("Receiver started. PID: %d\n", pid);
    printf("Waiting for RT signal (%d)... \n", RT_SIGNAL);

    // 2. Configure the sigaction structure
    sa.sa_sigaction = rt_handler;      // Use the three-argument handler function
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_SIGINFO;          // <-- CRUCIAL FLAG: Tells the kernel to populate the siginfo_t structure

    // 3. Register the handler for the RT_SIGNAL
    if (sigaction(RT_SIGNAL, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    // Pause the process until a signal is received
    // This process will wait indefinitely until RT_SIGNAL is received and handled.
    pause(); 
    
    // Should never reach here if handler calls exit(0)
    return 0;
}