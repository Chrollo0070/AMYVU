from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat
from datetime import datetime

api_id = int(input("Enter your API ID: "))
api_hash = input("Enter your API Hash: ")
session_name = input("Enter a session name (e.g., user1): ")

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.start()
    print("✅ Logged in successfully.\n")

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        # We check if entity is Channel or Chat and if it's a group or supergroup
        if isinstance(entity, Channel) or isinstance(entity, Chat):
            # Some chats are private or users, skip those that are not groups
            if dialog.is_group or (isinstance(entity, Channel) and entity.megagroup):
                try:
                    # Get the latest message from this group
                    async for msg in client.iter_messages(entity, limit=1):
                        if msg:
                            print(f"👥 {dialog.name}")
                            print(f"📅 Latest Activity: {msg.date.strftime('%Y-%m-%d')}")
                            print("-" * 40)
                        else:
                            print(f"👥 {dialog.name}")
                            print(f"📅 No messages found")
                            print("-" * 40)
                except Exception as e:
                    print(f"⚠️ Could not fetch messages from {dialog.name}: {e}")

with client:
    client.loop.run_until_complete(main())
