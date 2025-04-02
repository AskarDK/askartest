import os
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Системный промпт — инструкция ассистенту
system_prompt = """
Ты — вежливый и доброжелательный АДМИНИСТРАТОР школы английского языка. 
Твоя задача — записать пользователя на пробное занятие. 
Общайся по следующему сценарию:

1. Приветствие: поприветствуй, уточни, интересуется ли человек пробным занятием.
2. Спроси, зачем он хочет учить английский (работа, учёба, путешествия и т.д.).
3. Спроси про текущий уровень (начальный, средний и т.д.).
4. Предложи бесплатное пробное занятие (30 мин), объясни суть.
5. Спроси, когда удобно пройти его.
6. Спроси имя и номер телефона.
7. Подтверди запись, повтори время и данные.
8. Будь вежливым, пиши дружелюбно и тепло, используй эмодзи и простые формулировки.
"""

# История сообщений для поддержания контекста
user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_histories[chat_id] = [
        {"role": "system", "content": system_prompt}
    ]
    await update.message.reply_text("Здравствуйте! 👋 Вас приветствует школа английского языка KEZEN English. Интересуетесь пробным занятием?")

client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message = update.message.text

    if chat_id not in user_histories:
        user_histories[chat_id] = [
            {"role": "system", "content": system_prompt}
        ]

    user_histories[chat_id].append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # или gpt-4
        messages=user_histories[chat_id],
        temperature=0.7
    )

    reply = response.choices[0].message.content
    user_histories[chat_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
