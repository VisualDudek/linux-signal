// test_background_sigwinch.c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <termios.h>

void sigwinch_handler(int sig) {
    char msg[] = "Received SIGWINCH\n";
    write(STDOUT_FILENO, msg, sizeof(msg)-1);
}

int main() {
    signal(SIGWINCH, sigwinch_handler);
    
    pid_t my_pgid = getpgrp();
    pid_t fg_pgid = tcgetpgrp(STDIN_FILENO);
    
    printf("My PGID: %d\n", my_pgid);
    printf("Terminal foreground PGID: %d\n", fg_pgid);
    
    if (my_pgid == fg_pgid) {
        printf("I am in FOREGROUND - will receive SIGWINCH\n");
    } else {
        printf("I am in BACKGROUND - will NOT receive SIGWINCH\n");
    }
    
    printf("Resize terminal now...\n");
    sleep(60);
    return 0;
}