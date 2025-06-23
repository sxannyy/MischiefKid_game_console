import threading
import secrets
from fastapi import FastAPI
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

import settings
import db
import models
from models.token import Token
from routers import auth, saves
from utils.hasher import Hasher

app = FastAPI(title="MischiefKid Game Console API")

app.include_router(auth.router)
app.include_router(saves.router)

bot = Bot(token=settings.settings.TELEGRAM_TOKEN)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Используй /register <логин> <имя> <фамилия> для регистрации.\n"
        "/token <логин> — получить токен\n"
        "/getsave — получить ссылку на сохранение\n"
        "/save — загрузить файл сохранения\n"
        "/help — помощь"
    )

# /register
def register(update: Update, context: CallbackContext):
    if len(context.args) < 3:
        update.message.reply_text("Использование: /register <логин> <имя> <фамилия>")
        return

    username = context.args[0]
    first_name = context.args[1]
    last_name = context.args[2]
    chat_id = update.effective_chat.id

    db_gen = db.get_db()
    session = next(db_gen)
    try:
        existing = session.query(models.User).filter(models.User.username == username).first()
        if existing:
            update.message.reply_text("Пользователь с таким логином уже зарегистрирован.")
            return

        user = models.User(
            username=username,
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            save_link=None
        )
        session.add(user)
        session.commit()

        update.message.reply_text("Регистрация успешна!")
    finally:
        session.close()

# /token
def token_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Укажите логин: /token <логин>")
        return

    username = context.args[0]
    chat_id = update.effective_chat.id

    db_gen = db.get_db()
    session = next(db_gen)
    try:
        user = session.query(models.User).filter(models.User.username == username).first()

        if not user:
            update.message.reply_text("Логин не найден.")
            return

        if user.chat_id != chat_id:
            update.message.reply_text("Ваш chat_id не совпадает с зарегистрированным.")
            return

        session.query(Token).filter(Token.username == username).delete()

        token_plain = str(secrets.randbelow(10**6)).zfill(6)
        token_hash = Hasher.hash(token_plain)

        token_entry = Token(
            username=username,
            token_hash=token_hash
        )
        session.add(token_entry)
        session.commit()

        update.message.reply_text(f"Ваш одноразовый токен: {token_plain}")
    finally:
        session.close()

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("register", register))
dispatcher.add_handler(CommandHandler("token", token_cmd))

@app.on_event("startup")
def on_startup():
    from db import Base, engine
    Base.metadata.create_all(bind=engine)
    threading.Thread(target=updater.start_polling, daemon=True).start()

@app.on_event("shutdown")
def on_shutdown():
    updater.stop()