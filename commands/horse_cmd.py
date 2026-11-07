import discord
from discord import app_commands

from random import random,choice,randrange
from pathlib import Path
from PIL import Image, ImageDraw,ImageFont
import numpy as np
import os
import sqlite3

from bot import command_tree, client
from config import VGDCServerId

FRAMEPATH = "horse_images/"
HORSEPATH = "horse_images/"
HORSES = ["horse_base_A.png", "horse_base_B.png"]
EMBEDCOLORS = [0xfca19c, 0x9ba09c, 0x9e976e, 0x88e894, 0x68d6d2, 0xfcf683,0xd69cfc, 0x32fcc3,0xfc8fd1,0x37fcc1]


@command_tree.command(
	name="horse",
	description="Generate a horse :D",
	guild=discord.Object(id=VGDCServerId)
)
async def horse(interaction: discord.Interaction):

    await interaction.response.defer()
    user = interaction.user.name
    user_id = interaction.user.id

    # Points check
    connection = sqlite3.connect("points.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT num_points FROM points WHERE user_id={user_id}")
    item = cursor.fetchall()
    if len(item)!=1:
        embed = discord.Embed(
            title="Not Enough Points!",
            description=f"Uh oh, you don't have enough points to roll for a horse. You need 10 points.",
            color=0xFFB444
        )
        await interaction.followup.send(
            embed=embed
        )
        return

    points = item[0][0]
    if points >= 10:
        points -= 10
        cursor.execute(f"UPDATE points SET num_points={points} WHERE user_id={user_id}")
        connection.commit()
        connection.close()
    else:
        connection.commit()
        connection.close()
        embed = discord.Embed(
            title="Not Enough Points!",
            description=f"Uh oh, you don't have enough points to roll for a horse.",
            color=0xFFB444
        )
        embed.add_field(
            name="Your Points",
            value=points
        )
        await interaction.followup.send(
            embed=embed
        )
        return

    
    # Determine rarity
    roll = random() * 100
    if roll < 0.003:
        rarity = "SSR++ ☆☆☆☆☆☆"
        r_num = 9
        frame = Path(FRAMEPATH +"horse_ssrplusplus.png")
    elif roll < 0.05:
        rarity = "SSR+ ☆☆☆☆"
        r_num = 8
        frame = Path(FRAMEPATH +"horse_ssrplus.png")
    elif roll < 0.3:
        rarity = "SSR ☆☆☆"
        r_num = 7
        frame = Path(FRAMEPATH +"horse_ssr.png")
    elif roll < 1.2:
        rarity = "SR ☆☆"
        r_num = 6
        frame = Path(FRAMEPATH +"horse_sr.png")
    elif roll < 4:
        rarity = "UR ☆"
        r_num = 5
        frame = Path(FRAMEPATH +"horse_ur.png")
    elif roll < 10:
        rarity = "Rare ☆"
        r_num = 4
        frame = Path(FRAMEPATH +"horse_rare.png")
    elif roll < 25:
        rarity = "Uncommon"
        r_num = 3
        frame = Path(FRAMEPATH +"horse_uncommon.png")
    elif roll < 45:
        rarity = "Common++"
        r_num = 2
        frame = Path(FRAMEPATH +"horse_commonplus.png")
    elif roll > 99.95:
        rarity = "Super Negative Luck"
        r_num = 0
        frame = Path(FRAMEPATH +"horse_nl.png")
    else:
        rarity = "Common"
        r_num = 1
        frame = Path(FRAMEPATH +"horse_common.png")

    isShiny = random() * 100 < 1

    # Randomly generated horse image
    horseBase = randrange(1, len(HORSES)+1)
    horseImgPath = Path(HORSEPATH + HORSES[horseBase-1])

    horseImg = Image.open(horseImgPath)

    horseImg = horseImg.convert('RGBA')
    data = horseImg.get_flattened_data()

    if horseBase==1:
        r1a, g1a, b1a, r1b, g1b, b1b, r1c, g1c, b1c = 175,58,58,95,21,21, 193, 176, 43
        r2c, g2c, b2c,a2c = randrange(20,240), randrange(20,240), randrange(20,240), 255
    elif horseBase==2:
        r1a, g1a, b1a, r1b, g1b, b1b = 229,106,106,130,62,75
    
    r2a,g2a,b2a,a2a = randrange(20,240), randrange(20,240), randrange(20,240), 255
    r2b,g2b,b2b,a2b = int(r2a * 0.5), int(g2a * 0.5), int(b2a * 0.5), 255
    
    primaryColorMask = (r1a,g1a,b1a,255)
    secondaryColorMask = (r1b,g1b,b1b,255)
    new_img = []
    for cell in data:
        if cell[0]==r1a and cell[1]==g1a and cell[2]==b1a:
            new_img.append((r2a,g2a,b2a,a2a))
        elif cell[0]==r1b and cell[1]==g1b and cell[2]==b1b:
            new_img.append((r2b,g2b,b2b,a2b))
        elif horseBase==1 and cell[0]==r1c and cell[1]==g1c and cell[2]==b1c:
            new_img.append((r2c,g2c,b2c,a2c))
        else:
            new_img.append((cell[0],cell[1],cell[2],cell[3]))

    horseImg.putdata(new_img)
    number = int(f"{r_num}{horseBase}{g2a:03d}{b2a:03d}{"0" if isShiny else "8"}{r2a:03d}")
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
    speed = r_num + randrange(0,6)
    affection = r_num + randrange(-1, 4)
    strength = int(r_num/3)

    if speed < 1:
        speed = 1
    if affection < 1:
        affection = 1

    horseName = choice(["W","B","Tr","D","Qu"]) + "i" + ("l" * randrange(1,7))

    # Explosion chance
    isExploded = random() * 100 < (2+affection)

    if isExploded:
        embed = discord.Embed(
            title="Your Will Horse Exploded",
            description=f"Oh no, something went wrong :(\nYour {rarity} horse, {horseName}, exploded before it could be sent to you.",
            color=0xFFB444
        )
        embed.add_field(
            name="Remaining Points",
            value=points
        )
        await interaction.followup.send(
            embed=embed
        )
        return
    
    # Send Message

    file = discord.File("output.png", filename="image.png")

    embed = discord.Embed(
        title="🎲 Will Horse Gacha ✮⋆˙",
        description=f"Here's your random horse roll!",
        color=EMBEDCOLORS[r_num]
    )
    embed.add_field(
        name="Rarity",
        value=rarity,
        inline=True
    )
    embed.add_field(
        name="Name",
        value = horseName,
        inline=True
    )
    embed.add_field(
        name="Number",
        value = number,
        inline=True
    )
    embed.add_field(
        name="Remaining Points",
        value=points,
        inline=True
    )
    embed.add_field(
        name="Speed",
        value=f"[{"■" * speed}{"☐" * (15-speed)}]",
        inline=False
    )
    embed.add_field(
        name="Affection",
        value=f"[{"♣" * strength}{"♧" * (15-strength)}]",
        inline=False
    )
    embed.add_field(
        name="Strength",
        value=f"[{"♜" * affection}{"♖" * (3-affection)}]",
        inline=False
    )
    embed.set_image(url="attachment://image.png")

    await interaction.followup.send(
        file=file,
        embed=embed
    )

    #print(f"Horse: {number} | Affection: {affection} | isExploded: {isExploded}")

