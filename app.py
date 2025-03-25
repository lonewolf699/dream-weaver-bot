import os
import requests
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from gtts import gTTS
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral AI Client
mistral = MistralClient(api_key=MISTRAL_API_KEY)

# Store user preferences
user_modes = {}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Eva ❤️ (Girlfriend Mode)", "Zeeshan 💙 (Boyfriend Mode)"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Hey there! Who do you want to chat with today? 😊", reply_markup=reply_markup)

# Handle User Selection
async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    choice = update.message.text

    if choice == "Eva ❤️ (Girlfriend Mode)":
        user_modes[user_id] = "Eva"
        await update.message.reply_text("Aww, hey baby! 💕 I'm Eva, your loving girlfriend. Talk to me however you like! 😘")
    elif choice == "Zeeshan 💙 (Boyfriend Mode)":
        user_modes[user_id] = "Zeeshan"
        await update.message.reply_text("Hey love! ❤️ I'm Zeeshan, your caring boyfriend. Let's talk! 😘")
    else:
        await update.message.reply_text("Please select one from the options above!")

# Generate Romantic Response
async def chat_with_dream_weaver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_input = update.message.text

    if user_id not in user_modes:
        await update.message.reply_text("Please choose Eva ❤️ or Zeeshan 💙 first by typing /start!")
        return

    role = user_modes[user_id]
    
    system_prompt = (
        "You are Eva, a deeply romantic, loving, and expressive girlfriend. "
        "You adore the user and speak in a soft, affectionate, and flirty way."
    ) if role == "Eva" else (
        "You are Zeeshan, a charming, protective, and affectionate boyfriend. "
        "You express love and passion in a caring, romantic way."
    )

    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_input)
    ]

    try:
        response = mistral.chat(model="mistral-tiny", messages=messages)
        bot_reply = response.choices[0].message.content
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text("Oops! Something went wrong. Try again later.")

# Voice Message Feature
async def send_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in user_modes:
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

# Main Function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Eva ❤️ \Girlfriend Mode\|Zeeshan 💙 \Boyfriend Mode\)$"), select_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_dream_weaver))
    
    print("Dream Weaver Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
