from typing import Final
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
from os.path import join, dirname
from dotenv import load_dotenv
from openai import OpenAI

# ——— Carga de variables de entorno ———
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TELEGRAM_TOKEN: Final = os.environ["TELEGRAM_TOKEN"]
BOT_USERNAME: Final = os.environ["BOT_USERNAME"]
DEEPSEEK_API_KEY: Final = os.environ["DEEPSEEK_API_KEY"]
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "")

# ——— Cliente de IA ———
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def handle_response(text: str) -> str:
    """Envía el texto a la IA y devuelve la respuesta."""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": text}
        ],
        stream=False
    )
    return resp.choices[0].message.content

# ——— Handlers ———
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def tools1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Próximamente integraré capacidad de envío de correos.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # Si estás en grupo y mencionan al bot, filtras así:
    if update.message.chat.type == 'group':
        if BOT_USERNAME not in text:
            return
        # quitas la mención para pasar sólo el contenido real
        text = text.replace(BOT_USERNAME, "").strip()

    # 1) Llamas a la IA
    response = handle_response(text)

    # 2) Respondes al usuario
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} causó error {context.error}')

# ——— Inicio del bot ———
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("tools1", tools1))
    # mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # errores
    app.add_error_handler(error)

    print("Bot is starting...")
    app.run_polling(poll_interval=3)
