import discord
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")  # this will come from Railway

intents = discord.Intents.default()
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

def owner_only(interaction: discord.Interaction):
    return interaction.user.id == interaction.guild.owner_id

@tree.command(name="dm", description="DM members with cooldown")
@app_commands.check(owner_only)
@app_commands.describe(
    target="all or online",
    content="Message to send"
)
async def dm(interaction: discord.Interaction, target: str, content: str):
    await interaction.response.send_message("Sending DMs...", ephemeral=True)

    members = []
    if target == "all":
        members = interaction.guild.members
    elif target == "online":
        members = [m for m in interaction.guild.members if m.status != discord.Status.offline]

    count = 0
    for member in members:
        if member.bot:
            continue
        try:
            await member.send(content)
            count += 1
            await asyncio.sleep(10)
        except:
            pass

    await interaction.followup.send(f"DMs sent to {count} members", ephemeral=True)

@dm.error
async def dm_error(interaction, error):
    from discord import app_commands
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("Only server owner can use this", ephemeral=True)

client.run(TOKEN)
