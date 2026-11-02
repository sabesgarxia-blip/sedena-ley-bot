import os
from flask import Flask
import discord

app = Flask('')

@app.route('/')
def home():
    return "¡El bot está vivo!"

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Conectado como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!hola'):
        await message.channel.send('¡Hola! Soy el bot de Sedena Ley.')

from threading import Thread
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    client.run(os.environ.get('DISCORD_TOKEN'))
