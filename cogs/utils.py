import discord
import asyncio
from discord.ext import commands
from datetime import datetime
import aiohttp


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_deleted_message = None
        self.afk_users = {}

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f'pong!  `{round(self.bot.latency * 1000)}ms`')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.last_deleted_message = message

    @commands.command(name='snipe', aliases=['s'])
    async def snipe(self, ctx):
        if self.last_deleted_message:
            embed = discord.Embed(
                description=self.last_deleted_message.content,
                color=0x586165
                )
            embed.set_author(
                name=self.last_deleted_message.author.display_name,
                icon_url=self.last_deleted_message.author.avatar.url
                )
            embed.set_footer(text=f"Channel: {self.last_deleted_message.channel.name} | ID: {self.last_deleted_message.id}")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(
                description=f":mag_right: | {ctx.author.mention}: No messages to snipe!",
                colour=0xfbff00
                )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='clearsnipe', aliases=['cs'])
    async def cs(self, ctx):
        if self.last_deleted_message:
            self.last_deleted_message = None
            await ctx.message.add_reaction("👍")
        else:
            embed=discord.Embed(
                description=f":mag_right: | {ctx.author.mention}: No messages to clear!",
                colour=0xfbff00
                )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="emoji", aliases=["e", "em", "emote"])
    async def emoji(self, ctx, emoji: str):
        embed = discord.Embed(
            color=0x586165
        )

        if emoji.startswith("<:") or emoji.startswith("<a:"):
            try:
                emoji_obj = await commands.EmojiConverter().convert(ctx, emoji)
                embed.set_image(url=emoji_obj.url)
            except:
                return
        else:
            codepoints = '-'.join(f'{ord(c):x}' for c in emoji)
            twemoji_url = f"https://twemoji.maxcdn.com/v/latest/72x72/{codepoints}.png"
            embed.set_image(url=twemoji_url)
        await ctx.send(embed=embed)

        @commands.command(name="afk")
        async def set_afk(self, ctx, *, reason= None):
            if reason == None:
                reason = "N/A"
            user_id = ctx.author.id
            self.afk_users[user_id] = reason

            embed = discord.Embed(
                description=f"💤 | {ctx.author.mention}: You're now AFK with the status: **{reason}**"
                )
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url
                )
            await ctx.send(embed=embed)
        
        @commands.Cog.listener()
        async def on_message(self, message):
            if message.author.bot:
                return
            if message.author.id in self.afk_users:
                del self.afk_users[message.author.id]
                
                embed = discord.Embed(
                    description=f"💤 | {ctx.author.mention}: Welcome back! You're no longer AFK"
                    )
                embed.set_author(
                    name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url
                )
                await message.channel.send(embed=embed)

            mentioned_users = message.mentions
            for user in mentioned_users:
                if user.id in self.afk_users:
                    reason = reason
                    embed = discord.Embed(
                        description=f"💤 | {ctx.author.mention}: {user.mention} is currently AFK: {reason}"
                        )
                    embed.set_author(
                        name=ctx.author.display_name,
                        icon_url=ctx.author.avatar.url
                        )
                    await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utils(bot))
