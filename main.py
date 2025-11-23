from flask import Flask
from bot import run
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run_flask():
    # Bind to 0.0.0.0 and use Render's PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Run Flask in a background thread
    threading.Thread(target=run_flask).start()

    # Start Discord bot
    run()
