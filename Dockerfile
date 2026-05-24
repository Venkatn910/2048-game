FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install flask flask-socketio eventlet
EXPOSE 5050
CMD ["python3", "app.py"]
