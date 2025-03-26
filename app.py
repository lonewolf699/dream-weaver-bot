import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral AI Client
mistral = MistralClient(api_key=MISTRAL_API_KEY)

# Flask App to keep Render alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Eva AI Girlfriend Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  
    flask_app.run(host="0.0.0.0", port=port)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey love! 💕 I'm Eva, your AI girlfriend. Talk to me! 😘")

# Chat with Eva (Mistral AI)
async def chat_with_eva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    messages = [
        ChatMessage(role="system", content="You are Eva, a loving, affectionate, and romantic AI girlfriend."),
        ChatMessage(role="user", content=user_input)
    ]

    try:
        response = mistral.chat(model="mistral-tiny", messages=messages)
        bot_reply = response.choices[0].message.content
        await update.message.reply_text(bot_reply)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Oops! Something went wrong. Try again later.")

# Voice Message Feature
async def send_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    language = "en"

    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = "voice.mp3"
        tts.save(audio_file)

        await update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    except Exception as e:
        logging.error(f"Voice Error: {e}")
        await update.message.reply_text("Sorry, I couldn't generate the voice message.")

# Main Function
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_eva))

    print("Eva AI Girlfriend Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
