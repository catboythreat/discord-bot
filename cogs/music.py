import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }

    def check_queue(self, ctx):
        guild_id = ctx.guild.id
        if self.queues[guild_id]:
            next_song = self.queues[guild_id].popleft()
            player = discord.FFmpegOpusAudio(next_song, **self.ffmpeg_options)
            self.voice_clients[guild_id].play(player, after=lambda e: self.check_queue(ctx))
            asyncio.run_coroutine_threadsafe(ctx.send(" "), self.bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(ctx.send("Queue is empty."), self.bot.loop)

    @commands.command(name='play')
    async def play(self, ctx, *, url):
        guild_id = ctx.guild.id

        try:
            if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[guild_id] = voice_client
            else:
                voice_client = self.voice_clients[guild_id]
        except Exception as e:
            await ctx.send(f"Error connecting to voice channel: {str(e)}")
            return

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            song_url = data['url']
            
            if guild_id not in self.queues:
                self.queues[guild_id] = deque()

            self.queues[guild_id].append(song_url)

            await ctx.send(f"Added to queue: {data['title']}")

            if not voice_client.is_playing():
                self.check_queue(ctx)

        except Exception as e:
            print(e)
            await ctx.send(f"Error playing the song: {str(e)}")

    @commands.command(name='skip')
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            await ctx.send("Song skipped.")
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        guild_id = ctx.guild.id
        try:
            self.voice_clients[guild_id].pause()
            await ctx.send("Music paused.")
        except Exception as e:
            print(e)
            await ctx.send(f"Error pausing the music: {str(e)}")

    @commands.command(name='resume')
    async def resume(self, ctx):
        guild_id = ctx.guild.id
        try:
            self.voice_clients[guild_id].resume()
            await ctx.send("Music resumed.")
        except Exception as e:
            print(e)
            await ctx.send(f"Error resuming the music: {str(e)}")

    @commands.command(name='stop')
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        try:
            self.voice_clients[guild_id].stop()
            await self.voice_clients[guild_id].disconnect()
            self.queues[guild_id].clear()
            await ctx.send("Music stopped and disconnected.")
        except Exception as e:
            print(e)
            await ctx.send(f"Error stopping the music: {str(e)}")

    @commands.command(name='queue')
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.queues or not self.queues[guild_id]:
            await ctx.send("The queue is currently empty.")
            return

        queue_list = list(self.queues[guild_id])
        next_song = queue_list[0] if queue_list else None
        queue_display = []

        if next_song:
            queue_display.append(f"**Next up:** {next_song}")

        queue_display.extend([f"{i + 1}: {song}" for i, song in enumerate(queue_list[1:])])
        queue_text = "\n".join(queue_display)

        await ctx.send(f"**Current Queue:**\n{queue_text}")

async def setup(bot):
    await bot.add_cog(Music(bot))
