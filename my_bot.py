import asyncio
import logging
import os

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
    raise RuntimeError("❌ BOT_TOKEN не найден!")

try:
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
except ValueError:
    ADMIN_CHAT_ID = 0

SUPPORT_PHONE = "+998 (90) 931-31-07"
PLUS_PREFIX = "➕ "
MINUS_PREFIX = "➖ "

# =========================
# ЛОГГИРОВАНИЕ И БОТ
# =========================

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# ТЕКСТЫ
# =========================

TEXTS = {
    "ru": {
        "welcome": "Выберите действие:",
        "menu_btn": "🍔 Посмотреть Меню",
        "addr_btn": "📍 Узнать Адрес",
        "lang_btn": "🌐 Сменить язык / Tilni o'zgartirish",
        "select_cat": "📋 Выберите интересующий вас раздел меню:",
        "back": "🔙 Назад",
        "address": "📍 Демо-адрес: Ташкент, Мирабадский район, ориентир: Госпитальный рынок.",
        
        "cart": "🧺 Моя корзина",
        "clear_cart": "🗑 Очистить корзину",
        "order_btn": "🛒 Оформить заказ",
        "cart_empty": "🧺 Ваша корзина пока пуста.",
        "cart_title": "🧺 ВАША КОРЗИНА:",
        "cart_total": "💰 Итого:",
        "cart_hint": "\n💡 <i>(Нажимайте ➖ или ➕, чтобы изменить количество)</i>",
        "currency": "сум",
        
        "phone_req": "📱 Для оформления заказа отправьте ваш номер телефона, нажав кнопку ниже:",
        "phone_btn": "📞 Отправить номер телефона",
        "phone_wrong": "❌ Пожалуйста, отправьте СВОЙ номер телефона — нажмите кнопку ниже.",
        
        "ask_comment": "✍️ Хотите добавить комментарий к заказу?\n\nНапишите его одним сообщением (например: <i>'без лука'</i>), или нажмите кнопку ниже.",
        "skip_btn": "⏩ Пропустить",
        "comment_added": "✅ Комментарий добавлен. Отправляю заказ...",
        "cart_cleared": "🗑 Корзина очищена.",
        "thanks": "✅ Спасибо! Ваш заказ принят.\n\n📞 Номер для связи: {}\n📞 Служба поддержки: {}",
        "thanks_warn": "✅ Ваш заказ принят.\n\n📞 Номер для связи: {}\n⚠️ Если с вами не свяжутся в течение 10 минут — позвоните: {}",
    },
    "uz": {
        "welcome": "Harakatni tanlang:",
        "menu_btn": "🍔 Menyuni ko'rish",
        "addr_btn": "📍 Manzilni bilish",
        "lang_btn": "🌐 Сменить язык / Tilni o'zgartirish",
        "select_cat": "📋 Kerakli bo'limni tanlang:",
        "back": "🔙 Orqaga",
        "address": "📍 Demo-manzil: Toshkent, Mirobod tumani, mo'ljal: Gospitalniy bozori.",
        
        "cart": "🧺 Savatim",
        "clear_cart": "🗑 Savatni tozalash",
        "order_btn": "🛒 Buyurtma berish",
        "cart_empty": "🧺 Savatingiz hozircha bo'sh.",
        "cart_title": "🧺 SAVATINGIZ:",
        "cart_total": "💰 Jami:",
        "cart_hint": "\n💡 <i>(Miqdorni o'zgartirish uchun ➖ yoki ➕ tugmalarini bosing)</i>",
        "currency": "so'm",
        
        "phone_req": "📱 Buyurtmani rasmiylashtirish uchun pastdagi tugmani bosib, telefon raqamingizni yuboring:",
        "phone_btn": "📞 Telefon raqamni yuborish",
        "phone_wrong": "❌ Iltimos, O'ZINGIZNING telefon raqamingizni yuboring — pastdagi tugmani bosing.",
        
        "ask_comment": "✍️ Buyurtmaga izoh qo'shmoqchimisiz?\n\nUni bitta xabar bilan yozing (masalan: <i>'piyozsiz'</i>), yoki pastdagi tugmani bosing.",
        "skip_btn": "⏩ O'tkazib yuborish",
        "comment_added": "✅ Izoh qo'shildi. Buyurtma yuborilmoqda...",
        "cart_cleared": "🗑 Savat tozalandi.",
        "thanks": "✅ Rahmat! Buyurtmangiz qabul qilindi.\n\n📞 Aloqa raqamingiz: {}\n📞 Qo'llab-quvvatlash markazi: {}",
        "thanks_warn": "✅ Buyurtmangiz qabul qilindi.\n\n📞 Aloqa raqamingiz: {}\n⚠️ Agar 10 daqiqa ichida siz bilan bog'lanmasa — qo'ng'iroq qiling: {}",
    }
}

# =========================
# ТОВАРЫ И ИХ ФОТО (ВСТАВЬ СВОИ ССЫЛКИ)
# =========================
# Я поставил красивые картинки из интернета для примера.
# Когда будешь сдавать клиенту, просто замени ссылки на фото его блюд!

PRODUCTS = {
    "Чизбургер": {"price": 28000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=800&auto=format&fit=crop"},
    "Шеф-Бургер": {"price": 26000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800&auto=format&fit=crop"},
    "Coca-Cola": {"price": 7000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?q=80&w=800&auto=format&fit=crop"},
    "Чай": {"price": 5000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?q=80&w=800&auto=format&fit=crop"},
    "Супер-комбо": {"price": 45000, "cat": "combo", "photo": "https://images.unsplash.com/photo-1610614819513-58e34989848b?q=80&w=800&auto=format&fit=crop"}
}

CATEGORIES = {
    "burgers": {"ru": "🍔 Бургеры", "uz": "🍔 Burgerlar"},
    "drinks": {"ru": "🥤 Напитки", "uz": "🥤 Ichimliklar"},
    "combo": {"ru": "📦 Комбо", "uz": "📦 Kombo"}
}

user_languages = {}
user_carts = {}
processing_orders = set()
pending_orders = {} 

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_lang(user_id):
    return user_languages.get(user_id, "ru")

def add_to_cart(user_id, product):
    if product not in PRODUCTS:
        return
    user_carts.setdefault(user_id, {})
    user_carts[user_id][product] = user_carts[user_id].get(product, 0) + 1

def remove_from_cart(user_id, product):
    cart = user_carts.get(user_id)
    if not cart or product not in cart:
        return
    cart[product] -= 1
    if cart[product] <= 0:
        del cart[product]
    if not cart:
        user_carts.pop(user_id, None)

def calculate_total(user_id):
    cart = user_carts.get(user_id)
    if not cart:
        return 0
    return sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)

def build_cart_text(user_id):
    lang = get_lang(user_id)
    currency = TEXTS[lang]["currency"]
    cart = user_carts.get(user_id)
    
    if not cart:
        return TEXTS[lang]["cart_empty"]
    
    lines = [TEXTS[lang]["cart_title"], ""]
    for product, quantity in cart.items():
        if product not in PRODUCTS:
            continue
        subtotal = PRODUCTS[product]["price"] * quantity
        lines.append(f"• {product} × {quantity} = {subtotal:,} {currency}")
    
    total = calculate_total(user_id)
    lines.append("")
    lines.append(f"{TEXTS[lang]['cart_total']} {total:,} {currency}")
    lines.append(TEXTS[lang]["cart_hint"])
    
    return "\n".join(lines)

def build_phone_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["phone_btn"], request_contact=True))
    return builder.as_markup(resize_keyboard=True)

# =========================
# ОТПРАВКА ЗАКАЗА
# =========================

async def send_final_order(user_id, lang, comment=None):
    data = pending_orders.pop(user_id, None)
    if not data:
        return

    phone = data["phone"]
    currency = TEXTS[lang]["currency"]
    
    order_text = ""
    for product, quantity in data["cart"].items():
        if product not in PRODUCTS:
            continue
        subtotal = PRODUCTS[product]["price"] * quantity
        order_text += f"• {product} × {quantity} = {subtotal:,} {currency}\n"

    comment_text = f"\n📝 <b>Комментарий:</b> {comment}\n" if comment else ""

    admin_message = (
        "🔔 НОВЫЙ ЗАКАЗ!\n---------------------------\n"
        f"👤 Клиент: {data['first_name']}\n"
        f"🔗 Telegram: {data['username']}\n"
        f"📞 Телефон: {phone}\n"
        "---------------------------\n🍔 ЗАКАЗ:\n"
        f"{order_text}\n"
        f"💰 ИТОГО: {data['total']:,} {currency}\n"
        f"{comment_text}"
        "---------------------------\n⚠️ Свяжитесь с клиентом."
    )

    admin_notified = False
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode="HTML")
            admin_notified = True
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")
            
    thanks_key = "thanks" if admin_notified else "thanks_warn"
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    await bot.send_message(
        chat_id=user_id,
        text=TEXTS[lang][thanks_key].format(phone, SUPPORT_PHONE),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    processing_orders.discard(user_id)

# =========================
# ГЛАВНОЕ МЕНЮ И КОРЗИНА
# =========================

async def show_main_menu(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["menu_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["addr_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["lang_btn"]))
    builder.adjust(1)
    await message.answer(TEXTS[lang]["welcome"], reply_markup=builder.as_markup(resize_keyboard=True))

async def show_cart(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    cart = user_carts.get(user_id, {})
    builder = ReplyKeyboardBuilder()

    for product in cart.keys():
        if product not in PRODUCTS:
            continue
        builder.add(types.KeyboardButton(text=f"{MINUS_PREFIX}{product}"))
        builder.add(types.KeyboardButton(text=f"{PLUS_PREFIX}{product}"))

    builder.add(types.KeyboardButton(text=TEXTS[lang]["order_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["clear_cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    adjust_sizes = [2] * len(cart) + [1, 1, 1]
    builder.adjust(*adjust_sizes)

    await message.answer(build_cart_text(user_id), reply_markup=builder.as_markup(resize_keyboard=True), parse_mode="HTML")

# =========================
# ХЕНДЛЕРЫ: КОМАНДЫ И ЯЗЫК
# =========================

@dp.message(CommandStart())
@dp.message(lambda msg: msg.text == "🌐 Сменить язык / Tilni o'zgartirish")
async def choose_language(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🇷🇺 Русский"))
    builder.add(types.KeyboardButton(text="🇺🇿 O'zbekcha"))
    builder.adjust(2)
    await message.answer("🇷🇺 Выберите язык / 🇺🇿 Tilni tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda msg: msg.text in ["🇷🇺 Русский", "🇺🇿 O'zbekcha"])
async def select_language(message: types.Message):
    if message.text == "🇷🇺 Русский":
        user_languages[message.from_user.id] = "ru"
    elif message.text == "🇺🇿 O'zbekcha":
        user_languages[message.from_user.id] = "uz"
    await show_main_menu(message)

@dp.message(Command("cart"))
async def cmd_cart(message: types.Message):
    await show_cart(message)

# =========================
# КРАСИВОЕ МЕНЮ (INLINE КНОПКИ)
# =========================

@dp.message(lambda msg: msg.text in ["🍔 Посмотреть Меню", "🍔 Menyuni ko'rish"])
async def show_categories(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки категорий
    builder.button(text=CATEGORIES["burgers"][lang], callback_data="cat_burgers")
    builder.button(text=CATEGORIES["drinks"][lang], callback_data="cat_drinks")
    builder.button(text=CATEGORIES["combo"][lang], callback_data="cat_combo")
    builder.adjust(2, 1) # 2 кнопки в ряд, 1 снизу
    
    await message.answer(TEXTS[lang]["select_cat"], reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category_items(callback: types.CallbackQuery):
    await callback.answer() # Убираем часики на кнопке
    cat_id = callback.data.split("_")[1]
    lang = get_lang(callback.from_user.id)
    
    # Берем первый товар из категории, чтобы показать карточку
    items = [k for k, v in PRODUCTS.items() if v["cat"] == cat_id]
    if not items:
        return
        
    await show_item_card(callback.message, items[0], lang, cat_id)

async def show_item_card(message: types.Message, product_name: str, lang: str, cat_id: str):
    product = PRODUCTS[product_name]
    currency = TEXTS[lang]["currency"]
    
    # Получаем все товары этой категории для кнопок
    items = [k for k, v in PRODUCTS.items() if v["cat"] == cat_id]
    
    builder = InlineKeyboardBuilder()
    for item in items:
        price = PRODUCTS[item]["price"]
        # Если товар уже в корзине, показываем это
        builder.button(text=f"➕ {item} | {price:,} {currency}", callback_data=f"add_{item}")
    
    builder.button(text=TEXTS[lang]["back"], callback_data="back_to_cats")
    builder.adjust(1) # Кнопки добавления в столбик
    
    caption = (
        f"<b>{product_name}</b>\n"
        f"💰 Цена: {product['price']:,} {currency}\n\n"
        f"Нажмите на кнопку ниже, чтобы добавить в корзину:"
    )
    
    # Отправляем фото с кнопками
    try:
        await message.answer_photo(
            photo=product["photo"],
            caption=caption,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        # Если фото не загрузилось, отправляем текстом
        await message.answer(caption, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "back_to_cats")
async def back_to_cats(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete() # Удаляем фото
    lang = get_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=CATEGORIES["burgers"][lang], callback_data="cat_burgers")
    builder.button(text=CATEGORIES["drinks"][lang], callback_data="cat_drinks")
    builder.button(text=CATEGORIES["combo"][lang], callback_data="cat_combo")
    builder.adjust(2, 1)
    await callback.message.answer(TEXTS[lang]["select_cat"], reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_item_inline(callback: types.CallbackQuery):
    product_name = callback.data[4:] # отрезаем "add_"
    user_id = callback.from_user.id
    lang = get_lang(user_id)
    
    if product_name in PRODUCTS:
        add_to_cart(user_id, product_name)
        # Показываем всплывающее окошко, что добавлено
        await callback.answer(f"✅ {product_name} добавлен!", show_alert=False)
    else:
        await callback.answer("Ошибка", show_alert=True)

# =========================
# ХЕНДЛЕРЫ: КОРЗИНА (КНОПКИ ВНИЗУ)
# =========================

@dp.message(lambda msg: msg.text in ["🧺 Моя корзина", "🧺 Savatim"])
async def open_cart(message: types.Message):
    await show_cart(message)

@dp.message(lambda msg: msg.text is not None and msg.text.startswith(PLUS_PREFIX))
async def increase_item(message: types.Message):
    product = message.text[len(PLUS_PREFIX):].strip()
    if product in PRODUCTS:
        add_to_cart(message.from_user.id, product)
    await show_cart(message)

@dp.message(lambda msg: msg.text is not None and msg.text.startswith(MINUS_PREFIX))
async def decrease_item(message: types.Message):
    product = message.text[len(MINUS_PREFIX):].strip()
    if product in PRODUCTS:
        remove_from_cart(message.from_user.id, product)
    await show_cart(message)

@dp.message(lambda msg: msg.text in ["🗑 Очистить корзину", "🗑 Savatni tozalash"])
async def clear_cart(message: types.Message):
    user_carts.pop(message.from_user.id, None)
    lang = get_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["cart_cleared"])

@dp.message(lambda msg: msg.text in ["📍 Узнать Адрес", "📍 Manzilni bilish"])
async def show_address(message: types.Message):
    lang = get_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["address"])

# =========================
# ХЕНДЛЕРЫ: ОФОРМЛЕНИЕ
# =========================

@dp.message(lambda msg: msg.text in ["🛒 Оформить заказ", "🛒 Buyurtma berish"])
async def request_phone(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    if not user_carts.get(user_id):
        await message.answer(TEXTS[lang]["cart_empty"])
        return
    await message.answer(TEXTS[lang]["phone_req"], reply_markup=build_phone_keyboard(lang))

@dp.message(lambda msg: msg.contact is not None)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    if message.contact.user_id != user_id:
        await message.answer(TEXTS[lang]["phone_wrong"], reply_markup=build_phone_keyboard(lang))
        return

    if user_id in processing_orders or user_id in pending_orders:
        return

    cart = user_carts.get(user_id)
    if not cart:
        await message.answer(TEXTS[lang]["cart_empty"])
        return

    processing_orders.add(user_id)
    pending_orders[user_id] = {
        "phone": message.contact.phone_number,
        "cart": cart.copy(),
        "total": calculate_total(user_id),
        "username": f"@{message.from_user.username}" if message.from_user.username else "Нет",
        "first_name": message.from_user.first_name
    }
    user_carts.pop(user_id, None)

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["skip_btn"]))
    
    await message.answer(TEXTS[lang]["ask_comment"], reply_markup=builder.as_markup(resize_keyboard=True), parse_mode="HTML")

@dp.message(lambda msg: msg.text in ["⏩ Пропустить", "⏩ O'tkazib yuborish"])
async def skip_comment(message: types.Message):
    user_id = message.from_user.id
    if user_id in pending_orders:
        await send_final_order(user_id, get_lang(user_id), comment=None)

@dp.message(lambda msg: msg.from_user.id in pending_orders and msg.text is not None)
async def handle_comment(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    await message.answer(TEXTS[lang]["comment_added"])
    await send_final_order(user_id, lang, comment=message.text.strip())

@dp.message(lambda msg: msg.text in ["🔙 Назад", "🔙 Orqaga"])
async def back_button(message: types.Message):
    await show_main_menu(message)

@dp.message()
async def fallback(message: types.Message):
    await show_main_menu(message)

@dp.error()
async def error_handler(event: types.ErrorEvent):
    logger.error(f"Ошибка: {event.exception}", exc_info=event.exception)

# =========================
# WEBHOOK И HEALTHCHECK
# =========================

async def handle_webhook(request: web.Request):
    try:
        update_data = await request.json()
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")
    return web.Response(status=200)

async def healthcheck(request: web.Request):
    return web.Response(text="Bot is running!")

async def heartbeat():
    while True:
        await asyncio.sleep(3600)
        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(ADMIN_CHAT_ID, "💚 Бот работает")
            except Exception:
                pass

async def on_startup(app: web.Application):
    webhook_host = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_HOST")
    if not webhook_host:
        return
    webhook_url = f"{webhook_host}/webhook/{TOKEN}"
    logger.info(f"Устанавливаю вебхук: {webhook_url}")
    
    try:
        await bot.set_my_commands([
            types.BotCommand(command="start", description="🏠 Главное меню"),
            types.BotCommand(command="cart", description="🧺 Моя корзина"),
        ])
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(webhook_url)
        asyncio.create_task(heartbeat())
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
