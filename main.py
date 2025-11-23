# main.py
from threading import Thread
from bot import run as run_bot
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Discord bot is running!", 200

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
