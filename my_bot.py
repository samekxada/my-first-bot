import asyncio
import logging
import os
import json

from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# =========================
# НАСТРОЙКИ
# =========================

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN: 
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения!")

try: 
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
except ValueError: 
    ADMIN_CHAT_ID = 0

SUPPORT_PHONE = "+998 (90) 931-31-07"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# ТЕКСТЫ
# =========================

TEXTS = {
    "ru": {
        "welcome": "🍔 <b>Добро пожаловать!</b>\n\nЗаказывайте онлайн, мы доставим! 🛵\n\nНажмите на <b>синюю кнопку</b> внизу слева, чтобы открыть меню.",
        "menu_btn": "🍔 Меню (кнопка ниже)",
        "addr_btn": "📍 Узнать Адрес",
        "lang_btn": "🌐 Язык / Til",
        "address": "📍 Демо-адрес: Ташкент, Мирабадский район.",
        
        "phone_req": "📱 Отправьте ваш номер телефона, нажав кнопку ниже, чтобы подтвердить заказ:",
        "phone_btn": "📞 Отправить номер",
        "phone_wrong": "❌ Пожалуйста, отправьте СВОЙ номер.",
        
        "ask_comment": "✍️ Хотите добавить комментарий к заказу?\n\nНапишите его (например: <i>'без лука'</i>), или нажмите кнопку ниже.",
        "skip_btn": "⏩ Пропустить",
        
        "thanks": "✅ Спасибо! Ваш заказ принят.\n\n📞 Номер для связи: {}\n📞 Служба поддержки: {}",
        "thanks_warn": "✅ Заказ принят.\n\n📞 Номер: {}\n⚠️ Если не свяжутся за 10 минут — позвоните: {}",
        "sauce_offer": "🥫 Отличный выбор! Хотите добавить соус к заказу?",
        "sauce_added": "✅ Соус добавлен!"
    },
    "uz": {
        "welcome": "🍔 <b>Xush kelibsiz!</b>\n\nOnlayn buyurtma bering, biz yetkazib beramiz! 🛵\n\nMenyuni ochish uchun pastdagi <b>ko'k tugmani</b> bosing.",
        "menu_btn": "🍔 Menyu (pastdagi tugma)",
        "addr_btn": "📍 Manzilni bilish",
        "lang_btn": "🌐 Язык / Til",
        "address": "📍 Demo-manzil: Toshkent, Mirobod tumani.",
        
        "phone_req": "📱 Buyurtmani tasdiqlash uchun pastdagi tugma orqali raqamingizni yuboring:",
        "phone_btn": "📞 Raqamni yuborish",
        "phone_wrong": "❌ Iltimos, O'Z raqamingizni yuboring.",
        
        "ask_comment": "✍️ Buyurtmaga izoh qo'shmoqchimisiz?\n\nYozing (masalan: <i>'piyozsiz'</i>), yoki tugmani bosing.",
        "skip_btn": "⏩ O'tkazib yuborish",
        
        "thanks": "✅ Rahmat! Buyurtmangiz qabul qilindi.\n\n📞 Aloqa: {}\n📞 Yordam: {}",
        "thanks_warn": "✅ Buyurtma qabul qilindi.\n\n📞 Aloqa: {}\n⚠️ 10 daqiqada bog'lanmasa — qo'ng'iroq qiling: {}",
        "sauce_offer": "🥫 Ajoyib tanlov! Sous qo'shmoqchimisiz?",
        "sauce_added": "✅ Sous qo'shildi!"
    }
}

# База цен для соусов (для апселла)
PRODUCTS = {
    "Соус сырный": 3000, 
    "Соус чесночный": 3000,
    "Кетчуп": 2000,
    "Соус Барбекю": 3000
}

user_languages = {}
webapp_carts = {} 
pending_orders = {} 

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_lang(user_id): 
    return user_languages.get(user_id, "ru")

def build_phone_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["phone_btn"], request_contact=True))
    return builder.as_markup(resize_keyboard=True)

def get_main_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["addr_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["lang_btn"]))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

# =========================
# ОТПРАВКА ЗАКАЗА АДМИНУ
# =========================

async def finalize_order(user_id, lang, comment=None):
    data = pending_orders.pop(user_id, None)
    if not data: return

    phone = data["phone"]
    currency = "сум" if lang == "ru" else "so'm"
    
    order_text = ""
    total = 0
    for item in data["cart"]:
        subtotal = item['price'] * item['qty']
        total += subtotal
        order_text += f"• {item['name']} × {item['qty']} = {subtotal:,} {currency}\n"
    
    comment_text = f"\n📝 <b>Комментарий:</b> {comment}\n" if comment else ""

    admin_message = (
        f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n---------------------------\n"
        f"👤 Клиент: {data['first_name']}\n🔗 Telegram: {data['username']}\n📞 Телефон: {phone}\n"
        f"---------------------------\n🍔 ЗАКАЗ:\n{order_text}\n💰 ИТОГО: {total:,} {currency}\n{comment_text}"
        f"---------------------------\n"
    )

    notified = False
    if ADMIN_CHAT_ID:
        admin_kb = InlineKeyboardBuilder()
        # Кнопка завершения заказа
        admin_kb.button(text="✅ Завершить заказ", callback_data=f"complete_{user_id}")
        
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text=admin_message, 
                reply_markup=admin_kb.as_markup(), 
                parse_mode="HTML"
            )
            notified = True
        except Exception as e: 
            logger.error(f"Ошибка отправки админу: {e}")
            
    thanks_key = "thanks" if notified else "thanks_warn"
    await bot.send_message(user_id, TEXTS[lang][thanks_key].format(phone, SUPPORT_PHONE), reply_markup=get_main_keyboard(lang))

# =========================
# ЗАВЕРШЕНИЕ ЗАКАЗА (ДЛЯ АДМИНА)
# =========================

@dp.callback_query(lambda c: c.data.startswith("complete_"))
async def complete_order(callback: types.CallbackQuery):
    client_id = int(callback.data.split("_")[1])
    
    try:
        # Отправляем клиенту
        await bot.send_message(
            chat_id=client_id,
            text="🛵 <b>Отличные новости!</b>\n\nВаш заказ готов. Курьер уже в пути, ожидайте в течение 20 минут.",
            parse_mode="HTML"
        )
        
        # Меняем текст на сообщении админа
        await callback.message.edit_text(
            text=callback.message.text + "\n\n✅ <b>СТАТУС: ЗАВЕРШЕН (Клиент уведомлен)</b>",
            parse_mode="HTML"
        )
        await callback.answer("Клиент уведомлен! 🛵", show_alert=False)
        
    except Exception as e:
        await callback.answer(f"Ошибка отправки: {e}", show_alert=True)

# =========================
# ХЕНДЛЕРЫ: СТАРТ И ЯЗЫК
# =========================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇺🇿 O'zbekcha"))
    builder.adjust(2)
    await message.answer("🇷🇺 Выберите язык / 🇺🇿 Tilni tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda msg: msg.text in ["🇷🇺 Русский", "🇺🇿 O'zbekcha"])
async def select_language(message: types.Message):
    lang = "ru" if message.text == "🇷🇺 Русский" else "uz"
    user_languages[message.from_user.id] = lang
    await message.answer(TEXTS[lang]["welcome"], reply_markup=get_main_keyboard(lang), parse_mode="HTML")

@dp.message(lambda msg: msg.text in ["🌐 Язык / Til", "🌐 Сменить язык / Tilni o'zgartirish"])
async def change_lang(message: types.Message):
    await cmd_start(message)

# =========================
# ПРИЕМ ДАННЫХ ИЗ MINI APP (WEB APP)
# =========================

@dp.message(lambda msg: msg.web_app_data)
async def handle_web_app_data(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    
    try:
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])
        
        if not items:
            await message.answer("Корзина пуста.")
            return
            
        webapp_carts[user_id] = items
        total = sum(item['price'] * item['qty'] for item in items)
        items_text = "\n".join([f"• {item['name']} × {item['qty']}" for item in items])
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🥫 Сырный (+3000)", callback_data="web_sauce_Соус сырный")
        builder.button(text="🥫 Чесночный (+3000)", callback_data="web_sauce_Соус чесночный")
        builder.button(text="❌ Без соуса", callback_data="web_no_sauce")
        builder.adjust(2, 1)
        
        await message.answer(
            f"🛒 <b>Ваш заказ:</b>\n{items_text}\n\n💰 <b>Итого:</b> {total:,} сум\n\n"
            f"{TEXTS[lang]['sauce_offer']}",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга WebApp: {e}")
        await message.answer("Произошла ошибка при обработке заказа. Попробуйте еще раз.")

@dp.callback_query(lambda c: c.data.startswith("web_sauce_"))
async def add_web_sauce(callback: types.CallbackQuery):
    sauce_name = callback.data.replace("web_sauce_", "")
    user_id = callback.from_user.id
    lang = get_lang(user_id)
    
    if user_id in webapp_carts:
        webapp_carts[user_id].append({"name": sauce_name, "qty": 1, "price": PRODUCTS[sauce_name]})
        await callback.answer(TEXTS[lang]["sauce_added"], show_alert=False)
        await callback.message.delete()
        await ask_phone_webapp(callback.message, user_id, lang)

@dp.callback_query(lambda c: c.data == "web_no_sauce")
async def no_web_sauce(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await ask_phone_webapp(callback.message, callback.from_user.id, get_lang(callback.from_user.id))

async def ask_phone_webapp(message: types.Message, user_id: int, lang: str):
    await message.answer(TEXTS[lang]["phone_req"], reply_markup=build_phone_keyboard(lang))

# Обработка контакта для Web App
@dp.message(lambda msg: msg.contact is not None and msg.from_user.id in webapp_carts)
async def handle_webapp_contact(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    
    if message.contact.user_id != user_id:
        await message.answer(TEXTS[lang]["phone_wrong"], reply_markup=build_phone_keyboard(lang))
        return

    pending_orders[user_id] = {
        "phone": message.contact.phone_number,
        "cart": webapp_carts.pop(user_id),
        "username": f"@{message.from_user.username}" if message.from_user.username else "Нет",
        "first_name": message.from_user.first_name
    }
    
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["skip_btn"]))
    await message.answer(TEXTS[lang]["ask_comment"], reply_markup=builder.as_markup(resize_keyboard=True), parse_mode="HTML")

# =========================
# ОБРАБОТКА КОММЕНТАРИЕВ
# =========================

@dp.message(lambda msg: msg.text in ["⏩ Пропустить", "⏩ O'tkazib yuborish"])
async def skip_comment(message: types.Message):
    user_id = message.from_user.id
    if user_id in pending_orders:
        await finalize_order(user_id, get_lang(user_id), comment=None)

@dp.message(lambda msg: msg.from_user.id in pending_orders and msg.text is not None)
async def handle_comment(message: types.Message):
    user_id = message.from_user.id
    await finalize_order(user_id, get_lang(user_id), comment=message.text.strip())

# =========================
# АДРЕС И ЗАГЛУШКИ
# =========================

@dp.message(lambda msg: msg.text in ["📍 Узнать Адрес", "📍 Manzilni bilish"])
async def show_address(message: types.Message):
    await message.answer(TEXTS[get_lang(message.from_user.id)]["address"], reply_markup=get_main_keyboard(get_lang(message.from_user.id)))

@dp.message(lambda msg: msg.text in ["🍔 Меню (кнопка ниже)", "🍔 Menyu (pastdagi tugma)", "🔙 Назад", "🔙 Orqaga"])
async def show_old_menu(message: types.Message):
    await message.answer("Пожалуйста, нажмите на синюю кнопку внизу слева.", reply_markup=get_main_keyboard(get_lang(message.from_user.id)))

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Нажмите на синюю кнопку 'Сделать заказ' внизу слева, чтобы открыть меню.", reply_markup=get_main_keyboard(get_lang(message.from_user.id)))

@dp.error()
async def error_handler(event: types.ErrorEvent):
    logger.error(f"Ошибка: {event.exception}", exc_info=event.exception)

# =========================
# WEBHOOK И HEALTHCHECK
# =========================

async def handle_webhook(request: web.Request):
    try:
        update_data = await request.json()
        await dp.feed_update(bot, types.Update(**update_data))
    except Exception as e: 
        logger.error(f"Ошибка вебхука: {e}")
    return web.Response(status=200)

async def healthcheck(request: web.Request): 
    return web.Response(text="Bot is running!")

async def on_startup(app: web.Application):
    webhook_host = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_HOST")
    if not webhook_host: return
    webhook_url = f"{webhook_host}/webhook/{TOKEN}"
    logger.info(f"Вебхук: {webhook_url}")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(webhook_url)
    except Exception as e: 
        logger.error(f"Ошибка при старте: {e}")

async def on_shutdown(app: web.Application): 
    await bot.session.close()

if __name__ == "__main__":
    logger.info("🚀 ЗАПУСК...")
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_post(f"/webhook/{TOKEN}", handle_webhook)
    app.router.add_get("/healthz", healthcheck)
    app.router.add_get("/", healthcheck)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=port)
