#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

#define RT_SIGNAL SIGRTMIN

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <receiver_PID>\n", argv[0]);
        return 1;
    }

    pid_t receiver_pid = (pid_t)atoi(argv[1]);
    union sigval value;
    
    // The data we want to send
    const int DATA_PAYLOAD = 42; 

    // CRITICAL STEP: Set the union member
    value.sival_int = DATA_PAYLOAD;

    printf("Sender running. Target PID: %d\n", receiver_pid);
    printf("Sending RT signal %d with payload: %d\n", RT_SIGNAL, DATA_PAYLOAD);

    // sigqueue() sends the signal with the specified value (payload)
    if (sigqueue(receiver_pid, RT_SIGNAL, value) == -1) {
        perror("sigqueue failed");
        return 2;
    }

    printf("Signal successfully sent.\n");
    return 0;
}