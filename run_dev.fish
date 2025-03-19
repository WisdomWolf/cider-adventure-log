#!/usr/bin/env fish
if test -z "$TMUX"
    set operation new-session
else
    set operation new-window
end
tmux $operation "./flask_run.sh; read" \; \
split-window "cd frontend; npm run dev; read" \; \
select-layout even-horizontal