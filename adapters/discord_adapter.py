"""
Discord Bridge for Exy OS.
Run this script separately from your FastAPI server.
Requires: pip install discord.py websockets
"""
import os
import json
import asyncio
import time
import discord
import websockets
from discord.ext import commands

# Load your Discord Bot Token from the environment
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
EXY_OS_WS_URL = "ws://127.0.0.1:8000/api/ws"

# Set up Discord intents (Needs Message Content Intent enabled in Discord Dev Portal)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- NEW: App Command Tree Setup ---
@bot.event
async def setup_hook():
    """Syncs slash commands to Discord to activate the modern 'App' UI."""
    await bot.tree.sync()
    print("App Commands synced. 'App' badge activated in Discord.")

@bot.tree.command(name="status", description="Check if Exy OS is online")
async def status(interaction: discord.Interaction):
    """A basic slash command to ensure Discord registers this as a modern App."""
    await interaction.response.send_message("🟢 Exy OS is online and observing.", ephemeral=True)
# -----------------------------------

async def send_to_exy_os(payload: dict, discord_message: discord.Message):
    """Handles the WebSocket connection to your FastAPI backend."""
    try:
        # Connect to Exy OS (Headers removed, they were a red herring!)
        async with websockets.connect(EXY_OS_WS_URL) as ws:
            # Send the translated payload
            await ws.send(json.dumps(payload))
            
            # Wait for Exy OS to reply
            response_json = await ws.recv()
            response = json.loads(response_json)
            
            # Send the reply back to the Discord channel
            if "received" in response:
                await discord_message.channel.send(response["received"])
            elif "error" in response:
                await discord_message.channel.send(f"⚠️ OS Error: {response['error']}")
                
    except websockets.exceptions.InvalidStatus as e:
        print(f"Server rejected connection ({e}). Check your FastAPI terminal for hidden errors!")
    except ConnectionRefusedError:
        print("Error: Exy OS is not running. Please start Uvicorn first.")

@bot.event
async def on_ready():
    print(f"Bridge Active: Logged in as {bot.user}")
    print("Listening for messages to forward to Exy OS...")

@bot.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # THE ADAPTER PATTERN: Translate Discord's object into ExyPayload
    exy_payload = {
        "user_id": str(message.author.id),
        "platform": "discord",
        "raw_text": message.content,
        "timestamp": int(time.time()),
        "message_id": str(message.id),
        "channel_id": str(message.channel.id)
    }

    # Fire and forget the websocket task
    asyncio.create_task(send_to_exy_os(exy_payload, message))

if __name__ == "__main__":
    if DISCORD_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please replace YOUR_BOT_TOKEN_HERE with your actual Discord bot token.")
    else:
        bot.run(DISCORD_TOKEN)