#!/bin/sh

cd /home/ubuntu/LeisureBites-Backend
source venv/bin/activate
uvicorn app.main:app --workers=1
