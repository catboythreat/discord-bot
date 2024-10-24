import discord
from discord.ext import commands

class VCManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.j2c_channel_ids = {}
        self.voice_channel_owners = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id

        if guild_id not in self.j2c_channel_ids:
            return
        
        j2c_channel_id = self.j2c_channel_ids[guild_id]
        j2c_channel = member.guild.get_channel(j2c_channel_id)

        if after.channel and after.channel.id == j2c_channel_id:
            category = j2c_channel.category
            new_channel = await member.guild.create_voice_channel(
                name=f"{member.display_name}'s VC",
                category=category
            )
            await member.move_to(new_channel)

            if guild_id not in self.voice_channel_owners:
                self.voice_channel_owners[guild_id] = {}
            self.voice_channel_owners[guild_id][new_channel.id] = member.id

        if before.channel and guild_id in self.voice_channel_owners:
            if before.channel.id in self.voice_channel_owners[guild_id]:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del self.voice_channel_owners[guild_id][before.channel.id]

    @commands.command(name="vc")
    async def vc(self, ctx, action: str = None, *, args=None):
        guild_id = ctx.guild.id

        valid_actions = ["set", "claim", "rename", "lock", "unlock", "transfer", "kick", "allow", "ghost", "unghost", "ban", "unban", "limit"]
        if not action or action not in valid_actions:
            embed = discord.Embed(
                title="Command: voicemaster",
                description="Creates a customizable temporarily voice channel.\n```\nSyntax: ,vc (action) (arguments)\nExample: ,vc kick @Abyss\n```",
                colour=0x586165
            )
            embed.set_author(name="abyss help", icon_url=ctx.me.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            return

        if action == "set":
            if not ctx.author.guild_permissions.administrator:
                embed = discord.Embed(
                    description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: You need to be an administrator to use this command.",
                    colour=0xfa0505
                )
                await ctx.reply(embed=embed, mention_author=False)
                return

            if args:
                self.j2c_channel_ids[guild_id] = int(args)
                await ctx.message.add_reaction("👍")
            return

        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: You need to be in a VC to use this command.",
                colour=0xfbff00
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        voice_channel = ctx.author.voice.channel

        if action == "claim":
            if guild_id in self.voice_channel_owners and voice_channel.id in self.voice_channel_owners[guild_id]:
                if self.voice_channel_owners[guild_id][voice_channel.id] not in [m.id for m in voice_channel.members]:
                    self.voice_channel_owners[guild_id][voice_channel.id] = ctx.author.id
                    await ctx.message.add_reaction("<:abyssclaim:1281223707687260190>")
                else:
                    embed = discord.Embed(
                        description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: Cannot claim this VC.",
                        colour=0xfbff00
                    )
                    await ctx.reply(embed=embed, mention_author=False)
            return

        if guild_id not in self.voice_channel_owners or voice_channel.id not in self.voice_channel_owners[guild_id] or self.voice_channel_owners[guild_id][voice_channel.id] != ctx.author.id:
            embed = discord.Embed(
                description=f"<:botdecline:1280951104603033650> | {ctx.author.mention}: You are not the owner of this VC.",
                colour=0xfa0505
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        if action == "rename" and args:
            await voice_channel.edit(name=args)
            embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Your **voice channel** has been renamed to `{args}`", colour=0x56d04e)
            await ctx.send(embed=embed)

        elif action == "lock":
            await voice_channel.set_permissions(ctx.guild.default_role, connect=False)
            embed = discord.Embed(description=f"<:abysslock:1281007638762618940> | {ctx.author.mention}: Your **voice channel** has been locked", colour=0xafc125)
            await ctx.send(embed=embed)

        elif action == "unlock":
            await voice_channel.set_permissions(ctx.guild.default_role, connect=True)
            embed = discord.Embed(description=f"<:abyssunlock:1281007617224741002> | {ctx.author.mention}: Your **voice channel** has been locked", colour=0xafc125)
            await ctx.send(embed=embed)

        elif action == "transfer" and args:
            member = ctx.guild.get_member(int(args.strip('<@!>')))
            if member:
                self.voice_channel_owners[guild_id][voice_channel.id] = member.id
                embed = discord.Embed(
                    description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Ownership transferred to {member.mention}.",
                    colour=0x56d04e
                )
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: User not found.",
                    colour=0xfbff00
                )
                await ctx.send(embed=embed)

        elif action == "kick" and args:
            member = ctx.guild.get_member(int(args.strip('<@!>')))
            if member and member in voice_channel.members:
                await member.move_to(None)
                await voice_channel.set_permissions(member, connect=False)
                embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Removed **connect permissions** from {member.mention}", colour=0x56d04e)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: User not found.",
                    colour=0xfbff00
                )
                await ctx.reply(embed=embed, mention_author=False)

        elif action == "allow" and args:
            member = ctx.guild.get_member(int(args.strip('<@!>')))
            if member:
                await voice_channel.set_permissions(member, connect=True)
                embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Granted **connect permissions** to {member.mention}", colour=0x56d04e)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: User not found.",
                    colour=0xfbff00
                )
                await ctx.send(embed=embed)

        elif action == "ghost":
            await voice_channel.set_permissions(ctx.guild.default_role, view_channel=False)
            embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Your **voice channel** is no longer visible", colour=0x56d04e)
            await ctx.send(embed=embed)

        elif action == "unghost":
            await voice_channel.set_permissions(ctx.guild.default_role, view_channel=True)
            embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Your **voice channel** is now visible", colour=0x56d04e)
            await ctx.send(embed=embed)

        elif action == "limit" and args:
            try:
                limit = int(args)
                if limit < 0 or limit > 99:
                    raise ValueError("Limit must be between 0 and 99.")

                await voice_channel.edit(user_limit=limit)
                embed = discord.Embed(description=f"<:botapprove:1280951128137400423> | {ctx.author.mention}: Your **voice channel** is now limited to `{limit}` users", colour=0x56d04e)
                await ctx.send(embed=embed)
            except ValueError:
                embed = discord.Embed(
                    description=f"<:boterror:1280951150840909894> | {ctx.author.mention}: Please provide a number between `0` and `99`",
                    colour=0xfbff00
                )
                await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(VCManager(bot))
