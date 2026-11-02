import os
import asyncio
from threading import Thread
import discord
from discord import app_commands
from flask import Flask
from groq import Groq

# ==========================================
# 1. SERVIDOR WEB PARA MANTENER VIVO FLY.IO
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return 'Bot Código Penal Federal activo 24/7'

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. CONFIGURACIÓN DE LA IA (GROQ)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY.strip())
        print("¡IA Groq configurada exitosamente!")
    else:
        print("Aviso: GROQ_API_KEY no encontrada en variables de entorno.")
        groq_client = None
except Exception as err:
    print(f"Error al configurar Groq: {err}")
    groq_client = None

# TEXTO COMPLETO OFICIAL DE LOS 77 ARTÍCULOS
CODIGO_PENAL_TEXTO = (
    "CÓDIGO PENAL FEDERAL\n"
    "Art 1: Fuero Común y Federal. Delito toda acción u omisión voluntaria.\n"
    "Art. 4: Conducción temeraria: 2,000 MXN y/o pérdida 3 puntos licencia.\n"
    "Art. 5: Daño a propiedad privada/pública con vehículo: 2,500 MXN y reparación total.\n"
    "Art. 6: No cumplir semáforos o señales de STOP: 500 MXN por cada infracción.\n"
    "Art. 7: Dirección contraria: 3,000 MXN y/o pérdida 1 punto.\n"
    "Art. 8: Conducir bajo efectos de alcohol/sustancias: 2,500 MXN y/o pérdida 6 puntos.\n"
    "Art. 9: Posesión de arma no autorizada en vehículo o disparos al aire: Art. 48 + 4,000 MXN e incautación.\n"
    "Art. 10: Exceso de velocidad: 1,500 MXN y retirada 2 puntos.\n"
    "Art. 11: Conducir sin licencia: 4,000 MXN e ingreso a prisión preventiva de 24h.\n"
    "Art. 12: Carreras clandestinas: 6,500 MXN, suspensión licencia y 1 mes de prisión.\n"
    "Art. 13: Mal estacionado: 750 MXN (o 1,000 MXN al depósito).\n"
    "Art. 15: No ceder paso a emergencias: 1,500 MXN y retirada licencia 1 mes.\n"
    "Art. 22: Uso de móvil/auriculares conduciendo: 400 MXN y retirada 1 punto.\n"
    "Art. 25: Huir de un accidente de tráfico sin socorrer: 4,700 MXN.\n"
    "Art. 26: Causar accidente mayor: 8,000 MXN y retirada de licencia.\n"
    "Art. 27: Circular sin matrícula: 4,000 MXN y depósito.\n"
    "Art. 30: Agresión verbal (2,000 MXN) / Agresión física (2 años prisión + indemnización 2,000 a 6,000 MXN).\n"
    "Art. 41: Allanamiento de morada (entrar a propiedad ajena o casa sin permiso): 7,000 MXN y 6 meses prisión temporal.\n"
    "Art. 43: Hurto (robo menor / a tienda): 15,000 MXN y 1 año prisión.\n"
    "Art. 44: Asalto con arma blanca: 10,000 MXN y 1 año 6 meses prisión.\n"
    "Art. 45: Asalto con arma de fuego: 20,000 MXN y 2 años prisión.\n"
    "Art. 46: Apropiación con fuerza o intimidación / robo a banco o establecimiento: 16,000 MXN y 2 años prisión.\n"
    "Art. 47: Daños a propiedades del Estado: 25,000 MXN + indemnización.\n"
    "Art. 48: Posesión de arma sin licencia: 17,000 MXN y 1 año prisión.\n"
    "Art. 50: Comercio ilegal de armas: 30,000 MXN y 2 años prisión.\n"
    "Art. 51: Intento de homicidio: 2 años prisión.\n"
    "Art. 54: Homicidio (asesinar/matar persona): 3 años prisión.\n"
    "Art. 55: Homicidio múltiple: 5 años o 3 años por cada víctima adicional.\n"
    "Art. 56: Secuestro: 3 años prisión.\n"
    "Art. 57: Extorsión: 10,000 MXN y 2 años prisión.\n"
    "Art. 58: Amenazas: 7,000 MXN y 1 año prisión.\n"
    "Art. 59: Falsedad documental: 70,000 a 100,000 MXN y 2 años prisión.\n"
    "Art. 60: Transitar sin documentación oficial: 10,000 MXN.\n"
    "Art. 61: Estafa: 12,000 MXN + indemnización.\n"
    "Art. 65: Robo de objeto del Estado: 50,000 MXN y 2 años prisión.\n"
    "Art. 68: Evasión / huida de la autoridad: 9,600 MXN y 1 mes prisión.\n"
    "Art. 69: Soborno a funcionario público: 37,000 MXN y 3 años prisión.\n"
    "Art. 70: Terrorismo: 500,000 MXN y 15 años prisión.\n"
    "Art. 71: Atentar contra integridad física de funcionario / herir a policía: 2 años prisión adicionales."
)

# ==========================================
# 3. MOTOR LOCAL DE RESPALDO RÁPIDO
# ==========================================
def motor_local_rapido(situacion):
    s = situacion.lower()
    articulos = []

    if any(k in s for k in ["velocidad", "rápido", "corriendo"]):
        articulos.append(("Art. 10 - Exceso de velocidad", "1,500 MXN y retirada 2 puntos."))
    if any(k in s for k in ["stop", "semáforo", "luz roja"]):
        articulos.append(("Art. 6 - No cumplir semáforos o señales de STOP", "500 MXN por infracción."))
    if any(k in s for k in ["alcohol", "ebrio", "copas", "drogas"]):
        articulos.append(("Art. 8 - Conducir bajo efectos de alcohol/sustancias", "2,500 MXN y/o pérdida 6 puntos."))
    if any(k in s for k in ["licencia", "permiso", "carnet"]) and not "arma" in s:
        articulos.append(("Art. 11 - Conducir sin licencia", "4,000 MXN e ingreso a prisión preventiva de 24h."))
    if any(k in s for k in ["allanamient", "propiedad", "casa", "meterse"]):
        articulos.append(("Art. 41 - Allanamiento de morada", "7,000 MXN y 6 meses prisión temporal."))
    if any(k in s for k in ["robo", "hurto", "tienda"]):
        articulos.append(("Art. 43 - Hurto (robo menor / a tienda)", "15,000 MXN y 1 año prisión."))
    if any(k in s for k in ["banco", "establecimiento", "fuerza"]):
        articulos.append(("Art. 46 - Apropiación con fuerza o intimidación", "16,000 MXN y 2 años prisión."))
    if any(k in s for k in ["arma", "pistola", "cuchillo", "dar dinero", "soborn"]):
        if "fuego" in s or "pistola" in s:
            articulos.append(("Art. 45 - Asalto con arma de fuego", "20,000 MXN y 2 años prisión."))
        elif "blanca" in s or "cuchillo" in s:
            articulos.append(("Art. 44 - Asalto con arma blanca", "10,000 MXN y 1 año 6 meses prisión."))
        elif "dar dinero" in s or "soborn" in s:
            articulos.append(("Art. 69 - Soborno a funcionario público", "37,000 MXN y 3 años prisión."))
        else:
            articulos.append(("Art. 48 - Posesión de arma sin licencia", "17,000 MXN y 1 año prisión."))
    if any(k in s for k in ["matar", "asesinar", "homicidio", "muerte"]):
        articulos.append(("Art. 54 - Homicidio", "3 años prisión."))
    if any(k in s for k in ["policia", "policía", "agente"]) and any(k in s for k in ["herir", "disparar", "atentar", "golpear"]):
        articulos.append(("Art. 71 - Atentar contra integridad física de funcionario / herir a policía", "2 años prisión adicionales."))

    if not articulos:
        articulos.append(("Art. 1 - Disposición General del Código Penal", "Sujeto a revisión de los hechos por la autoridad competente."))

    lista_art = [f"• {item[0]}" for item in articulos]
    lista_conc = [f"• {item[0]}: {item[1]}" for item in articulos]

    return f"**Artículos aplicables:**\n" + "\n".join(lista_art) + "\n\n**Conclusión:**\nSanciones correspondientes aplicadas:\n" + "\n".join(lista_conc)

def obtener_respuesta_ia(situacion):
    if not situacion or len(situacion.strip()) < 3:
        return motor_local_rapido(situacion)

    if not groq_client:
        return motor_local_rapido(situacion)

    system_prompt = (
        "Eres un asistente legal experto del Código Penal Federal. "
        "Lee la situación y extrae TODOS los artículos aplicables sin omitir ninguno:\n"
        f"{CODIGO_PENAL_TEXTO}\n\n"
        "FORMATO OBLIGATORIO:\n"
        "**Artículos aplicables:**\n"
        "• Art. XX - Nombre del delito\n\n"
        "**Conclusión:**\n"
        "Sanciones correspondientes aplicadas:\n"
        "• Art. XX - Nombre del delito: [Multa y Prisión]"
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'SITUACIÓN: "{situacion}"'}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        res = completion.choices[0].message.content
        if res and res.strip():
            return res
    except Exception as e:
        print(f"Aviso IA: {e}")

    return motor_local_rapido(situacion)

# ==========================================
# 4. CONFIGURACIÓN DEL CLIENTE Y COMANDOS
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

class BotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="el Código Penal Federal"))
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos slash sincronizados correctamente.")

client = BotClient()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="el Código Penal Federal"))
    print(f"Bot conectado exitosamente y en línea con luz verde como {client.user}")

@client.tree.command(
    name="codigo-penal",
    description="Analiza una situación y busca los artículos y sanciones.",
)
@app_commands.describe(
    situacion="Describe detalladamente los hechos ocurridos."
)
async def codigo_penal(interaction: discord.Interaction, situacion: str):
    await interaction.response.defer(thinking=True, ephemeral=False)
    try:
        resultado = await asyncio.to_thread(obtener_respuesta_ia, situacion)
        embed = discord.Embed(description=resultado.strip(), color=0xFFFFFF)
        await interaction.followup.send(embed=embed, ephemeral=False)
    except Exception as e:
        await interaction.followup.send(f"❌ Error al procesar: `{str(e)}`", ephemeral=False)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!codigo"):
        situacion = message.content[len("!codigo"):].strip()
        if not situacion:
            await message.channel.send("⚠️ Escribe una situación. Ej: `!codigo exceso de velocidad`")
            return

        msg_proceso = await message.channel.send("🔍 Analizando situación...")
        try:
            resultado = await asyncio.to_thread(obtener_respuesta_ia, situacion)
            embed = discord.Embed(description=resultado.strip(), color=0xFFFFFF)
            await msg_proceso.edit(content=None, embed=embed)
        except Exception as e:
            await msg_proceso.edit(content=f"❌ Error al procesar: `{str(e)}`")
        return

# ==========================================
# 5. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    keep_alive()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN.strip())
    else:
        print("ERROR: No se encontró la variable DISCORD_TOKEN.")
