#!/usr/bin/env bash

nvm use 6.0.0


function run() {
    tmux select-pane -t $1
    tmux send-keys "$2" C-m
}

if [[ $TMUX ]]; then
    tmux set-option -g mouse on

    tmux new-window
    tmux splitw -v -p 50
    tmux select-pane -t 0
    tmux bind q kill-session

    run 0 "./manage.py runserver 127.0.0.1:8001"
    run 1 "NODE_ENV=development npm start"
else
  tmux new-session $0
fi