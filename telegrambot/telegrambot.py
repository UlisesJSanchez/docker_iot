from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, asyncio, aiomysql, traceback, locale
import ssl
from aiomqtt import Client, ProtocolVersion
import matplotlib.pyplot as plt
from io import BytesIO

token=os.environ["TB_TOKEN"]

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre=update.message.from_user.first_name
    else:
        nombre=""
    if update.message.from_user.last_name:
        apellido=update.message.from_user.last_name
    else:
        apellido=""
    #kb = [["setpoint"],["periodo"],["destello"],["modo"]]
    await context.bot.send_message(update.message.chat.id, text="¡Bienvenido al Bot "+ nombre + " " + apellido + "!") # reply_markup=ReplyKeyboardMarkup(kb)

async def setpoint(update: Update, context):
    logging.info("Setpoint: " + str(context.args))
    if context.args:
        setpoint = context.args[0]
        try:
            float(setpoint)
            await publicar_mqtt(f'{os.environ["MAC_ID"]}/setpoint', setpoint)
            await context.bot.send_message(update.message.chat.id, text=f"Setpoint actualizado a {setpoint} °C.")
        except ValueError:
            await context.bot.send_message(update.message.chat.id, text="Valor de setpoint no válido. Se debe ingresar un número, por ejemplo: /setpoint 25.")
    else:
        await context.bot.send_message(update.message.chat.id, text="Se debe ingresar un valor de setpoint, por ejemplo: /setpoint 25.")

async def periodo(update: Update, context):
    logging.info("Periodo: " + str(context.args))
    if context.args:
        periodo = context.args[0]
        try:
            int(periodo)
            await publicar_mqtt(f'{os.environ["MAC_ID"]}/periodo', periodo)
            await context.bot.send_message(update.message.chat.id, text=f"Periodo actualizado a {periodo} segundos.")
        except ValueError:
            await context.bot.send_message(update.message.chat.id, text="Valor de periodo no válido. Se debe ingresar un número entero, por ejemplo: /periodo 10.")
    else:
        await context.bot.send_message(update.message.chat.id, text="Se debe ingresar un valor de periodo, por ejemplo: /periodo 10.")

async def destello(update: Update, context):
    logging.info("Destello: " + str(context.args))
    if context.args:
        await context.bot.send_message(update.message.chat.id, text="El comando destello no requiere argumentos. Para activarlo simplemente ingrese: /destello.")
    else:
        await publicar_mqtt(f'{os.environ["MAC_ID"]}/destello', 'destello')
        await context.bot.send_message(update.message.chat.id, text="Destello activado.")

async def modo(update: Update, context):
    logging.info("Modo: " + str(context.args))
    if context.args:
        modo = context.args[0].lower()
        if modo in ['auto', 'manual']:
            await publicar_mqtt(f'{os.environ["MAC_ID"]}/modo', modo)
            await context.bot.send_message(update.message.chat.id, text=f"Modo actualizado a {modo}.")
        else:
            await context.bot.send_message(update.message.chat.id, text="Modo no válido. Únicamente se aceptan 'auto' o 'manual', por ejemplo: /modo auto.")
    else:
        await context.bot.send_message(update.message.chat.id, text="Se debe ingresar el modo de operación, por ejemplo: /modo auto.")

async def rele(update: Update, context):
    logging.info("Réle: " + str(context.args))
    if context.args:
        estado = context.args[0].lower()
        if estado in ['on', 'off']:
            await publicar_mqtt(f'{os.environ["MAC_ID"]}/rele', estado)
            await context.bot.send_message(update.message.chat.id, text=f"Estado del relé actualizado a {estado}.")
        else:
            await context.bot.send_message(update.message.chat.id, text="Estado no válido. Únicamente se aceptan 'on' o 'off', por ejemplo: /rele on.")
    else:
        await context.bot.send_message(update.message.chat.id, text="Se debe ingresar el estado del relé, por ejemplo: /rele on.")

async def publicar_mqtt(topico: str, mensaje: str):
    
    tls_context = ssl.create_default_context()
    tls_context.check_hostname = False
    tls_context.verify_mode = ssl.CERT_NONE

    try:
        async with Client(
            hostname=os.environ["SERVIDOR"],
            username=os.environ.get("MQTT_USR"),
            password=os.environ.get("MQTT_PASS"),
            protocol=ProtocolVersion.V311,
            port=int(os.environ["PUERTO_MQTTS"]),
            tls_context=tls_context,
        ) as client:
            await client.publish(topico, mensaje, qos=1, retain=True)
            logging.info(f"Mensaje MQTT publicado -> Tópico: {topico} | Mensaje: {mensaje}")
    except Exception as e:
        logging.error(f"Error al publicar en MQTT: {e}")

async def kill(update: Update, context):
    logging.info(context.args)
    await context.bot.send_message(update.message.chat.id, text="Borrando base de datos en...")
    await asyncio.sleep(1)
    await context.bot.send_message(update.message.chat.id, text="3...")
    await asyncio.sleep(1)
    await context.bot.send_message(update.message.chat.id, text="2...")
    await asyncio.sleep(1)
    await context.bot.send_message(update.message.chat.id, text="1...")
    await asyncio.sleep(1)
    await context.bot.send_animation(update.message.chat.id, "BQACAgEAAxkBAAMIahiDRUBTDkaQwW0IzR9oBa5vwA8AApwFAALsoslEi568YZjqkuc7BA")
        
"""async def medicion(update: Update, context):
    logging.info(update.message.text)
    sql = f"SELECT timestamp, {update.message.text} FROM mediciones ORDER BY timestamp DESC LIMIT 1"
    conn = await aiomysql.connect(host=os.environ["MARIADB_SERVER"], port=3306,
                                    user=os.environ["MARIADB_USER"],
                                    password=os.environ["MARIADB_USER_PASS"],
                                    db=os.environ["MARIADB_DB"])
    async with conn.cursor() as cur:
        await cur.execute(sql)
        r = await cur.fetchone()
        if update.message.text == 'temperatura':
            unidad = 'ºC'
        else:
            unidad = '%'
        await context.bot.send_message(update.message.chat.id,
                                    text="La última {} es de {} {},\nregistrada a las {:%H:%M:%S %d/%m/%Y}"
                                    .format(update.message.text, str(r[1]).replace('.',','), unidad, r[0]))
        logging.info("La última {} es de {} {}, medida a las {:%H:%M:%S %d/%m/%Y}".format(update.message.text, r[1], unidad, r[0]))
    conn.close()"""

"""async def graficos(update: Update, context):
    logging.info(update.message.text)
    sql = fSELECT timestamp, {update.message.text.split()[1]}
            FROM (
                SELECT timestamp, {update.message.text.split()[1]},
                    ROW_NUMBER() OVER (ORDER BY id) AS rn
                FROM mediciones
                WHERE timestamp >= NOW() - INTERVAL 1 DAY
                AND sensor_id LIKE 'sensor_1'
            ) AS t
            WHERE rn % 2 = 0
            ORDER BY timestamp
    conn = await aiomysql.connect(host=os.environ["MARIADB_SERVER"], port=3306,
                                    user=os.environ["MARIADB_USER"],
                                    password=os.environ["MARIADB_USER_PASS"],
                                    db=os.environ["MARIADB_DB"])
    async with conn.cursor() as cur:
        await cur.execute(sql)
        filas = await cur.fetchall()

        fig, ax = plt.subplots(figsize=(7, 4))
        fecha,var=zip(*filas)
        ax.plot(fecha,var)
        ax.grid(True, which='both')
        ax.set_title(update.message.text, fontsize=14, verticalalignment='bottom')
        ax.set_xlabel('fecha')
        ax.set_ylabel('unidad')

        buffer = BytesIO()
        fig.tight_layout()
        fig.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buffer)
        buffer.close()
    conn.close()"""

def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('setpoint', setpoint))
    application.add_handler(CommandHandler('kill', kill))
    application.add_handler(CommandHandler('periodo', periodo))
    application.add_handler(CommandHandler('destello', destello))
    application.add_handler(CommandHandler('modo', modo))
    application.add_handler(CommandHandler('rele', rele))
    application.run_polling()

if __name__ == '__main__':
    main()
