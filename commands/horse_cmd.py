import discord
from discord import app_commands

from random import random,choice,randrange
from pathlib import Path
from PIL import Image, ImageDraw,ImageFont
import numpy as np
import os

from bot import command_tree, client
from config import VGDCServerId

FRAMEPATH = "horse_images/"
HORSEPATH = "horse_images/"
HORSES = ["horse_base_A.png", "horse_base_B.png"]


@command_tree.command(
	name="horse",
	description="Set Game Lab status to open",
	guild=discord.Object(id=VGDCServerId)
)
async def horse(interaction: discord.Interaction):

    user = interaction.user.name
    
    # Determine rarity
    roll = random() * 100
    if roll < 0.05:
        rarity = "SSR+"
        r_num = 7
        frame = Path(FRAMEPATH +"horse_ssrplus.png")
    elif roll < 0.3:
        rarity = "SSR"
        r_num = 6
        frame = Path(FRAMEPATH +"horse_ssr.png")
    elif roll < 1.2:
        rarity = "SR"
        r_num = 5
        frame = Path(FRAMEPATH +"horse_sr.png")
    elif roll < 4:
        rarity = "UR"
        r_num = 4
        frame = Path(FRAMEPATH +"horse_ur.png")
    elif roll < 10:
        rarity = "Rare"
        r_num = 3
        frame = Path(FRAMEPATH +"horse_rare.png")
    elif roll < 25:
        rarity = "Uncommon"
        r_num = 2
        frame = Path(FRAMEPATH +"horse_uncommon.png")
    elif roll < 45:
        rarity = "Common++"
        r_num = 1
        frame = Path(FRAMEPATH +"horse_commonplus.png")
    else:
        rarity = "Common"
        r_num = 0
        frame = Path(FRAMEPATH +"horse_common.png")

    isShiny = random() * 100 < 1


    # Randomly generated horse image
    horseBase = randrange(1, len(HORSES)+1)
    horseImgPath = Path(HORSEPATH + HORSES[horseBase-1])

    horseImg = Image.open(horseImgPath)

    horseImg = horseImg.convert('RGBA')
    data = horseImg.get_flattened_data()

    if horseBase==1:
        r1a, g1a, b1a, r1b, g1b, b1b = 175,58,58,95,21,21
    elif horseBase==2:
        r1a, g1a, b1a, r1b, g1b, b1b = 229,106,106,130,62,75
    
    r2a,g2a,b2a,a2a = randrange(20,240), randrange(20,240), randrange(20,240), 255
    r2b,g2b,b2b,a2b = int(r2a * 0.2), int(g2a * 0.2), int(b2a * 0.2), 255
    # r2a,g2a,b2a,a2a = 45,45,45, 255
    # r2b,g2b,b2b,a2b = 20,20,20,255
    primaryColorMask = (r1a,g1a,b1a,255)
    secondaryColorMask = (r1b,g1b,b1b,255)
    new_img = []
    for cell in data:
        if cell[0]==r1a and cell[1]==g1a and cell[2]==b1a:
            new_img.append((r2a,g2a,b2a,a2a))
        elif cell[0]==r1b and cell[1]==g1b and cell[2]==b1b:
            new_img.append((r2b,g2b,b2b,a2b))
        else:
            new_img.append((cell[0],cell[1],cell[2],cell[3]))

    horseImg.putdata(new_img)
    number = int(f"{r_num}{horseBase}{g2a}{b2a}{"0" if isShiny else "8"}{r2a}")
    frameImg = Image.open(frame)
    frameImg.alpha_composite(horseImg, (int((512 - horseImg.width)/2), int((512 - horseImg.height)/2) + 20))

    editedImage = ImageDraw.Draw(frameImg)
    editedImage.text((512-130, 8), f"#{number}", font=ImageFont.truetype('Figtree-VariableFont_wght.ttf', 20), fill=(255,255,255), stroke_width=0.8, spacing=6, align="center")
    editedImage.text((10, 512-16), f"Created using Bjorn Bot. This horse was rolled by {user}", font=ImageFont.truetype('Figtree-VariableFont_wght.ttf',12), fill=(255,255,255), stroke_width=0.2, spacing=4,align="left")
    if isShiny:
        shinyImg = Image.open(Path(FRAMEPATH + "horse_shiny_overlay.png"))
        frameImg.alpha_composite(shinyImg, (0,0))

    frameImg.save(Path("output.png"))

    # Determine Horse Stats
    speed = "□" * (r_num + randrange(0,6))
    affection = "□" * (r_num + randrange(-1, 4))

    if speed == "":
        speed = "□"
    if affection == "":
        affection = "□"
    
    # Send Message
    channel = interaction.channel

    file = discord.File("output.png", filename="image.png")

    embed = discord.Embed(
        title="🎲 Will Horse Gacha",
        description=f"Here's your random horse roll, {user}!",
        color=0xE74C3C
    )
    embed.add_field(
        name="Rarity",
        value=rarity,
        inline=False
    )
    embed.add_field(
        name="Speed",
        value=speed,
        inline=False
    )
    embed.add_field(
        name="Affection",
        value=affection,
        inline=False
    )
    embed.set_image(url="attachment://image.png")

    await channel.send(
        file = file,
        embed = embed
    )
    await interaction.followup.send(
        f"✅ Horse created!",
        ephemeral=True
    )