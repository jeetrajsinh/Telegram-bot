from telethon import TelegramClient, events
import re
import requests

# Telegram API credentials
api_id = 28901891  # Replace with your API ID
api_hash = 'd6c85bdc978cbeefe357c1fe508a173c'  # Replace with your API hash

# Bot token and chat ID for sending messages
bot_token = '7395410553:AAFsdBTPZj0_MnqLl653_-S_wIWksR3JW4M'  # Replace with your bot token
your_personal_chat_id = 6632952428  # Replace with your personal chat ID
your_group_chat_id = 0000000  # Replace with your group chat ID

# Regular expression to capture Solana token contract addresses
solana_contract_regex = r'[A-Za-z0-9]{44}'

# Dictionary to keep track of contract addresses and their mention counts
contract_mentions = {}

# Dictionary to keep track of last sent count for each contract address
last_sent_count = {}

# List of chat IDs to notify
chat_ids_to_notify = [6632952428, your_group_chat_id]

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    # Extract the message text and the sender's chat ID
    message = event.message.message or ""
    chat_id = event.chat_id

    # Handle forwarded messages
    if event.message.fwd_from:
        # If the message is forwarded, get the original message
        if event.message.fwd_from.saved_from_msg_id:
            original_message = await event.client.get_messages(event.message.fwd_from.saved_from_peer, ids=event.message.fwd_from.saved_from_msg_id)
            message = original_message.message

    # Handle media captions
    if event.message.media:
        if event.message.message:
            message += "\n" + event.message.message

    # Find all contract addresses in the message
    contract_addresses = re.findall(solana_contract_regex, message)
    
    # Debug: print received message and found contract addresses
    if contract_addresses:
        print(f"Received message in chat {chat_id}: {message}")
        print(f"Found contract addresses: {contract_addresses}")

    # Update the contract address mention counts across all groups
    for address in contract_addresses:
        if address not in contract_mentions:
            contract_mentions[address] = set()

        contract_mentions[address].add(chat_id)
        current_count = len(contract_mentions[address])
        # Debug: print updated contract mention count
        print(f"Updated mention count for {address}: {current_count} groups")

        # Check and notify if a contract address is mentioned by 3 or more groups
        if current_count >= 3:
            if address not in last_sent_count or current_count > last_sent_count[address]:
                send_message_via_bot(address, current_count)
                last_sent_count[address] = current_count

def send_message_via_bot(address, count):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    for chat_id in chat_ids_to_notify:
        data = {
            'chat_id': chat_id,
            'text': f'CA : `{address}` and count : {count}',
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"Notification sent to chat {chat_id}: CA : {address} and count : {count}")
        else:
            print(f"Failed to send notification to chat {chat_id}: {response.text}")

# Start the client
with client:
    print("Listening for messages...")
    client.run_until_disconnected()
    
