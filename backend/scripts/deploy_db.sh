#!/bin/bash

ssh your_user@your_server <<'EOF'

screen -S api -X stuff "^C"

sleep 1

screen -S api -X stuff "git restore . && git pull && gunicorn -w 4 -b 0.0.0.0:3000 main:app\n"

screen -S api -X stuff "^A^D"

exit
EOF
