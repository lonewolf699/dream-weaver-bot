import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import MistralClient
from gtts import gTTS
from dotenv import load_dotenv

# Load API keys from environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral AI Client
mistral = MistralClient(api_key=MISTRAL_API_KEY)

# Flask App (Keeps Render Service Alive)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Dream Weaver Bot is running!"

# Store user preferences
user_modes = {}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Eva ❤️ (Girlfriend Mode)", "Zeeshan 💙 (Boyfriend Mode)"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text("Hey there! Who do you want to chat with today? 😊", reply_markup=reply_markup)

# Handle User Selection (Correctly Stores Mode)
async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    choice = update.message.text

    if choice == "Eva ❤️ (Girlfriend Mode)":
        context.user_data["mode"] = "Eva"
        await update.message.reply_text("Aww, hey baby! 💕 I'm Eva, your loving girlfriend. Talk to me however you like! 😘")
    elif choice == "Zeeshan 💙 (Boyfriend Mode)":
        context.user_data["mode"] = "Zeeshan"
        await update.message.reply_text("Hey love! ❤️ I'm Zeeshan, your caring boyfriend. Let's talk! 😘")
    else:
        await update.message.reply_text("Please select one from the options above!")

# Chat Response
async def chat_with_dream_weaver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    role = context.user_data.get("mode")  # Get selected mode

    if not role:
        await update.message.reply_text("Please choose Eva ❤️ or Zeeshan 💙 first by typing /start!")
        return

    system_prompt = (
        "You are Eva, a deeply romantic, loving, and expressive girlfriend. "
        "You adore the user and speak in a soft, affectionate, and flirty way."
    ) if role == "Eva" else (
        "You are Zeeshan, a charming, protective, and affectionate boyfriend. "
        "You express love and passion in a caring, romantic way."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        response = mistral.chat(model="mistral-tiny", messages=messages)
        bot_reply = response.choices[0].message.content
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text("Oops! Something went wrong. Try again later.")

# Voice Message Feature
async def send_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "mode" not in context.user_data:
        await update.message.reply_text("Please choose Eva ❤️ or Zeeshan 💙 first by typing /start!")
        return

    text = update.message.text
    language = "en"

    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = "voice.mp3"
        tts.save(audio_file)

        await update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    except Exception as e:
        await update.message.reply_text("Sorry, I couldn't generate the voice message.")

# Main Function (Runs Both Flask & Bot)
def main():
    # Start Flask in a separate thread to keep the web service alive
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()

    # Start the Telegram bot
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Eva ❤️ Girlfriend Mode|Zeeshan 💙 Boyfriend Mode)$"), select_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_dream_weaver))

    print("Dream Weaver Bot is running...")  # You should see this in logs if the bot starts
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=3)

if __name__ == "__main__":
    main()
