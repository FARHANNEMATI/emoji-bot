import logging
logging.basicConfig(level=logging.INFO)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from flask import Flask
from threading import Thread
from datetime import datetime
import random

# ⚙️ تنظیمات اولیه
TOKEN = '7275034128:AAGMk8odzA8SZsZbwOeRiKt9ZH7UpeaHSK0'
EMOJI_PACK_LINK = 'https://t.me/addemoji/ZAXYPack'
SELLER_USERNAME = '@PVZAXY'

# 🚀 اجرای Flask برای روشن ماندن
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 🌐 دیتابیس چندزبانه
LANG_TEXTS = {
    'fa': {
        'welcome': "✨ خوش اومدی به ربات ساخت ایموجی اختصاصی! ✨\n\n🔥 با ایموجی‌های خفن از پک زیر، پروفایل خودتو خاص کن!\n\n👇 اول روی لینک زیر بزن و پک رو اضافه کن:\n{pack}\n\n💡 بعد یکی از ایموجی‌ها رو از همون پک همینجا برای من بفرست...",
        'receipt_title': "🧾 رسید سفارش",
        'receipt_user': "User",
        'receipt_id': "User ID",
        'receipt_emoji': "Emoji",
        'receipt_code': "Order Code",
        'receipt_time': "Timestamp",
        'receipt_status': "Status",
        'status_text': "در حال پردازش",
        'pay_msg': "💳 برای ادامه سفارش، به پشتیبانی پیام بده:",
        'send_support': "✉️ پیام به پشتیبانی",
        'send_pack': "📦 باز کردن پک",
        'not_custom': "⛔ لطفاً یکی از ایموجی‌های پک ZAXY را همینجا ارسال کن.",
        'receipt_loading': "✅ ایموجی با موفقیت دریافت شد!\nدر حال ساخت رسید سفارش..."
    },
    'en': {
        'welcome': "✨ Welcome to the Custom Emoji Bot! ✨\n\n🔥 Make your profile special with awesome emojis from the pack below:\n\n👇 First, tap this link and add the pack:\n{pack}\n\n💡 Then, send me one of the emojis from that pack here...",
        'receipt_title': "🧾 Receipt",
        'receipt_user': "User",
        'receipt_id': "User ID",
        'receipt_emoji': "Emoji",
        'receipt_code': "Order Code",
        'receipt_time': "Timestamp",
        'receipt_status': "Status",
        'status_text': "In Progress",
        'pay_msg': "💳 To continue your order, message our support:",
        'send_support': "✉️ Contact Support",
        'send_pack': "📦 Open Emoji Pack",
        'not_custom': "⛔ Please send one of the emojis from the ZAXY pack.",
        'receipt_loading': "✅ Emoji received successfully!\nGenerating your receipt..."
    },
    'ru': {
        'welcome': "✨ Добро пожаловать в бот создания кастомных эмодзи! ✨\n\n🔥 Сделай свой профиль уникальным с помощью эмодзи из набора ниже:\n\n👇 Сначала добавь этот набор эмодзи:\n{pack}\n\n💡 А затем отправь один из эмодзи прямо сюда...",
        'receipt_title': "🧾 Чек заказа",
        'receipt_user': "User",
        'receipt_id': "User ID",
        'receipt_emoji': "Emoji",
        'receipt_code': "Order Code",
        'receipt_time': "Timestamp",
        'receipt_status': "Status",
        'status_text': "В процессе",
        'pay_msg': "💳 Чтобы продолжить заказ, напишите в поддержку:",
        'send_support': "✉️ Написать в поддержку",
        'send_pack': "📦 Открыть набор эмодзи",
        'not_custom': "⛔ Пожалуйста, отправьте эмодзи из набора ZAXY.",
        'receipt_loading': "✅ Эмодзи успешно получен!\nСоздание квитанции..."
    }
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang_fa'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
        ]
    ])
    await update.message.reply_text(
        "Please choose your language:\nلطفاً زبان خود را انتخاب کنید:\nПожалуйста, выберите язык:",
        reply_markup=keyboard
    )

# انتخاب زبان
async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[-1]
    context.user_data['lang'] = lang

    txts = LANG_TEXTS[lang]
    msg = txts['welcome'].format(pack=EMOJI_PACK_LINK)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(txts['send_pack'], url=EMOJI_PACK_LINK)],
        [InlineKeyboardButton(txts['send_support'], url=f"https://t.me/{SELLER_USERNAME.strip('@')}")]
    ])
    await query.edit_message_text(msg, reply_markup=keyboard)

# بررسی custom emoji
def is_custom_emoji(update: Update) -> bool:
    if update.message and update.message.entities:
        for e in update.message.entities:
            if e.type == MessageEntity.CUSTOM_EMOJI:
                return True
    if update.message and update.message.text:
        return any(ord(c) > 100000 for c in update.message.text)
    return False

# رسید متنی
def build_receipt(user, emoji_text, lang='fa'):
    txt = LANG_TEXTS.get(lang, LANG_TEXTS['fa'])
    return (
        f"{txt['receipt_title']}\n\n"
        f"👤 {txt['receipt_user']}: @{user.username or 'N/A'}\n"
        f"🆔 {txt['receipt_id']}: {user.id}\n"
        f"🎨 {txt['receipt_emoji']}: {emoji_text}\n"
        f"🔖 {txt['receipt_code']}: ZX-{random.randint(1000, 9999)}\n"
        f"🕒 {txt['receipt_time']}: {datetime.now().strftime('%Y-%m-%d | %H:%M')}\n"
        f"📦 {txt['receipt_status']}: {txt['status_text']}"
    )

# هندلر ایموجی
async def handle_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'fa')
    txts = LANG_TEXTS[lang]

    if not is_custom_emoji(update):
        await update.message.reply_text(txts['not_custom'])
        return

    emoji_text = update.message.text or "N/A"
    receipt = build_receipt(update.effective_user, emoji_text, lang)
    await update.message.reply_text(txts['receipt_loading'])
    await update.message.reply_text(receipt)
    await update.message.reply_text(
        txts['pay_msg'],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(txts['send_support'], url=f"https://t.me/{SELLER_USERNAME.strip('@')}")]
        ])
    )

# اجرای ربات
def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_emoji))
    print("✅ ربات اجرا شد.")
    app.run_polling()

if __name__ == '__main__':
    main()