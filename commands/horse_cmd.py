import discord
from discord import app_commands

from random import random,choice

from bot import command_tree, client
from config import VGDCServerId

COMMONHORSES = []
RAREHORSE = []
SRHORSE = []
SSRHORSE = []


@command_tree.command(
	name="horse",
	description="Set Game Lab status to open",
	guild=discord.Object(id=VGDCServerId)
)
@app_commands.checks.has_permissions(manage_messages=True)
async def horse(interaction: discord.Interaction):

    roll = random() * 100
    if roll < 0.9:
        pull = choice(SSRHORSE)
        rarity = "SSR"
    elif roll < 7:
        pull = choice(SRHORSE)
        rarity = "SR"
    elif roll < 25:
        pull = choice(RAREHORSE)
        rarity = "R"
    else:
        pull = choice(COMMONHORSES)
        rarity = "COMMON"
    
    channel = interaction.channel
    embed = discord.Embed(
            title="Horse",
            description="Here's your random horse roll!",
            color=0xE74C3C
        )
    embed.add_field(
        name="Rarity",
        value=rarity,
        inline=False
    )
    embed.add_field(
        name="Horse",
        value=pull,
        inline=False
    )

        
    embed.set_footer(text="Bjorn's Random Horse Rolls")
    await channel.send(
        embed = embed
    )