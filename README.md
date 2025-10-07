


## pytania/zagadnienia
- jaka jest różnica pomiędzy legacy signals aka standard signals vs. real-time signals? -> user-defined oraz queued
- na podstawie `man 2 signal` co ot jest `sigaction(2)`?
- src: `man 2 signal` in a multithreaded process the effects of `signal()` are unspecified.
- `sigqueue(3)` jest library call a nie system call, jaka jest róznica?
- ^^^ ciekawe co tak naprawde kryje się pod "mode switch" (user mode -> kernel mode) ???
- use `ltrace` to see lib calls.
- bash and python don't expose the RT-signal payload -> they implement only "legacy signal", no easy way to read complex C-level data structure `siginfo_t` that the kernel uses to deliver the payload.
- python signal lib. handler function accepts two args. `(signum, frame)` what is frame?
- GOTCHA `struct sigaction` dopuszcza simple signal handler "?legacy" aka "sa_handler" oraz advanced signal handler aka "sa_sigaction", implementujesz jeden!
- signal masking, ciekawe że to nie jest feature RT a legacy signals.
- ? common pattern to run critical task in a thread, with signal masking
- "signal delivery to threads" vs. "process" -> "Ctrl+C" targets the process group, ??? kernel chooses a thread, kernel needs to deliver signal to one thread in the process, it chooses a thread where the signal is not currently blocked.
- Czy to że praktyką jest uruchamienie krytycznych tasków w nowym wątku w przypadku Pythona to strzał w kolano z powodu implementacji cpython "interpretera/run-time" który dostając ctrl-c do gółłwnego wątku odpala "shutdown" i jedzie po wszystkich wątkach?
- ??? `ioctl()` `fcntl()`
- `SIGWINCH`
- GOTCHA vvv zupełnie nie tak :) poniżej są tylko półprawdy, bash implements "wait and cooperative Exit" WCE
- bash implementuje/istanluje `SIGWINCH` handler z flagą `SA_REASTART` This change was introduced in bash starting from version 4.4, where bash began installing its `SIGWINCH` signal handler with SA_RESTART to prevent it from interrupting open/read/write system calls.
- ^^^ to ciekawe co się dzieje jak Python dostanie `SIGWINCH` ? z drugiej strony to bezsensu pytanie bo `SIGWINCH` ma tylko sens jeśli jest odpalony w terminalu a jak Python jest odpalony w terminlu to rachej przez bash/zsh
- !!! coś tu się nie zgadza bo niby SIGINT też pod BSD behavior ma SA_RESTART. ???
- ciekawe że zsh explicite ustawia `SA_INTERRUP` dla SunOS 4.X
- when bash is interactive, each foreground (chyba background) job gets own process group !!! 
- tty driver, kernel sends `SIGWINCH` only to foreground group
- check `man 7 man` for default signal action and numbering
- `clone()` modern fork
- Ctrl+C (terminal generated `SIGINT`) kernel sends to entire process group BUT `kill -INT <pid>` (cmd line kill) sends only to specific PID only. BUT `kill -INT -<pid>` negative PID send to a process group. 
- `kill -INT <pid == 0>` send to all processes in current process group


## src
- @YT "Pressing CTRL+D is NOT what you think!" by Gynvael

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
- ^^^ **006a** `Event()` to coordinate between threads
- ^^^ **006b** `.join()` duży minus to konieczność przekazania referencji do worker_thread
- ^^^ **006c** Polling, wydaje mi się że tutaj minusem jest semi busy-waiting ALE chyba największy potencjał do skomplikowanych stanów aplikacji.
- **007** tu się robi naprawdę ciekawie, wygląda to tak jakby `sleep` blokowoło SIGWINCH -> implementacja bash-a !!!
- ^^^ bash source code `sig.c` pod koniec kodu:
```c
  /* Let's see if we can keep SIGWINCH from interrupting interruptible system
     calls, like open(2)/read(2)/write(2) */
#if defined (SIGWINCH)
  if (sig == SIGWINCH)
    act.sa_flags |= SA_RESTART;		/* XXX */
#endif
```
- bash workaround:
```bash
sleep 30 &    # Background
wait $!       # Builtin wait - immediately interruptible
```
- foreground process have diff. PGID, background will not rec. SIGWINCH **008**
```sh
./background_sigwinch

./background_sigwinch &
```
- run below and resize window to see that SIGWINCH is deliverd to sleep but it is ignored
```bash
strace -e signal sleep 10
```
- `kernel/drivers/tty/n_tty.c`, `kill_pgrp()` sends the signal to every process that has process PGID. It doesn't target a specific PID first.
```c
static void __isig(int sig, struct tty_struct *tty)
{
	struct pid *tty_pgrp = tty_get_pgrp(tty);
	if (tty_pgrp) {
		kill_pgrp(tty_pgrp, sig, 1);
		put_pid(tty_pgrp);
	}
}
```
- performance demonstration between syscall and libcall **012**, 
    - why using `fflush(stout)` ??? 
    - czy dobrze rozumiem że buforowanie jest tu kluczem?
    - ciekawe czy samo `stdout` też ma w sobie jakiś buffor?
    - `putchar()` has library buffer, size is typically 8KB (BUFSIZ)
    - TAKEAWAY: the magic is in batching many small operations into fewer larger system calls
- `putchar()` buffer:
    - The buffer for putchar is the output buffer inside the `stdout` FILE structure.
    - putchar writes to this buffer using internal pointers (_IO_write_base, _IO_write_ptr, _IO_write_end).
    - The buffer is allocated by glibc and managed automatically; you don't interact with it directly in user code.
- `putchar()` src code froma glibc:
```c
// glibc/libio/putchar.c
int
putchar (int c)
{
  int result;
  _IO_acquire_lock (stdout);
  result = _IO_putc_unlocked (c, stdout);
  _IO_release_lock (stdout);
  return result;
}
```
- ^^^ GOTCHA nie wiedziałem że można w C typ result fn deklarować w osobnej lini
- dla `trace=signal` to są jakieś jaja ile przechodzi sigaction oraz sigprocmask **013**
- ^^^ co tu się dzieje ??? jeśli: 
    - `kill -INT <bash pid>` nic się nie dzieje
    - `kill -TERM <bash pid>` bash jest terminowany ALE sleep dalej działa pod strace !!!