#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install werkzeug==2.0.1
pip install flask==2.0.1
pip install flask-cors==3.0.10
pip install numpy
pip install scikit-learn
pip install python-dotenv==0.19.0
pip install openai==0.27.8
pip install gunicorn==20.1.0
pip install -r requirements.txt 