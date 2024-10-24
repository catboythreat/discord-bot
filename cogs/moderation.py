import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import timedelta 

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        if member is None and ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                title="Command: ban",
                description="Bans a member from the server.\n```\nSyntax: ,ban (member) (reason)\nExample: ,ban @User Spamming\n```",
                colour=0x586165
            )
            embed.add_field(name="Permission(s)", value="```ban_members```")
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return


        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You are missing the permission: `ban_members`!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: Cannot ban this user!",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if member.premium_since:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: This user is **boosting** the server since <t:{int(member.premium_since.timestamp())}:d>. Are you sure you want to ban {member.mention}?",
                colour=0xa22f93
            )
            
            approve_button = Button(style=discord.ButtonStyle.green, label="Approve", custom_id='ban_approve')
            decline_button = Button(style=discord.ButtonStyle.red, label="Decline", custom_id='ban_decline')
            view = View()
            view.add_item(approve_button)
            view.add_item(decline_button)
            message = await ctx.send(embed=embed, view=view)

            def check(interaction):
                return interaction.message.id == message.id and interaction.user == ctx.author
            interaction = await self.bot.wait_for('interaction', timeout=30.0, check=check)
            if interaction.custom_id == 'ban_approve':
                await member.ban(reason=f"Banned by {ctx.author.name} for {reason}")
                embed = discord.Embed(
                    title=f"<:botapprove:1280951128137400423> | {member.display_name} has been banned!",
                    colour=0x56d04e
                )
                embed.add_field(name="Username:", value=member.name, inline=False)
                embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                await message.delete()
                embed = discord.Embed(
                    description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: Ban cancelled.",
                    colour=0xfa0505
                )
                await ctx.send(embed=embed)
                return

        else:
            await member.ban(reason=f"Banned by {ctx.author.name} for {reason}")
            embed = discord.Embed(
                title=f"<:botapprove:1280951128137400423> | {member.display_name} has been banned!",
                colour=0x56d04e
            )
            embed.add_field(name="Username:", value=member.name, inline=False)
            embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
            await ctx.send(embed=embed)

    @commands.command()
    async def unban(self, ctx, user_id: int = None, *, reason=None):
        if user_id is None and ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                title="Command: unban",
                description="Unbans a user from the server.\n```\nSyntax: ,unban (user_id) (reason)\nExample: ,unban 123456789 Spamming\n```",
                colour=0x586165
            )
            embed.add_field(name="Permission(s)", value="```ban_members```")
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return

        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You are missing the permission: `ban_members`!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if reason is None:
            reason = "No reason provided"

        try:
            user = discord.Object(id=user_id)
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author.name} for: {reason}")
            await ctx.message.add_reaction("👍")
        except discord.NotFound:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: User is not banned!",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
        except discord.Forbidden:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: I don't have permission to unban this user!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        if member is None and ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                title="Command: kick",
                description="Kicks a member from the server.\n```\nSyntax: ,kick (member) (reason)\nExample: ,kick @User Spamming\n```",
                colour=0x586165
            )
            embed.add_field(name="Permission(s)", value="```kick_members```")
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return

        if not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You are missing the permission: `kick_members`!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: Cannot kick this user due to role hierarchy.",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        await member.kick(reason=f"Kicked by {ctx.author.name} for {reason}")
        embed = discord.Embed(
            title=f"<:botapprove:1280951128137400423> | {member.display_name} has been kicked!",
            colour=0x56d04e
        )
        embed.add_field(name="Username:", value=member.name, inline=False)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def mute(self, ctx, member: discord.Member = None, time: int = None, *, reason=None):
        if member is None or time is None and ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="Command: mute",
                description="Mutes a member for a specified time (in minutes).\n```\nSyntax: ,mute (member) (time in minutes) (reason)\nExample: ,mute @User 10 Spamming\n```",
                colour=0x586165
            )
            embed.add_field(name="Permission(s)", value="```moderate_members```")
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return

        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You are missing the permission: `moderate_members`!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: Cannot mute this user due to role hierarchy.",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        duration = timedelta(minutes=time)
        await member.timeout_for(duration, reason=f"Muted by {ctx.author.name} for {reason}")
        embed = discord.Embed(
            title=f"<:botapprove:1280951128137400423> | {member.display_name} has been muted for {time} minutes!",
            colour=0x56d04e
        )
        embed.add_field(name="Username:", value=member.name, inline=False)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        embed.add_field(name="Duration", value=f"{time} minutes", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def unmute(self, ctx, member: discord.Member = None, *, reason=None):
        if member is None and ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="Command: unmute",
                description="Unmutes a member (removes timeout).\n```\nSyntax: ,unmute (member) (reason)\nExample: ,unmute @User Time served\n```",
                colour=0x586165
            )
            embed.add_field(name="Permission(s)", value="```moderate_members```")
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return

        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You are missing the permission: `moderate_members`!",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: Cannot unmute this user due to role hierarchy.",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        # Remove the timeout
        await member.edit(timed_out_until=None, reason=f"Unmuted by {ctx.author.name} for {reason}")
        embed = discord.Embed(
            title=f"<:botapprove:1280951128137400423> | {member.display_name} has been unmuted!",
            colour=0x56d04e
        )
        embed.add_field(name="Username:", value=member.name, inline=False)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
