#!/bin/sh

uvicorn api.api:app --host 0.0.0.0 --port 8000 --reload
