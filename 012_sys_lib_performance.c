// performance_test.c
#include <stdio.h>
#include <unistd.h>
#include <time.h>

#define ITERATIONS 1000000

int main() {
    clock_t start, end;
    double syscall_time, library_time;
    
    printf("Running performance tests with %d iterations...\n", ITERATIONS);
    printf("Testing in progress");
    fflush(stdout);
    
    // Test 1: System call (write)
    start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        write(STDOUT_FILENO, "X", 1);  // System call each time!
    }
    end = clock();
    syscall_time = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("\nTesting library calls");
    fflush(stdout);
    
    // Test 2: Library call (putchar with buffering)
    start = clock();
    for (int i = 0; i < ITERATIONS; i++) {
        putchar('X');  // Buffered - fewer syscalls!
    }
    end = clock();
    library_time = (double)(end - start) / CLOCKS_PER_SEC;
    
    // Print all results at the end
    printf("\n\n=== PERFORMANCE RESULTS ===\n");
    printf("Iterations: %d\n", ITERATIONS);
    printf("write() syscall:    %.3f seconds\n", syscall_time);
    printf("putchar() library:  %.3f seconds\n", library_time);
    printf("Speedup ratio:      %.1fx faster\n", syscall_time / library_time);
    printf("==========================\n");
    
    return 0;
}