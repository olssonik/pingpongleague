#!/bin/bash

git add -- game_database.db

git commit -m "automaticall db update"

git push

ssh ubuntu@51.195.255.193 <<'EOF'

 screen -S api -X stuff "^C"

 sleep 2

 screen -S api -X stuff "git restore . && git pull && gunicorn -w 4 -b 0.0.0.0:3000 main:app\n"

 screen -S api -X stuff "^A^D"

 exit
 EOF
