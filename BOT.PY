import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("NO TOKEN")

WELCOME_CHANNEL_ID = 1454399890405851198
INFO_CHANNEL_ID = WELCOME_CHANNEL_ID  # puedes cambiarlo si quieres otro canal

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# STATUS (MIEMBROS + ONLINE + FIRMA)
# =========================
async def status_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():

        total_members = 0
        online_members = 0

        for guild in bot.guilds:

            await guild.chunk()

            total_members += guild.member_count

            for member in guild.members:
                if member.status != discord.Status.offline:
                    online_members += 1

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{total_members} miembros | {online_members} online • deve xDavid"
            )
        )

        await asyncio.sleep(60)

# =========================
# PANEL INFO EN CANAL
# =========================
async def info_panel_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():

        total_members = 0
        online_members = 0

        for guild in bot.guilds:

            await guild.chunk()

            total_members += guild.member_count

            for member in guild.members:
                if member.status != discord.Status.offline:
                    online_members += 1

        channel = bot.get_channel(INFO_CHANNEL_ID)

        if channel:
            embed = discord.Embed(
                title="📊 ESTADO DEL SERVIDOR",
                description=f"""
👥 **Miembros totales:** {total_members}
🟢 **En línea:** {online_members}

✍️ deve xDavid
""",
                color=0x8a2be2
            )

            await channel.purge(limit=1)
            await channel.send(embed=embed)

        await asyncio.sleep(60)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"BOT ACTIVO: {bot.user}")

    for guild in bot.guilds:
        await guild.chunk()

    asyncio.create_task(status_loop())
    asyncio.create_task(info_panel_loop())

# =========================
# WELCOME (TU INFORMACIÓN COMPLETA)
# =========================
@bot.event
async def on_member_join(member):

    print(f"JOIN: {member}")

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if not channel:
        print("❌ No se encontró el canal de welcome")
        return

    embed = discord.Embed(
        title="🔥 BIENVENIDO A GUATE XITER 🔥",
        description=f"""
👤 {member.mention}

Guate Xiter  
GX  
🔥 GUATE XITER 🔥  

✅ 100% confiables y seguros  
Trabajamos con total transparencia, brindando confianza y atención real a cada cliente.  

⚡ Servicio rápido y eficiente  
Entregas inmediatas, soporte activo y asistencia cuando lo necesites.  

🛡️ Seguridad garantizada  
Protegemos a nuestros clientes en todo momento para ofrecer una experiencia segura y estable.  

🏆 Top en confianza  
Cada día más personas nos eligen gracias a nuestra reputación y calidad de servicio.  

💬 Atención personalizada  
Siempre estamos disponibles para ayudarte y resolver cualquier duda.  

📢 REVISA NUESTROS CANALES OFICIALES  

📌 REGLAS  
• Respeta a todos los miembros del servidor.  
• No hacerse pasar por otras personas.  
• No usar nombres o imágenes inapropiadas.  
• Evita spam.  
• Mantén respeto.  

🔥 GUATE XITER — Calidad, confianza y seguridad.  

📎 CANALES:  
✦🎟️ Bypass UID:  
https://discord.com/channels/1454399889604608064/1484371103605461012  
https://discord.com/channels/1454399889604608064/1486218759080378560  

🌐 WEB:  
https://guate-xiter-store.vercel.app/
""",
        color=0x8a2be2
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="deve xDavid")

    await channel.send(embed=embed)

# =========================
# RUN
# =========================
bot.run(TOKEN)