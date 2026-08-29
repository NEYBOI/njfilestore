import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Telegram View-Once Media Saver Bot is Running 24/7!'

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def start_health_check_server():
    server_thread = threading.Thread(target=run_web, daemon=True)
    server_thread.start()
