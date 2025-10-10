import os
import logging
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # your LLM API endpoint

bot = Bot(token=TELEGRAM_TOKEN)
app = FastAPI(title="Telegram Bot Webhook API")

dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

async def handle_message(update: Update, context):
    user_message = update.message.text
    await bot.send_message(chat_id=update.effective_chat.id, text="Thinking...")

    try:
        response = requests.post(API_URL, json={"query": user_message})
        if response.status_code == 200:
            answer = response.json().get("answer", "Sorry, I couldn't process that.")
        else:
            answer = f"Error {response.status_code}: {response.text}"
    except Exception as e:
        answer = f"Error: {str(e)}"

    await bot.send_message(chat_id=update.effective_chat.id, text=answer)

dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
    return {"ok": True}

@app.get("/")
def health_check():
    return {"message": "Telegram bot webhook is live ✅"}
