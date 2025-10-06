


## pytania/zagadnienia
- jaka jest różnica pomiędzy legacy signals aka standard signals vs. real-time signals? -> user-defined oraz queued



## AAA
- PoC dlaczego "standard signals" miały drobne wady, **001** brak "queueing mechanism" 
send rapidly 3 signals:
```bash
kill -SIGUSR1 <PID>
```