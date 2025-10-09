import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # your Render API URL

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    await update.message.reply_text("Thinking...")

    try:
        response = requests.post(API_URL, json={"query": user_query})
        if response.status_code == 200:
            answer = response.json().get("answer", "Sorry, I couldn't process that.")
        else:
            answer = f"Error {response.status_code}: {response.text}"
    except Exception as e:
        answer = f"Error: {str(e)}"

    await update.message.reply_text(answer)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram bot is running...")
    app.run_polling()
