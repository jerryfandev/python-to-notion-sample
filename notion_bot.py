import re
import requests
import time

# Notion API credentials
# Configure these via environment variables or directly here for the demo
NOTION_API_KEY = "xxxxxxxxxx"  # Replace with your Notion API key or load dynamically
PAGE_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Replace with your Notion page ID, exact format
NOTION_API_URL = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

processed_messages = set()


def get_latest_text(response_prefix=None, message_prefix=None):
    if response_prefix is None or len(response_prefix) == 0:
        return None, None, None

    response = requests.get(NOTION_API_URL, headers=headers)
    data = response.json()

    if "results" in data and len(data["results"]) > 1:
        last_block = data["results"][-2]
        if last_block["type"] == "paragraph":
            text_content = last_block["paragraph"]["rich_text"]
            if text_content:
                message = text_content[0]["text"]["content"]
                if message.startswith(response_prefix):
                    return None, None, None
                else:
                    if message_prefix and message.startswith(message_prefix):
                        message = message[4:].strip()
                    next_block_index = data["results"].index(last_block) + 1
                    if next_block_index < len(data["results"]):
                        next_block = data["results"][next_block_index]
                        if next_block["type"] == "paragraph" and not next_block["paragraph"]["rich_text"]:
                            return last_block["id"], message, next_block["id"]
                        else:
                            return last_block["id"], message, None
                    return last_block["id"], message, None
    return None, None, None


def append_response(response_text, blank_block_id=None):
    if blank_block_id:
        notion_url = f"https://api.notion.com/v1/blocks/{blank_block_id}"
        payload = {
            "paragraph": {
                "rich_text": [{"text": {"content": response_text}}]
            }
        }
        response = requests.patch(notion_url, json=payload, headers=headers)
    else:
        payload = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": response_text}}]
                    }
                }
            ]
        }
        response = requests.patch(NOTION_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Bot replied with: {response_text}")
    else:
        print("Error updating response:", response.json())


def check_notion(response_prefix=None, message_prefix=None):
    global processed_messages

    while True:
        block_id, latest_text, blank_block_id = get_latest_text(response_prefix, message_prefix)
        if block_id and latest_text:
            if block_id in processed_messages:
                continue

            print(f"User said: {latest_text}")
            append_response(f"{response_prefix}{latest_text}", blank_block_id)
            processed_messages.add(block_id)

        time.sleep(1)
