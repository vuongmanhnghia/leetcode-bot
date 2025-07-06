import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from leetcode_integration import LeetCodeIntegration

# Load environment variables from .env file
load_dotenv()

# Bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required!")

# Bot intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )
        self.config = {
            "CHANNEL_ID": os.getenv("CHANNEL_ID"),
            "DAILY_TIME": os.getenv("DAILY_TIME"),
            "TIMEZONE_OFFSET": os.getenv("TIMEZONE_OFFSET"),
        }
        self.leetcode = LeetCodeIntegration()

    async def setup_hook(self):
        """Setup when bot starts"""
        print(f"Bot đang đăng nhập...")
        try:
            synced = await self.tree.sync()
            print(f"Đã sync {len(synced)} slash command(s)")
        except Exception as e:
            print(f"Lỗi khi sync commands: {e}")


bot = Bot()
