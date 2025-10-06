


## pytania/zagadnienia
- jaka jest różnica pomiędzy legacy signals aka standard signals vs. real-time signals? -> user-defined oraz queued
- na podstawie `man 2 signal` co ot jest `sigaction(2)`?
- src: `man 2 signal` in a multithreaded process the effects of `signal()` are unspecified.
- `sigqueue(3)` jest library call a nie system call, jaka jest róznica?
- bash and python don't expose the RT-signal payload -> they implement only "legacy signal", no easy way to read complex C-level data structure `siginfo_t` that the kernel uses to deliver the payload.
- python signal lib. handler function accepts two args. `(signum, frame)` what is frame?
- GOTCHA `struct sigaction` dopuszcza simple signal handler "?legacy" aka "sa_handler" oraz advanced signal handler aka "sa_sigaction", implementujesz jeden!
- signal masking, ciekawe że to nie jest feature RT a legacy signals.
- ? common pattern to run critical task in a thread, with signal masking
- "signal delivery to threads" vs. "process" -> "Ctrl+C" targets the process group, ??? kernel chooses a thread, kernel needs to deliver signal to one thread in the process, it chooses a thread where the signal is not currently blocked.
- Czy to że praktyką jest uruchamienie krytycznych tasków w nowym wątku w przypadku Pythona to strzał w kolano z powodu implementacji cpython "interpretera/run-time" który dostając ctrl-c do gółłwnego wątku odpala "shutdown" i jedzie po wszystkich wątkach?



## AAA
- PoC dlaczego "standard signals" miały drobne wady, **001** brak "queueing mechanism" 
send rapidly 3 signals:
```bash
kill -SIGUSR1 <PID>
```
- PoC send RT payload, using `sigaction` and `siggueue` **002**, **003**
```sh
gcc 002_sig_rt_rec.c -o receiver
gcc 003_sig_rt_sender.c -o sender
./receiver
./sender <PID>
```
- ^^^ widze że paload jest union type, co ułatwia transfer danych.
- ^^^ "arrow operator" or "structure pointer operator" access members of a strucutre through a pointer.
```c
struct sigaction {
    void (*sa_handler)(int);                    // Simple signal handler (one argument)
    void (*sa_sigaction)(int, siginfo_t*, void*); // Advanced signal handler (three arguments)
    sigset_t sa_mask;                          // Signals to block during handler execution
    int sa_flags;                              // Behavior modification flags
    void (*sa_restorer)(void);                 // Usually not used (internal)
};
```
- **004** duży niuans "signal delivery to threads" vs. "process"
- **005** signal masking działa na głównym wątku.
- **006** workaround ^^^, eeee dalej nie zapobiega w 100% dokończenie critical task