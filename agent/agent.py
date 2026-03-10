#!/usr/bin/env python3
"""
Fiverr Remote Monitor Agent
Monitors Fiverr inbox via Chrome Remote Debugging and forwards messages to server
"""

import os
import json
import time
import logging
import requests
import websocket
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import uuid
from typing import Dict, List, Optional
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
AGENT_TOKEN = os.getenv('AGENT_TOKEN', '')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '45'))
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', '30'))
RECONNECT_INTERVAL = int(os.getenv('RECONNECT_INTERVAL', '10'))
CHROME_DEBUG_PORT = int(os.getenv('CHROME_DEBUG_PORT', '9222'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FiverrMonitorAgent:
    """Main agent class for monitoring Fiverr messages"""

    def __init__(self):
        self.driver = None
        self.ws = None
        self.last_seen_file = 'last_seen.json'
        self.last_seen = self.load_last_seen()
        self.running = True
        self.agent_id = str(uuid.uuid4())

    def load_last_seen(self) -> Dict:
        """Load last seen message IDs"""
        try:
            with open(self.last_seen_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_last_seen(self):
        """Save last seen message IDs"""
        with open(self.last_seen_file, 'w') as f:
            json.dump(self.last_seen, f, indent=2)

    def connect_chrome(self) -> bool:
        """Connect to existing Chrome instance with remote debugging"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{CHROME_DEBUG_PORT}")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("ক্রোমের সাথে সফলভাবে সংযুক্ত হয়েছে | Successfully connected to Chrome")
            return True
        except Exception as e:
            logger.error(f"Chrome সংযোগে ব্যর্থ | Failed to connect to Chrome: {e}")
            return False

    def connect_websocket(self) -> bool:
        """Connect to server via WebSocket"""
        try:
            ws_url = f"{SERVER_URL.replace('http', 'ws')}/agent?token={AGENT_TOKEN}"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_ws_open,
                on_message=self.on_ws_message,
                on_error=self.on_ws_error,
                on_close=self.on_ws_close
            )

            # Run WebSocket in separate thread
            import threading
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()

            logger.info("WebSocket সংযুক্ত | WebSocket connected")
            return True
        except Exception as e:
            logger.error(f"WebSocket সংযোগে ব্যর্থ | WebSocket connection failed: {e}")
            return False

    def on_ws_open(self, ws):
        """WebSocket connection opened"""
        logger.info("WebSocket সংযোগ প্রতিষ্ঠিত | WebSocket connection established")
        # Send agent info
        self.send_ws_message({
            'type': 'agent_info',
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        })

    def on_ws_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            if data.get('type') == 'send_reply':
                self.send_reply(data.get('conversation_id'), data.get('message'))
            elif data.get('type') == 'ping':
                self.send_ws_message({'type': 'pong'})
        except Exception as e:
            logger.error(f"WebSocket বার্তা প্রক্রিয়াকরণে ব্যর্থ | Failed to process WebSocket message: {e}")

    def on_ws_error(self, ws, error):
        """WebSocket error handler"""
        logger.error(f"WebSocket ত্রুটি | WebSocket error: {error}")

    def on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        logger.warning("WebSocket সংযোগ বিচ্ছিন্ন | WebSocket connection closed")

    def send_ws_message(self, data: dict):
        """Send message via WebSocket"""
        try:
            if self.ws and self.ws.sock and self.ws.sock.connected:
                self.ws.send(json.dumps(data))
        except Exception as e:
            logger.error(f"WebSocket বার্তা পাঠাতে ব্যর্থ | Failed to send WebSocket message: {e}")

    def get_conversations(self) -> List[Dict]:
        """Fetch all conversations from Fiverr inbox"""
        try:
            # Navigate to inbox
            self.driver.get("https://www.fiverr.com/inbox")
            time.sleep(3)

            # Wait for conversations to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "conversation-item")))

            # Parse conversations
            conversations = []
            conversation_elements = self.driver.find_elements(By.CLASS_NAME, "conversation-item")

            for elem in conversation_elements:
                try:
                    conv_id = elem.get_attribute('data-conversation-id')
                    username = elem.find_element(By.CLASS_NAME, "username").text
                    last_message = elem.find_element(By.CLASS_NAME, "last-message").text
                    unread = 'unread' in elem.get_attribute('class')

                    conversations.append({
                        'conversation_id': conv_id,
                        'username': username,
                        'last_message': last_message,
                        'unread': unread,
                        'timestamp': datetime.now().isoformat()
                    })
                except NoSuchElementException:
                    continue

            return conversations
        except TimeoutException:
            logger.error("Inbox লোড করতে সময়সীমা অতিক্রান্ত | Timeout loading inbox")
            return []
        except Exception as e:
            logger.error(f"Conversation আনতে ব্যর্থ | Failed to fetch conversations: {e}")
            return []

    def get_messages(self, conversation_id: str) -> List[Dict]:
        """Fetch messages from a specific conversation"""
        try:
            self.driver.get(f"https://www.fiverr.com/inbox/{conversation_id}")
            time.sleep(2)

            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "message")))

            messages = []
            message_elements = self.driver.find_elements(By.CLASS_NAME, "message")

            for elem in message_elements:
                try:
                    msg_id = elem.get_attribute('data-message-id')
                    sender = elem.find_element(By.CLASS_NAME, "sender").text
                    text = elem.find_element(By.CLASS_NAME, "text").text
                    timestamp = elem.find_element(By.CLASS_NAME, "timestamp").get_attribute('data-timestamp')

                    messages.append({
                        'message_id': msg_id,
                        'sender': sender,
                        'text': text,
                        'timestamp': timestamp,
                        'conversation_id': conversation_id
                    })
                except NoSuchElementException:
                    continue

            return messages
        except Exception as e:
            logger.error(f"Messages আনতে ব্যর্থ | Failed to fetch messages: {e}")
            return []

    def send_reply(self, conversation_id: str, message: str) -> bool:
        """Send reply to a conversation"""
        try:
            self.driver.get(f"https://www.fiverr.com/inbox/{conversation_id}")
            time.sleep(2)

            # Find message input
            input_box = self.driver.find_element(By.CLASS_NAME, "message-input")
            send_button = self.driver.find_element(By.CLASS_NAME, "send-button")

            # Type message naturally
            import random
            for char in message:
                input_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))

            # Send
            send_button.click()

            logger.info(f"✅ Reply পাঠানো হয়েছে | Reply sent to {conversation_id}")
            self.send_ws_message({
                'type': 'reply_sent',
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Reply পাঠাতে ব্যর্থ | Failed to send reply: {e}")
            return False

    def check_new_messages(self):
        """Check for new messages and forward to server"""
        conversations = self.get_conversations()

        for conv in conversations:
            if conv['unread'] and conv['conversation_id'] not in self.last_seen:
                # New conversation!
                messages = self.get_messages(conv['conversation_id'])

                for msg in messages:
                    if msg['message_id'] not in self.last_seen.get(conv['conversation_id'], []):
                        # Forward new message to server
                        self.send_ws_message({
                            'type': 'new_message',
                            'conversation': conv,
                            'message': msg,
                            'timestamp': datetime.now().isoformat()
                        })

                        # Update last seen
                        if conv['conversation_id'] not in self.last_seen:
                            self.last_seen[conv['conversation_id']] = []
                        self.last_seen[conv['conversation_id']].append(msg['message_id'])

        self.save_last_seen()

    def send_heartbeat(self):
        """Send heartbeat to server"""
        self.send_ws_message({
            'type': 'heartbeat',
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        })

    def run(self):
        """Main run loop"""
        logger.info("==================================================")
        logger.info("Fiverr Remote Monitor Agent শুরু হচ্ছে | Starting...")
        logger.info("==================================================")

        # Connect to Chrome
        if not self.connect_chrome():
            logger.error("Chrome সংযোগ ব্যর্থ | Chrome connection failed. Exiting.")
            return

        # Connect to server
        if not self.connect_websocket():
            logger.error("WebSocket সংযোগ ব্যর্থ | WebSocket connection failed. Exiting.")
            return

        last_check = time.time()
        last_heartbeat = time.time()

        try:
            while self.running:
                current_time = time.time()

                # Check for new messages
                if current_time - last_check >= CHECK_INTERVAL:
                    self.check_new_messages()
                    last_check = current_time

                # Send heartbeat
                if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                    self.send_heartbeat()
                    last_heartbeat = current_time

                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Agent বন্ধ হচ্ছে | Stopping agent...")
        except Exception as e:
            logger.error(f"Agent রান করতে ব্যর্থ | Agent run failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            if self.ws:
                self.ws.close()


def main():
    """Entry point"""
    if not AGENT_TOKEN:
        logger.error("AGENT_TOKEN .env ফাইলে সেট করা নেই | AGENT_TOKEN not set in .env file")
        return

    agent = FiverrMonitorAgent()
    agent.run()


if __name__ == "__main__":
    main()
