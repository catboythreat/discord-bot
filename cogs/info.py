import discord
import asyncio
from discord.ext import commands
from discord.utils import get
import requests


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo', aliases=['si', 'sinfo'])
    async def serverinfo(self, ctx):
        try:
            guild = ctx.guild 
            embed = discord.Embed(
                title=guild.name,
                description=f"Server created on <t:{int(guild.created_at.timestamp())}:d>",
                color=0x586165
                )
            embed.add_field(
                name="Members",
                value=(f"Total: {guild.member_count}\n" f"Humans: {sum(1 for member in guild.members if not member.bot)}\n" f"Bots: {sum(1 for member in guild.members if member.bot)}"),
                inline=True
                )
            embed.add_field(
                name="Information",
                value=(f"Boosts: {guild.premium_subscription_count}\n" f"Level: {self.get_boost_level(guild.premium_tier)}\n" f"Security: {self.get_verification_level(guild.verification_level)}"),
                inline=True
                )
            embed.add_field(
                name=" ",
                value=" ",
                inline=False
                )
            embed.add_field(
                name=f"Channels",
                value=(f"Text: {len([channel for channel in guild.channels if isinstance(channel, discord.TextChannel)])}\n" f"Voice: {len([channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)])}"),
                inline=True
                )
            embed.add_field(
                name="Counts",
                value=(f"Roles: {len(guild.roles)}\n" f"Emojis: {len(guild.emojis)}"),
                inline=True
                )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            if guild.banner:
                embed.set_image(url=guild.banner.url)
            await ctx.reply(embed=embed, mention_author=False)
        except Exception as e:
            print(f"Error sending serverinfo embed: {e}")

    def get_boost_level(self, tier):
        levels = {0: "None", 1: "1", 2: "2", 3: "3"}
        return levels.get(tier, "Unknown")

    def get_verification_level(self, level):
        levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
        }
        return levels.get(level, "Unknown")


    @commands.command(name='whois', aliases=['userinfo', 'ui'])
    async def whois(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_list = ", ".join(reversed(roles)) if roles else "No roles"
        embed = discord.Embed(
            title=f"{member.name}'s info:",
            colour=0x586165
            )
        embed.add_field(
            name="Dates",
            value=f"Joined Discord: <t:{int(member.created_at.timestamp())}:d>\n" f"Joined Server: <t:{int(member.joined_at.timestamp())}:d>"
            )
        embed.add_field(
            name="**Roles**",
            value=roles_list,
            inline=False
            )
        embed.set_thumbnail(url=f"{member.avatar.url}")
        embed.set_footer(text=f"ID: {member.id}")
        await ctx.reply(embed=embed, mention_author=False)



    @commands.command(name='pfp', aliases=['av', 'avatar'])
    async def pfp(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(
            title=f"{member.name}'s Avatar",
            color=0x586165
            )
        embed.set_image(url=member.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)


    def fetch_definition(self, term: str):
        url = f"https://api.urbandictionary.com/v0/define?term={term}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data['list']:
                return data['list'][0]
        return None

    @commands.command(name="urbandictionary", aliases=["ud", "urban"])
    async def urbandictionary(self, ctx, *, term: str):
        definition_data = self.fetch_definition(term)

        if definition_data:
            word = definition_data['word']
            definition = definition_data['definition']
            example = definition_data['example']
            permalink = definition_data['permalink']
            thumbs_up = definition_data['thumbs_up']
            thumbs_down = definition_data['thumbs_down']

            embed = discord.Embed(
                title=word,
                description=definition,
                url=permalink,
                color=0xFFFFFF
            )
            embed.add_field(name="Example", value=example if example else "No example provided.", inline=False)
            embed.add_field(name="votes", value=f"👍 `{thumbs_up} | {thumbs_down}` 👎", inline=False)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.reply(f"No definition found for `{term}`.", mention_author=False)


async def setup(bot):
    await bot.add_cog(Info(bot))
