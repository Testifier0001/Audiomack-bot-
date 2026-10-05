import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'nocheckcertificate': True,
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("Joined the voice channel!")
    else:
        await ctx.send("Join a voice channel first!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first!")

    voice = ctx.voice_client or await ctx.author.voice.channel.connect()

    await ctx.send(f"Searching: {query}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info.get('title', 'Unknown')

        source = discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
        
        if voice.is_playing():
            voice.stop()
        voice.play(source)
        await ctx.send(f"Now playing: **{title}**")
    except Exception as e:
        await ctx.send(f"Error: {str(e)[:150]}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped")

bot.run(TOKEN)
