#!/bin/sh

if [ "$FLASK_ENV" = "development" ]; then
  export FLASK_APP=api/app.py
  export FLASK_DEBUG=1
  flask run --host '0.0.0.0' --port 5000
else
  gunicorn api.app:app -b 0.0.0.0:5000 -w 4
fi