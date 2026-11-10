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
        "sauce_offer": "🥫 Отличный выбор! Хотите добавить соус к заказу?",
        "sauce_added": "✅ Соус добавлен!"
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
        "sauce_offer": "🥫 Ajoyib tanlov! Buyurtmaga sous qo'shmoqchimisiz?",
        "sauce_added": "✅ Sous qo'shildi!"
    }
}

# =========================
# КАТЕГОРИИ
# =========================

CATEGORIES = {
    "burgers": {"ru": "🍔 Бургеры", "uz": "🍔 Burgerlar"},
    "lavash": {"ru": "🌯 Лаваши", "uz": "🌯 Lavashlar"},
    "snacks": {"ru": "🍟 Закуски", "uz": "🍟 Gazaklar"},
    "drinks": {"ru": "🥤 Напитки", "uz": "🥤 Ichimliklar"},
    "sauces": {"ru": "🧂 Соусы", "uz": "🧂 Souslar"},
    "combo": {"ru": "📦 Комбо", "uz": "📦 Kombo"}
}

# =========================
# ТОВАРЫ (ЦЕНЫ, ФОТО, ОПИСАНИЯ КОМБО)
# =========================

PRODUCTS = {
    # --- БУРГЕРЫ ---
    "Классик Бургер": {"price": 24000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=800"},
    "Чизбургер": {"price": 28000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800"},
    "Двойной Чизбургер": {"price": 38000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1586816001966-79b736744398?q=80&w=800"},
    "Шеф-Бургер": {"price": 26000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1594212844822-18d2b66e3724?q=80&w=800"},
    "Двойной Шеф-Бургер": {"price": 36000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1603064752734-4c48eff53d05?q=80&w=800"},
    "Острый Бургер": {"price": 29000, "cat": "burgers", "photo": "https://images.unsplash.com/photo-1615297928064-24977384d0da?q=80&w=800"},

    # --- ЛАВАШИ ---
    "Лаваш обычный": {"price": 25000, "cat": "lavash", "photo": "https://images.unsplash.com/photo-1628840042765-356cda07504e?q=80&w=800"},
    "Лаваш сырный": {"price": 30000, "cat": "lavash", "photo": "https://images.unsplash.com/photo-1604868189265-38f2854b6e48?q=80&w=800"},
    "Лаваш острый": {"price": 28000, "cat": "lavash", "photo": "https://images.unsplash.com/photo-1619895092538-128341789043?q=80&w=800"},

    # --- ЗАКУСКИ ---
    "Картошка фри (средняя)": {"price": 15000, "cat": "snacks", "photo": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?q=80&w=800"},
    "Картошка фри (большая)": {"price": 20000, "cat": "snacks", "photo": "https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?q=80&w=800"},
    "Наггетсы (6 шт)": {"price": 18000, "cat": "snacks", "photo": "https://images.unsplash.com/photo-1562967914-608f82629710?q=80&w=800"},
    "Крылышки (6 шт)": {"price": 32000, "cat": "snacks", "photo": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?q=80&w=800"},

    # --- НАПИТКИ ---
    "Coca-Cola 0.5": {"price": 7000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?q=80&w=800"},
    "Pepsi 0.5": {"price": 7000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?q=80&w=800"},
    "Fanta 0.5": {"price": 7000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1624517452488-04869289c4ca?q=80&w=800"},
    "Lipton 0.5": {"price": 8000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1556881286-fc6915169721?q=80&w=800"},
    "Сок (0.2)": {"price": 10000, "cat": "drinks", "photo": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?q=80&w=800"},

    # --- СОУСЫ ---
    "Соус сырный": {"price": 3000, "cat": "sauces", "photo": "https://images.unsplash.com/photo-1619860860774-1e2e17343432?q=80&w=800"},
    "Соус чесночный": {"price": 3000, "cat": "sauces", "photo": "https://images.unsplash.com/photo-1599321955726-e04842f9159f?q=80&w=800"},
    "Кетчуп": {"price": 2000, "cat": "sauces", "photo": "https://images.unsplash.com/photo-1607013251379-e6eecfffe234?q=80&w=800"},
    "Соус Барбекю": {"price": 3000, "cat": "sauces", "photo": "https://images.unsplash.com/photo-1589647427545-38dfc97e5a8f?q=80&w=800"},

    # --- КОМБО (С ОПИСАНИЕМ) ---
    "Комбо Соло": {
        "price": 45000, "cat": "combo", 
        "photo": "https://images.unsplash.com/photo-1610614819513-58e34989848b?q=80&w=800",
        "desc": "Состав: Чизбургер, Картошка фри (средняя), Coca-Cola 0.5"
    },
    "Узбекский пир": {
        "price": 75000, "cat": "combo", 
        "photo": "https://images.unsplash.com/photo-1610440042657-612c34d95e9f?q=80&w=800",
        "desc": "Состав: Двойной Шеф-Бургер, Картошка фри (средняя), Coca-Cola 1 литр"
    },
    "Семейный ужин": {
        "price": 150000, "cat": "combo", 
        "photo": "https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800",
        "desc": "Состав: 2 Двойных Чизбургера, 2 Лаваша, Картошка фри (большая), Наггетсы (6 шт), 2 Coca-Cola 0.5"
    },
    "Друзья навсегда": {
        "price": 199000, "cat": "combo", 
        "photo": "https://images.unsplash.com/photo-1594212844822-18d2b66e3724?q=80&w=800",
        "desc": "Состав: 3 Двойных Чизбургера, Картошка фри (большая), Наггетсы (9 шт), Pepsi 1.5 литра, 3 Соуса на выбор"
    }
}

# =========================
# БАЗА ДАННЫХ (В ПАМЯТИ)
# =========================
user_languages = {}
user_carts = {}
processing_orders = set()
pending_orders = {} 

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_lang(user_id):
    return user_languages.get(user_id, "ru")

def add_to_cart(user_id, product, qty=1):
    if product not in PRODUCTS: return
    user_carts.setdefault(user_id, {})
    user_carts[user_id][product] = user_carts[user_id].get(product, 0) + qty

def remove_from_cart(user_id, product):
    cart = user_carts.get(user_id)
    if not cart or product not in cart: return
    cart[product] -= 1
    if cart[product] <= 0: del cart[product]
    if not cart: user_carts.pop(user_id, None)

def calculate_total(user_id):
    cart = user_carts.get(user_id)
    if not cart: return 0
    return sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)

def build_cart_text(user_id):
    lang = get_lang(user_id)
    currency = TEXTS[lang]["currency"]
    cart = user_carts.get(user_id)
    
    if not cart: return TEXTS[lang]["cart_empty"]
    
    lines = [TEXTS[lang]["cart_title"], ""]
    for product, quantity in cart.items():
        if product in PRODUCTS:
            subtotal = PRODUCTS[product]["price"] * quantity
            lines.append(f"• {product} × {quantity} = {subtotal:,} {currency}")
    
    total = calculate_total(user_id)
    lines.extend(["", f"{TEXTS[lang]['cart_total']} {total:,} {currency}", TEXTS[lang]["cart_hint"]])
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
    if not data: return

    phone = data["phone"]
    currency = TEXTS[lang]["currency"]
    
    order_text = "".join(f"• {p} × {q} = {PRODUCTS[p]['price'] * q:,} {currency}\n" for p, q in data["cart"].items() if p in PRODUCTS)
    comment_text = f"\n📝 <b>Комментарий:</b> {comment}\n" if comment else ""

    admin_message = (
        f"🔔 НОВЫЙ ЗАКАЗ!\n---------------------------\n"
        f"👤 Клиент: {data['first_name']}\n🔗 Telegram: {data['username']}\n📞 Телефон: {phone}\n"
        f"---------------------------\n🍔 ЗАКАЗ:\n{order_text}\n💰 ИТОГО: {data['total']:,} {currency}\n{comment_text}"
        f"---------------------------\n⚠️ Свяжитесь с клиентом."
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

    await bot.send_message(user_id, TEXTS[lang][thanks_key].format(phone, SUPPORT_PHONE), reply_markup=builder.as_markup(resize_keyboard=True))
    processing_orders.discard(user_id)

# =========================
# ГЛАВНОЕ МЕНЮ И КОРЗИНА
# =========================

async def show_main_menu(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["menu_btn"]), types.KeyboardButton(text=TEXTS[lang]["addr_btn"]),
                types.KeyboardButton(text=TEXTS[lang]["cart"]), types.KeyboardButton(text=TEXTS[lang]["lang_btn"]))
    builder.adjust(1)
    await message.answer(TEXTS[lang]["welcome"], reply_markup=builder.as_markup(resize_keyboard=True))

async def show_cart(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    cart = user_carts.get(user_id, {})
    builder = ReplyKeyboardBuilder()

    for product in cart.keys():
        if product in PRODUCTS:
            builder.add(types.KeyboardButton(text=f"{MINUS_PREFIX}{product}"), types.KeyboardButton(text=f"{PLUS_PREFIX}{product}"))

    builder.add(types.KeyboardButton(text=TEXTS[lang]["order_btn"]), types.KeyboardButton(text=TEXTS[lang]["clear_cart"]), types.KeyboardButton(text=TEXTS[lang]["back"]))
    builder.adjust(*([2] * len(cart) + [1, 1, 1]))

    await message.answer(build_cart_text(user_id), reply_markup=builder.as_markup(resize_keyboard=True), parse_mode="HTML")

# =========================
# КОМАНДЫ И ЯЗЫК
# =========================

@dp.message(CommandStart())
@dp.message(lambda msg: msg.text == "🌐 Сменить язык / Tilni o'zgartirish")
async def choose_language(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇺🇿 O'zbekcha"))
    builder.adjust(2)
    await message.answer("🇷🇺 Выберите язык / 🇺🇿 Tilni tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda msg: msg.text in ["🇷🇺 Русский", "🇺🇿 O'zbekcha"])
async def select_language(message: types.Message):
    user_languages[message.from_user.id] = "ru" if message.text == "🇷🇺 Русский" else "uz"
    await show_main_menu(message)

@dp.message(Command("cart"))
async def cmd_cart(message: types.Message): await show_cart(message)

# =========================
# МЕНЮ (INLINE КНОПКИ)
# =========================

@dp.message(lambda msg: msg.text in ["🍔 Посмотреть Меню", "🍔 Menyuni ko'rish"])
async def show_categories(message: types.Message):
    lang = get_lang(message.from_user.id)
    builder = InlineKeyboardBuilder()
    for cat_id, cat_names in CATEGORIES.items():
        builder.button(text=cat_names[lang], callback_data=f"cat_{cat_id}")
    builder.adjust(2)
    await message.answer(TEXTS[lang]["select_cat"], reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category_items(callback: types.CallbackQuery):
    await callback.answer()
    cat_id = callback.data.split("_")[1]
    lang = get_lang(callback.from_user.id)
    items = [k for k, v in PRODUCTS.items() if v["cat"] == cat_id]
    if items: await show_item_card(callback.message, items[0], lang, cat_id)

async def show_item_card(message: types.Message, product_name: str, lang: str, cat_id: str):
    product = PRODUCTS[product_name]
    currency = TEXTS[lang]["currency"]
    items = [k for k, v in PRODUCTS.items() if v["cat"] == cat_id]
    
    builder = InlineKeyboardBuilder()
    for item in items:
        price = PRODUCTS[item]["price"]
        builder.button(text=f"➕ {item} | {price:,} {currency}", callback_data=f"add_{item}")
    builder.button(text=TEXTS[lang]["back"], callback_data="back_to_cats")
    builder.adjust(1) 
    
    # Выводим описание для комбо
    desc_text = f"\n<i>{product.get('desc', '')}</i>\n" if "desc" in product else ""
    caption = f"<b>{CATEGORIES[cat_id][lang]}</b>\n{desc_text}\nВыберите товар, чтобы добавить:"
    
    try:
        await message.answer_photo(photo=product["photo"], caption=caption, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        await message.answer(caption, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "back_to_cats")
async def back_to_cats(callback: types.CallbackQuery):
    await callback.answer()
    try: await callback.message.delete()
    except: pass
    await show_categories(callback.message)

# =========================
# ДОБАВЛЕНИЕ В КОРЗИНУ И АПСЕЛЛ СОУСОВ
# =========================

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_item_inline(callback: types.CallbackQuery):
    product_name = callback.data[4:]
    user_id = callback.from_user.id
    lang = get_lang(user_id)
    
    if product_name in PRODUCTS:
        add_to_cart(user_id, product_name)
        await callback.answer(f"✅ {product_name} добавлен!", show_alert=False)
        
        # Апселл соусов (если это не соус и не напиток)
        if PRODUCTS[product_name]["cat"] in ["burgers", "lavash", "snacks", "combo"]:
            builder = InlineKeyboardBuilder()
            for p, data in PRODUCTS.items():
                if data["cat"] == "sauces":
                    builder.button(text=f"🥫 {p} (+{data['price']:,})", callback_data=f"sauce_{p}")
            builder.adjust(2)
            await callback.message.answer(TEXTS[lang]["sauce_offer"], reply_markup=builder.as_markup())
    else:
        await callback.answer("Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("sauce_"))
async def add_sauce_inline(callback: types.CallbackQuery):
    sauce_name = callback.data[6:]
    user_id = callback.from_user.id
    lang = get_lang(user_id)
    
    if sauce_name in PRODUCTS:
        add_to_cart(user_id, sauce_name)
        await callback.answer(TEXTS[lang]["sauce_added"], show_alert=False)
        # Удаляем сообщение с предложением соуса, чтобы не засорять чат
        try: await callback.message.delete()
        except: pass

# =========================
# КОРЗИНА (КНОПКИ ВНИЗУ)
# =========================

@dp.message(lambda msg: msg.text in ["🧺 Моя корзина", "🧺 Savatim"])
async def open_cart(message: types.Message): await show_cart(message)

@dp.message(lambda msg: msg.text is not None and msg.text.startswith(PLUS_PREFIX))
async def increase_item(message: types.Message):
    p = message.text[len(PLUS_PREFIX):].strip()
    if p in PRODUCTS: add_to_cart(message.from_user.id, p)
    await show_cart(message)

@dp.message(lambda msg: msg.text is not None and msg.text.startswith(MINUS_PREFIX))
async def decrease_item(message: types.Message):
    p = message.text[len(MINUS_PREFIX):].strip()
    if p in PRODUCTS: remove_from_cart(message.from_user.id, p)
    await show_cart(message)

@dp.message(lambda msg: msg.text in ["🗑 Очистить корзину", "🗑 Savatni tozalash"])
async def clear_cart(message: types.Message):
    user_carts.pop(message.from_user.id, None)
    await message.answer(TEXTS[get_lang(message.from_user.id)]["cart_cleared"])

@dp.message(lambda msg: msg.text in ["📍 Узнать Адрес", "📍 Manzilni bilish"])
async def show_address(message: types.Message):
    await message.answer(TEXTS[get_lang(message.from_user.id)]["address"])

# =========================
# ОФОРМЛЕНИЕ ЗАКАЗА
# =========================

@dp.message(lambda msg: msg.text in ["🛒 Оформить заказ", "🛒 Buyurtma berish"])
async def request_phone(message: types.Message):
    user_id, lang = message.from_user.id, get_lang(message.from_user.id)
    if not user_carts.get(user_id): await message.answer(TEXTS[lang]["cart_empty"]); return
    await message.answer(TEXTS[lang]["phone_req"], reply_markup=build_phone_keyboard(lang))

@dp.message(lambda msg: msg.contact is not None)
async def handle_contact(message: types.Message):
    user_id, lang = message.from_user.id, get_lang(message.from_user.id)

    if message.contact.user_id != user_id:
        await message.answer(TEXTS[lang]["phone_wrong"], reply_markup=build_phone_keyboard(lang))
        return

    if user_id in processing_orders or user_id in pending_orders or not user_carts.get(user_id): return

    processing_orders.add(user_id)
    pending_orders[user_id] = {
        "phone": message.contact.phone_number,
        "cart": user_carts.get(user_id).copy(),
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
    if message.from_user.id in pending_orders:
        await send_final_order(message.from_user.id, get_lang(message.from_user.id), comment=None)

@dp.message(lambda msg: msg.from_user.id in pending_orders and msg.text is not None)
async def handle_comment(message: types.Message):
    user_id = message.from_user.id
    await message.answer(TEXTS[get_lang(user_id)]["comment_added"])
    await send_final_order(user_id, get_lang(user_id), comment=message.text.strip())

@dp.message(lambda msg: msg.text in ["🔙 Назад", "🔙 Orqaga"])
async def back_button(message: types.Message): await show_main_menu(message)

@dp.message()
async def fallback(message: types.Message): await show_main_menu(message)

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
    except Exception as e: logger.error(f"Ошибка вебхука: {e}")
    return web.Response(status=200)

async def healthcheck(request: web.Request): return web.Response(text="Bot is running!")

async def heartbeat():
    while True:
        await asyncio.sleep(3600)
        if ADMIN_CHAT_ID:
            try: await bot.send_message(ADMIN_CHAT_ID, "💚 Бот работает")
            except: pass

async def on_startup(app: web.Application):
    webhook_host = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_HOST")
    if not webhook_host: return
    webhook_url = f"{webhook_host}/webhook/{TOKEN}"
    logger.info(f"Устанавливаю вебхук: {webhook_url}")
    try:
        await bot.set_my_commands([types.BotCommand(command="start", description="🏠 Главное меню"), types.BotCommand(command="cart", description="🧺 Моя корзина")])
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(webhook_url)
        asyncio.create_task(heartbeat())
    except Exception as e: logger.error(f"Ошибка при старте: {e}")

async def on_shutdown(app: web.Application): await bot.session.close()

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
