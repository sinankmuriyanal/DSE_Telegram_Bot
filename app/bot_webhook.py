from fastapi import FastAPI, Request
import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from app.formatter import markdown_to_telegram_html


app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # your LLM API endpoint

bot = Bot(token=TELEGRAM_TOKEN)

@app.get("/")
async def root():
    return {"status": "Bot API running"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)

    # handle message
    if update.message and update.message.text:
        user_query = update.message.text
        await bot.send_message(chat_id=update.message.chat_id, text="Thinking...")
        try:
            response = requests.post(API_URL, json={"query": user_query})
            answer = response.json().get("answer", "Sorry, I couldn't process that.") if response.status_code == 200 else f"Error {response.status_code}"
        except Exception as e:
            answer = f"Error: {str(e)}"

         # 🔹 Convert Markdown → Telegram HTML
        answer = markdown_to_telegram_html(answer)

        # 🔹 Send formatted message
        await bot.send_message(chat_id=update.message.chat_id, text=answer, parse_mode="HTML")

    return {"status": "ok"}
