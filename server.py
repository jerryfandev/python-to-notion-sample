from flask import Flask, jsonify
from threading import Thread
from notion_bot import check_notion

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Notion bot is running"}), 200

def main():
    response_prefix = "BOT: "  # Customize as needed
    message_prefix = "Hey BOT"  # Customize as needed

    # Start polling Notion in a background thread
    thread = Thread(target=check_notion, args=(response_prefix, message_prefix))
    thread.daemon = True
    thread.start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5080)

if __name__ == "__main__":
    main()
