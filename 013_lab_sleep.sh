#!/bin/bash
echo "Script PID: $$"

strace -f -e trace=signal,fork,vfork,clone,execve,setpgid bash <<EOF
echo "Bash PID: $$"
# echo "Bash PGID: $(ps -o pgid= -p $$)"
sleep 15
EOF

