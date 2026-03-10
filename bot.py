import discord
import requests
import asyncio
import matplotlib.pyplot as plt

# =========================
# CONFIGURAÇÕES DO BOT
# =========================
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1479970037132427366
PLACE_ID = 93862983804718
ROLE_ID = 1480280983193391214
MARGEM_PICO = 1000
MARGEM_MUDANCA = 500
# =========================

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

previous_count = 0
player_history = []


def get_universe_id(place_id):

    try:
        url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json().get("universeId")

        return None

    except:
        return None


def get_player_count():

    try:

        universe_id = get_universe_id(PLACE_ID)

        if not universe_id:
            return 0

        url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return 0

        data = response.json()

        if "data" in data and data["data"]:
            return data["data"][0].get("playing", 0)

        return 0

    except:
        return 0


def gerar_grafico():

    if len(player_history) < 2:
        return None

    plt.figure()

    plt.plot(player_history)

    plt.title("Players Laboratório Brainrot")
    plt.xlabel("Verificações (30s)")
    plt.ylabel("Players")

    arquivo = "grafico_players.png"

    plt.savefig(arquivo)
    plt.close()

    return arquivo


async def monitor_game():

    await client.wait_until_ready()

    print("Monitoramento iniciado")

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Canal não encontrado")
        return

    peak = 0

    global previous_count

    while not client.is_closed():

        count = get_player_count()

        print(f"Players agora: {count} | Pico: {peak}")

        # salvar histórico
        player_history.append(count)

        if len(player_history) > 20:
            player_history.pop(0)

        diferenca = count - previous_count

        # atualização normal
        if abs(diferenca) >= MARGEM_MUDANCA:

            cor = 0x00ff00 if diferenca > 0 else 0xff0000

            embed = discord.Embed(
                title="Atualização de Jogadores",
                description=f"Laboratório Brainrot agora tem **{count} players**",
                color=cor
            )

            if diferenca > 0:
                embed.add_field(name="Mudança", value=f"↑ +{diferenca} jogadores")

            else:
                embed.add_field(name="Mudança", value=f"↓ -{abs(diferenca)} jogadores")

            await channel.send(embed=embed)

            grafico = gerar_grafico()

            if grafico:
                await channel.send(file=discord.File(grafico))

        # NOVO PICO
        if count >= peak + MARGEM_PICO:

            aumento = count - peak
            peak = count

            embed_pico = discord.Embed(
                title="🚀 NOVO PICO ATINGIDO!",
                description=f"Laboratório Brainrot chegou a **{peak} players!**",
                color=0x00ff00
            )

            embed_pico.add_field(
                name="Aumento de pico",
                value=f"+{aumento} jogadores"
            )

            await channel.send(f"<@&{ROLE_ID}>", embed=embed_pico)

            grafico = gerar_grafico()

            if grafico:
                await channel.send(file=discord.File(grafico))

        previous_count = count

        # verifica a cada 30 segundos
        await asyncio.sleep(30)


@client.event
async def on_ready():

    print(f"Bot online como {client.user}")

    client.loop.create_task(monitor_game())


client.run(TOKEN)