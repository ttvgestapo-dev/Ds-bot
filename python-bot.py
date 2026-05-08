import os
import discord
from discord.ext import commands
import boto3
from dotenv import load_dotenv
import asyncio
import random
from duckduckgo_search import DDGS


# Cargar variables de entorno
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
REGION = 'us-east-1'
INSTANCE_ID = os.getenv('INSTANCE_ID')

# Configurar conexión con AWS
ec2 = boto3.client('ec2', 
                   region_name=REGION,
                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                   aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

# Configurar el Bot de Discord con los permisos (Intents)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado exitosamente como {bot.user}')

@bot.command(name='prender')
async def prender_server(ctx):
    # Aviso inicial de que el proceso es largo
    await ctx.send("⏳ Contactando a Pablo... Iniciando el Rape Mode.\n⚠️ **Aviso:** El modpack ATM10 es pesado y el servidor tardará aproximadamente **6 minutos y 30 segundos** en estar listo para jugar.")
    
    try:
        # 1. Mandar a encender la instancia
        ec2.start_instances(InstanceIds=[INSTANCE_ID])
        await ctx.send("✅ Instancia iniciada. Obteniendo IP")
        
        # 2. Esperar 5 segundos para la IP
        await asyncio.sleep(5)
        
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        ip_publica = response['Reservations'][0]['Instances'][0].get('PublicIpAddress')
        
        if ip_publica:
            await ctx.send(f"🌐 IP obtenida: `{ip_publica}`\n⏳ Me quedaré esperando el resto del tiempo de carga. Te avisaré apenas pasen los 6:30 min.")
        else:
            await ctx.send("⚠️ AWS aún no suelta la IP, pero el servidor sigue cargando. Avisaré al terminar los 6:30 min.")

        # 3. Esperar el resto del tiempo para completar los 6:30 min (390 segundos)
        # Como ya esperamos 15, restamos: 390 - 15 = 375 segundos
        await asyncio.sleep(285)
        
        # 4. Aviso final de servidor listo
        mencion = "@everyone" # Puedes cambiar esto por un rol si prefieres
        await ctx.send(f"🔥 {mencion} **¡EL SERVIDOR ESTA LISTO, TODOS A VIOLAR!**")
            
    except Exception as e:
        await ctx.send(f"❌ Error al iniciar: {e}")

@bot.command(name='apagar')
async def apagar_server(ctx):
    await ctx.send("⏳ Apagando el servidor, Pablo no contesto...")
    try:
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
        await ctx.send("💤 Servidor apagado. ¡Horas ahorradas con éxito!")
    except Exception as e:
        await ctx.send(f"❌ Error al apagar: {e}")

@bot.command(name='estado')
async def estado_server(ctx):
    try:
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        estado = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        # Le damos un poco de formato visual dependiendo del estado
        if estado == 'running':
            mensaje = "🟢 El servidor está **CUCKEANDO** mientras Dieguito está en la Muni sentado haciendo **NADA!!**!"
        elif estado == 'stopped':
            mensaje = "🔴 El servidor está **APAGADO** y dieguito fue violado!!."
        elif estado == 'pending':
            mensaje = "🟡 El servidor se está encendiendo en este momento."
        elif estado == 'stopping':
            mensaje = "🟡 El servidor se está apagando."
        else:
            mensaje = f"⚪ Estado actual: {estado}"
            
        await ctx.send(mensaje)
    except Exception as e:
        await ctx.send(f"❌ Error al consultar estado: {e}")

@bot.command(name='Cp')
async def buscar_imagen(ctx, *, busqueda: str = "Mia Khalifa"):
    # El bot avisa que está buscando
    await ctx.send(f"👀 Buscando en la web algo aleatorio sobre: **{busqueda}**... 👀")
    
    try:
        # Usamos DuckDuckGo para buscar las imágenes de forma silenciosa
        with DDGS() as ddgs:
            # Traemos los primeros 20 resultados de la búsqueda
            resultados = list(ddgs.images(busqueda, max_results=20))
        
        # Si la búsqueda no arroja resultados
        if not resultados:
            await ctx.send(f"❌ No encontré ninguna imagen para '{busqueda}'. Intenta con otra palabra.")
            return
            
        # Elegimos un resultado al azar de la lista
        imagen_elegida = random.choice(resultados)
        url_imagen = imagen_elegida['image']
        
        # Armamos el mensaje visual
        embed = discord.Embed(
            title=f"🔎 Búsqueda aleatoria: {busqueda}", 
            color=discord.Color.dark_grey() 
        )
        embed.set_image(url=url_imagen)
        embed.set_footer(text="Fuente: Extracción web de imágenes")
        
        # Enviamos la imagen al canal
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error al extraer la imagen: {e}")

# Iniciar el bot
bot.run(DISCORD_TOKEN)