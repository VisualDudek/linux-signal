#!/bin/bash

echo "Bash PID: $$"
echo "Bash PGID: $(ps -o pgid= -p $$)"
echo "About to execute sleep..."
# "strace -f -e trace=fork,vfork,clone,execve,setpgid ./011_ask_agent.sh"
# "OR"
# "strace -f -e trace=fork,vfork,clone,execve,setpgid -o strace_output.txt ./011_ask_agent.sh"

sleep 5

echo "Sleep finished"