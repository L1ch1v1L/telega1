from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re
import sqlalchemy as db

# Используйте более осмысленное имя для переменной
data_storage = {"221": "привет хамстер комбат"}

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, {update.effective_user.first_name}, команды:\n/get "code" - выводит короч что записал\n/set "code" "text" - запись короч'
    )

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = re.findall(r'"(.*?)"', update.message.text)[0].replace('"',"")
    await update.message.reply_text(
        data_storage[code]
    )

async def get_one_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = update.message.text.split(" ")
    id = int(raw[1])
    engine = db.create_engine("mysql+pymysql://root@127.0.0.1/PRIVET2?charset=utf8mb4")
    conn = engine.connect()
    query = db.text(f"SELECT * FROM news1 WHERE id = {id}")
    news = conn.execute(query).fetchall()
    await update.message.reply_text(str(news[0][0])+str("\n\n") +str(news[0][1]))

async def set_one_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    
    # Находим все строки в двойных кавычках
    matches = re.findall(r'"(.*?)"', message_text)

    # Проверяем, что нашли по крайней мере два совпадения
    if len(matches) < 2:
        await update.message.reply_text("Ошибка: Пожалуйста, укажите код и текст в правильном формате: /setn \"code\" \"text\".")
        return
    code = str(matches[0])
    text_value = str(matches[1])

    engine = db.create_engine("mysql+pymysql://root@127.0.0.1/PRIVET2?charset=utf8mb4")

    # Подключение к базе данных
    with engine.connect() as conn:
        # Параметризованный запрос
        query = db.text(f"INSERT INTO news1 (name, description) VALUES('{code}', '{text_value}')")
        conn.execute(query)
        conn.commit()

    await update.message.reply_text("Добавлен!")
    
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем текст сообщения
    message_text = update.message.text
    
    # Находим все строки в двойных кавычках
    matches = re.findall(r'"(.*?)"', message_text)

    # Проверяем, что нашли по крайней мере два совпадения
    if len(matches) < 2:
        await update.message.reply_text("Ошибка: Пожалуйста, укажите код и текст в правильном формате: /set \"code\" \"text\".")
        return
    code = matches[0]  # Первый найденный паттерн
    text = matches[1]  # Второй найденный паттерн
    data_storage[code] = text
    await update.message.reply_text(f'Код: {code}, Текст: {text}')

app = ApplicationBuilder().token("6667584141:AAEafW3LB-2kavIYkxUuz9i-_Sw-oE0iW2E").build()

app.add_handler(CommandHandler("start", hello))
app.add_handler(CommandHandler("set", add))
app.add_handler(CommandHandler("get", get))
app.add_handler(CommandHandler("getn",get_one_news))
app.add_handler(CommandHandler("setn",set_one_news))

app.run_polling()