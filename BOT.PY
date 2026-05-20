import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import asyncio
import random
from collections import defaultdict

# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ No se encontró DISCORD_TOKEN")

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# DATA
# =========================
FILE = "data.json"

def load():
    try:
        with open(FILE, "r") as f:
            data = json.load(f)

        data.setdefault("autoroles", {
            "user": [],
            "bot": []
        })

        return data

    except:
        return {
            "autoroles": {
                "user": [],
                "bot": []
            }
        }

def save():
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load()

# =========================
# SYSTEMS
# =========================
xp = defaultdict(int)
level = defaultdict(int)
money = defaultdict(int)
spam = defaultdict(list)
join_tracker = []

welcome_cache = set()

# ⚠️ CANAL WELCOME
LOG_CHANNEL_ID = 1454399890405851198

# =========================
# SETTINGS
# =========================
settings = {
    "antilink": True,
    "antispam": True
}

# =========================
# CACHE
# =========================
async def clear_welcome_cache(user_id):
    await asyncio.sleep(60)
    welcome_cache.discard(user_id)

# =========================
# STATUS LOOP
# =========================
async def status_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        total = sum(
            g.member_count
            for g in bot.guilds
        )

        online = sum(
            1
            for g in bot.guilds
            for m in g.members
            if m.status != discord.Status.offline
        )

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{total} miembros | {online} online"
            )
        )

        await asyncio.sleep(60)

# =========================
# READY
# =========================
@bot.event
async def on_ready():

    print("=" * 40)
    print(f"✅ BOT ACTIVO: {bot.user}")
    print("=" * 40)

    try:
        synced = await bot.tree.sync()

        print(
            f"✅ Slash Commands: {len(synced)}"
        )

    except Exception as e:
        print(f"❌ Error: {e}")

    asyncio.create_task(
        status_loop()
    )

# =========================
# MEMBER JOIN
# =========================
@bot.event
async def on_member_join(member):

    if member.id in welcome_cache:
        return

    welcome_cache.add(member.id)

    asyncio.create_task(
        clear_welcome_cache(member.id)
    )

    # =========================
    # ANTI RAID
    # =========================
    now = datetime.datetime.utcnow().timestamp()

    join_tracker.append(now)

    join_tracker[:] = [
        t for t in join_tracker
        if now - t < 10
    ]

    if len(join_tracker) >= 5:

        for c in member.guild.text_channels:

            try:
                await c.set_permissions(
                    member.guild.default_role,
                    send_messages=False
                )

            except:
                pass

    # =========================
    # AUTO ROLE
    # =========================
    tipo = "bot" if member.bot else "user"

    roles = data["autoroles"].get(
        tipo,
        []
    )

    if not isinstance(roles, list):
        roles = [roles]

    for role_id in roles:

        try:
            role = discord.utils.get(
                member.guild.roles,
                id=int(role_id)
            )

            if role:

                await member.add_roles(
                    role,
                    reason="Autorole"
                )

        except:
            pass

    # =========================
    # WELCOME
    # =========================
    ch = member.guild.get_channel(
        LOG_CHANNEL_ID
    )

    if ch:

        embed = discord.Embed(
            title="🔥 BIENVENIDO A GUATE XITER 🔥",
            description=f"""
👤 {member.mention}

💀 Aquí no jugamos
🚀 Aquí se sube de nivel
🏆 Aquí se domina
⚔️ Solo sobreviven los activos
""",
            color=0xff0000
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_image(
            url="https://i.postimg.cc/nV2JGZmr/file-00000000c9ec71f59259d589e645e4e1.png"
        )

        await ch.send(embed=embed)

# =========================
# MESSAGE SYSTEM
# =========================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    uid = str(message.author.id)

    # =========================
    # XP SYSTEM
    # =========================
    xp[uid] += 5

    if xp[uid] >= 100:

        xp[uid] = 0

        level[uid] += 1

        reward = random.randint(50, 150)

        money[uid] += reward

        embed = discord.Embed(
            title="🏆 LEVEL UP",
            description=f"""
🎉 {message.author.mention}

🚀 Nivel: {level[uid]}
💰 Dinero: {reward}
""",
            color=0xff0000
        )

        embed.set_thumbnail(
            url=message.author.display_avatar.url
        )

        await message.channel.send(
            embed=embed
        )

    # =========================
    # ANTI SPAM
    # =========================
    if settings["antispam"]:

        now = datetime.datetime.utcnow().timestamp()

        spam[uid].append(now)

        spam[uid] = [
            t for t in spam[uid]
            if now - t < 5
        ]

        if len(spam[uid]) > 5:

            try:
                await message.delete()

                embed = discord.Embed(
                    title="🛡 ANTI SPAM",
                    description=f"{message.author.mention} spam detectado",
                    color=0xff0000
                )

                embed.set_image(
                    url="https://media.tenor.com/7B8wG8-6hSAAAAAC/anime.gif"
                )

                await message.channel.send(
                    embed=embed
                )

            except:
                pass

            return

    # =========================
    # ANTI LINK
    # =========================
    if settings["antilink"]:

        if (
            "http" in message.content.lower()
            or
            "discord.gg" in message.content.lower()
        ):

            try:
                await message.delete()

                embed = discord.Embed(
                    title="🚫 LINK BLOQUEADO",
                    description=f"{message.author.mention} links no permitidos",
                    color=0xff0000
                )

                embed.set_image(
                    url="https://media.tenor.com/jhJ2aXhD6wAAAAAC/anime-ban.gif"
                )

                await message.channel.send(
                    embed=embed
                )

            except:
                pass

            return

    # =========================
    # ANTI NSFW
    # =========================
    nsfw_words = [
        "porn",
        "xxx",
        "nsfw",
        "hentai"
    ]

    if any(
        word in message.content.lower()
        for word in nsfw_words
    ):

        try:
            await message.delete()

            embed = discord.Embed(
                title="📸 NSFW BLOQUEADO",
                description=f"{message.author.mention} contenido prohibido",
                color=0xff0000
            )

            embed.set_image(
                url="https://media.tenor.com/qDEZGcFwVasAAAAC/anime-ban.gif"
            )

            await message.channel.send(
                embed=embed
            )

        except:
            pass

        return

    await bot.process_commands(message)

# =========================
# PING
# =========================
@bot.tree.command(name="ping")
async def ping(interaction):

    await interaction.response.send_message(
        f"🏓 {round(bot.latency * 1000)}ms"
    )

# =========================
# INFO
# =========================
@bot.tree.command(name="info")
async def info(interaction):

    g = interaction.guild

    online = sum(
        1
        for m in g.members
        if m.status != discord.Status.offline
    )

    embed = discord.Embed(
        title="📊 INFO SERVER",
        color=0xff0000
    )

    embed.add_field(
        name="👥 Miembros",
        value=g.member_count
    )

    embed.add_field(
        name="🟢 Online",
        value=online
    )

    embed.add_field(
        name="🚀 Boosts",
        value=g.premium_subscription_count
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# RANK
# =========================
@bot.tree.command(name="rank")
async def rank(
    interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    uid = str(member.id)

    embed = discord.Embed(
        title="🏆 RANK",
        color=0xff0000
    )

    embed.add_field(
        name="Nivel",
        value=level[uid]
    )

    embed.add_field(
        name="XP",
        value=xp[uid]
    )

    embed.add_field(
        name="Dinero",
        value=money[uid]
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# LEADERBOARD
# =========================
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction):

    top = sorted(
        level.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    desc = ""

    for i, user in enumerate(top, start=1):

        member = interaction.guild.get_member(
            int(user[0])
        )

        if member:

            desc += (
                f"#{i} 👑 "
                f"{member.mention} "
                f"- Nivel {user[1]}\n"
            )

    embed = discord.Embed(
        title="🏆 TOP LEVELS",
        description=desc,
        color=0xff0000
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# BALANCE
# =========================
@bot.tree.command(name="balance")
async def balance(interaction):

    uid = str(interaction.user.id)

    await interaction.response.send_message(
        f"💰 Dinero: {money[uid]}"
    )

# =========================
# WORK
# =========================
@bot.tree.command(name="work")
async def work(interaction):

    uid = str(interaction.user.id)

    amount = random.randint(100, 500)

    money[uid] += amount

    await interaction.response.send_message(
        f"💵 Ganaste {amount}"
    )

# =========================
# CLEAR
# =========================
@bot.tree.command(name="clear")
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def clear(
    interaction,
    amount: int
):

    await interaction.channel.purge(
        limit=amount
    )

    await interaction.response.send_message(
        f"🧹 {amount} mensajes borrados",
        ephemeral=True
    )

# =========================
# BAN
# =========================
@bot.tree.command(name="ban")
@app_commands.checks.has_permissions(
    ban_members=True
)
async def ban(
    interaction,
    member: discord.Member
):

    await member.ban()

    await interaction.response.send_message(
        f"🔨 {member} baneado"
    )

# =========================
# KICK
# =========================
@bot.tree.command(name="kick")
@app_commands.checks.has_permissions(
    kick_members=True
)
async def kick(
    interaction,
    member: discord.Member
):

    await member.kick()

    await interaction.response.send_message(
        f"👢 {member} kickeado"
    )

# =========================
# TIMEOUT
# =========================
@bot.tree.command(name="timeout")
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def timeout(
    interaction,
    member: discord.Member,
    minutes: int
):

    until = (
        discord.utils.utcnow()
        +
        datetime.timedelta(minutes=minutes)
    )

    await member.timeout(
        until
    )

    await interaction.response.send_message(
        f"⏳ {member.mention} timeout {minutes}m"
    )

# =========================
# VERIFY
# =========================
@bot.tree.command(name="verify")
async def verify(interaction):

    role = discord.utils.get(
        interaction.guild.roles,
        name="Verified"
    )

    if not role:

        return await interaction.response.send_message(
            "❌ crea un rol llamado Verified"
        )

    await interaction.user.add_roles(role)

    await interaction.response.send_message(
        "✅ Verificado"
    )

# =========================
# TICKET
# =========================
@bot.tree.command(name="ticket")
async def ticket(interaction):

    overwrites = {

        interaction.guild.default_role:
        discord.PermissionOverwrite(
            read_messages=False
        ),

        interaction.user:
        discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        )
    }

    channel = await interaction.guild.create_text_channel(
        name=f"ticket-{interaction.user.name}",
        overwrites=overwrites
    )

    await channel.send(
        f"🎫 Ticket creado para {interaction.user.mention}"
    )

    await interaction.response.send_message(
        f"✅ {channel.mention}",
        ephemeral=True
    )

# =========================
# ANTI LINK
# =========================
@bot.tree.command(name="antilink")
@app_commands.checks.has_permissions(
    administrator=True
)
async def antilink(
    interaction,
    estado: str
):

    estado = estado.lower()

    if estado not in ["on", "off"]:

        return await interaction.response.send_message(
            "usa: on/off",
            ephemeral=True
        )

    settings["antilink"] = (
        estado == "on"
    )

    await interaction.response.send_message(
        f"🔗 AntiLink {estado}"
    )

# =========================
# ANTI SPAM
# =========================
@bot.tree.command(name="antispam")
@app_commands.checks.has_permissions(
    administrator=True
)
async def antispam(
    interaction,
    estado: str
):

    estado = estado.lower()

    if estado not in ["on", "off"]:

        return await interaction.response.send_message(
            "usa: on/off",
            ephemeral=True
        )

    settings["antispam"] = (
        estado == "on"
    )

    await interaction.response.send_message(
        f"🛡 AntiSpam {estado}"
    )

# =========================
# AUTOROLE
# =========================
class RoleSelect(discord.ui.Select):

    def __init__(self, roles, tipo):

        self.tipo = tipo

        options = [

            discord.SelectOption(
                label=r.name,
                value=str(r.id)
            )

            for r in roles
            if r.name != "@everyone"

        ][:25]

        super().__init__(
            placeholder="Selecciona roles",
            options=options,
            min_values=1,
            max_values=len(options)
        )

    async def callback(
        self,
        interaction
    ):

        data["autoroles"][self.tipo] = [

            int(v)
            for v in self.values
        ]

        save()

        await interaction.response.send_message(
            "✅ Autoroles guardados",
            ephemeral=True
        )

class RoleView(discord.ui.View):

    def __init__(self, roles, tipo):

        super().__init__(timeout=60)

        self.add_item(
            RoleSelect(roles, tipo)
        )

@bot.tree.command(name="autorole_add")
async def autorole_add(
    interaction,
    tipo: str
):

    if tipo not in ["user", "bot"]:

        return await interaction.response.send_message(
            "❌ usa user o bot",
            ephemeral=True
        )

    await interaction.response.send_message(
        "Selecciona roles",
        view=RoleView(
            interaction.guild.roles,
            tipo
        ),
        ephemeral=True
    )

# =========================
# RUN
# =========================
bot.run(TOKEN)