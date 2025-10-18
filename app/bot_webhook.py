# app/bot_webhook.py
from fastapi import FastAPI, Request
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler
from app.formatter import markdown_to_telegram_html

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # your LLM API endpoint

# Build the async Telegram Application once (no polling, webhook only)
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


@app.get("/")
async def root():
    return {"status": "Bot API running"}


@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)

    # Handle text messages
    if update.message and update.message.text:
        user_query = update.message.text.strip()

        # Greeting handling
        if user_query.lower() in ["/start", "hi", "hello"]:
            await telegram_app.bot.send_message(
                chat_id=update.message.chat.id,
                text="Hi! How can I help you today?"
            )
            return {"status": "ok"}

        # Otherwise, call your LLM API
        try:
            response = requests.post(API_URL, json={"query": user_query})
            resp_json = response.json() if response.status_code == 200 else {}
            answer = resp_json.get("answer", "Sorry, I couldn't process that.")
            chat_log_id = resp_json.get("chat_log_id")
        except Exception as e:
            answer = f"Error: {str(e)}"
            chat_log_id = None

        # Convert Markdown → Telegram HTML
        answer = markdown_to_telegram_html(answer)

        # Feedback buttons
        reply_markup = None
        if chat_log_id:
            keyboard = [
                [
                    InlineKeyboardButton("👍 Useful", callback_data=f"feedback:{chat_log_id}:1"),
                    InlineKeyboardButton("👎 Not Useful", callback_data=f"feedback:{chat_log_id}:0"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

        # Send answer
        await telegram_app.bot.send_message(
            chat_id=update.message.chat.id,
            text=answer,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    return {"status": "ok"}


# Feedback callback handler
async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # remove loading spinner

    callback_data = query.data
    if callback_data.startswith("feedback:"):
        _, chat_log_id, value = callback_data.split(":")
        is_useful = bool(int(value))
        FEEDBACK_API = os.getenv("API_URL") + "/feedback"
        try:
            requests.post(FEEDBACK_API, json={"chat_log_id": chat_log_id, "is_useful": is_useful})
        except Exception as e:
            print(f"Feedback post failed: {e}")

    # Remove feedback buttons after click
    await query.edit_message_reply_markup(reply_markup=None)


# Add the CallbackQueryHandler once
telegram_app.add_handler(CallbackQueryHandler(feedback_handler))
