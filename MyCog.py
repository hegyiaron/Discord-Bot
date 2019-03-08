import discord
from discord.ext import commands
from apiclient.discovery import build
import json
from datetime import datetime
import time
import asyncio
import sys
import logging
import aiohttp
import re

bot = commands.Bot(command_prefix='-', description=None)

#A "cog" létrehozása, amely a fő scriptben elő lesz hívva
class MyCog:
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(pass_context=True)
    async def cog_command(self, ctx):
        return 0

def setup(bot):
    bot.add_cog(MyCog(bot))
