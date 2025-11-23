# bot.py
import os
import json
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

from api import call_addfriend_api

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS_RAW = os.getenv("ADMINS", "")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "eu").lower()

ADMINS = {int(x.strip()) for x in ADMINS_RAW.split(",") if x.strip().isdigit()}

BASE_DIR = Path(__file__).parent
CHANNELS_FILE = BASE_DIR / "channels.json"
USAGE_FILE = BASE_DIR / "usage.json"

GIF_THUMB = "https://i.imgur.com/3ikE0vL.gif"

# Limits
NORMAL_LIMIT = 2

# Helper persistence functions
def ensure_files():
    if not CHANNELS_FILE.exists():
        CHANNELS_FILE.write_text(json.dumps({"guild_channels": {}}, indent=2))
    if not USAGE_FILE.exists():
        USAGE_FILE.write_text(json.dumps({"users": {}}, indent=2))

def load_channels():
    ensure_files()
    return json.loads(CHANNELS_FILE.read_text())

def save_channels(data):
    CHANNELS_FILE.write_text(json.dumps(data, indent=2))

def load_usage():
    ensure_files()
    return json.loads(USAGE_FILE.read_text())

def save_usage(data):
    USAGE_FILE.write_text(json.dumps(data, indent=2))

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

def get_user_limit_remaining(user_id: int):
    usage = load_usage()
    users = usage.setdefault("users", {})
    u = users.get(str(user_id), {"used": 0})
    if is_admin(user_id):
        return None  # None means unlimited
    used = u.get("used", 0)
    return max(0, NORMAL_LIMIT - used)

def increment_user_usage(user_id: int):
    if is_admin(user_id):
        return
    usage = load_usage()
    users = usage.setdefault("users", {})
    u = users.setdefault(str(user_id), {"used": 0})
    u["used"] = u.get("used", 0) + 1
    save_usage(usage)

def reset_usage_for_user(user_id: int):
    usage = load_usage()
    users = usage.setdefault("users", {})
    if str(user_id) in users:
        users[str(user_id)]["used"] = 0
        save_usage(usage)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

def make_embed(message_text: str, success: bool, author: discord.Member, remaining_limit: Optional[int]):
    color = 0x7c5cff if success else 0xFF4D4D  # purple for success, red for error
    embed = discord.Embed(
        title="Friend Added Successfully" if success else "Friend Request Failed",
        description=None,
        color=color
    )
    # API message
    embed.add_field(name="\u200b", value=message_text, inline=False)

    # GIF at bottom
    embed.set_image(url=GIF_THUMB)

    # Footer
    embed.set_footer(text="Dev: Wotaxx • Powered by ULTIGER IOS")

    # Limit info
    limit_text = "unlimited" if remaining_limit is None else str(remaining_limit)
    embed.add_field(name="Limit", value=limit_text, inline=True)

    # Author
    embed.set_author(name=str(author), icon_url=author.display_avatar.url if author.display_avatar else None)

    return embed

# Admin-only set channel
@bot.command(name="setchannel")
async def setchannel(ctx):
    if not is_admin(ctx.author.id):
        await ctx.reply("You are not allowed to use this command.")
        return
    data = load_channels()
    guilds = data.setdefault("guild_channels", {})
    guilds[str(ctx.guild.id)] = ctx.channel.id
    save_channels(data)
    await ctx.reply(f"Set this channel ({ctx.channel.id}) as the allowed channel for !add.")

@bot.command(name="removechannel")
async def removechannel(ctx):
    if not is_admin(ctx.author.id):
        await ctx.reply("You are not allowed to use this command.")
        return
    data = load_channels()
    guilds = data.setdefault("guild_channels", {})
    if str(ctx.guild.id) in guilds:
        del guilds[str(ctx.guild.id)]
        save_channels(data)
        await ctx.reply("Removed the allowed channel for this server.")
    else:
        await ctx.reply("No channel was set for this server.")

# Main add command
@bot.command(name="add")
async def add(ctx, adduid: str = None):
    if adduid is None:
        await ctx.reply("Usage: `!add <uid>`")
        return

    # Channel restriction
    channels = load_channels().get("guild_channels", {})
    allowed_channel_id = channels.get(str(ctx.guild.id))
    if allowed_channel_id is not None and ctx.channel.id != allowed_channel_id:
        await ctx.reply("This command can only be used in the configured channel.")
        return

    # Usage limit
    remaining = get_user_limit_remaining(ctx.author.id)
    if remaining is not None and remaining <= 0:
        await ctx.reply(f"You reached your limit. Limit: {NORMAL_LIMIT}")
        return

    # Compute remaining_after upfront
    remaining_after = get_user_limit_remaining(ctx.author.id)

    # Call API
    await ctx.typing()
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, call_addfriend_api, adduid)
    except Exception:
        # Delete user message silently if network error
        await ctx.message.delete()
        return

    # Parse API response
    success_message = result.get("message")
    error_message = result.get("error")

    # If neither message nor error, delete user message silently
    if not success_message and not error_message:
        await ctx.message.delete()
        return

    # Increment usage
    increment_user_usage(ctx.author.id)
    remaining_after = get_user_limit_remaining(ctx.author.id)

    # Make embed
    if success_message:
        embed = make_embed(success_message, success=True, author=ctx.author, remaining_limit=remaining_after)
    else:  # error_message exists
        embed = make_embed(error_message, success=False, author=ctx.author, remaining_limit=remaining_after)

    await ctx.reply(embed=embed)

# Admin command to reset user usage
@bot.command(name="resetusage")
async def resetusage(ctx, user_id: int = None):
    if not is_admin(ctx.author.id):
        await ctx.reply("You are not allowed to use this command.")
        return
    if user_id is None:
        await ctx.reply("Usage: `!resetusage <discord_user_id>`")
        return
    reset_usage_for_user(user_id)
    await ctx.reply(f"Reset usage for user {user_id}.")

def run():
    ensure_files()
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN env var missing in .env")
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    run()
