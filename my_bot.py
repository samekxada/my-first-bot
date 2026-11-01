import asyncio
import logging
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# =========================
# НАСТРОЙКИ
# =========================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

try:
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
except ValueError:
    ADMIN_CHAT_ID = 0

SUPPORT_PHONE = "+998 (90) 931-31-07"


# Префиксы для кнопок +/−
PLUS_PREFIX = "➕ "
MINUS_PREFIX = "➖ "


# =========================
# ЛОГГИРОВАНИЕ И БОТ
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
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

        "burgers": "🍔 Бургеры",
        "drinks": "🥤 Напитки",
        "combo": "📦 Комбо-наборы",

        "back": "🔙 Назад",

        "address":
            "📍 Демо-адрес: Ташкент, Мирабадский район, "
            "ориентир: Госпитальный рынок.",

        "add_burger": "🍔 Добавить чизбургер",
        "add_chicken": "🍗 Добавить Шеф-Бургер",

        "add_cola": "🥤 Добавить Coca-Cola",
        "add_tea": "🍵 Добавить чай",

        "add_combo": "📦 Добавить Супер-комбо",

        "cart": "🧺 Моя корзина",
        "clear_cart": "🗑 Очистить корзину",
        "order_btn": "🛒 Оформить заказ",

        "cart_empty": "🧺 Ваша корзина пока пуста.",
        "cart_title": "🧺 ВАША КОРЗИНА:",
        "cart_total": "💰 Итого:",
        "currency": "сум",

        "phone_req":
            "📱 Для оформления заказа отправьте ваш номер телефона, "
            "нажав кнопку ниже:",

        "phone_btn": "📞 Отправить номер телефона",
        "phone_wrong":
            "❌ Пожалуйста, отправьте СВОЙ номер телефона — "
            "нажмите кнопку ниже.",

        "cart_cleared": "🗑 Корзина очищена.",

        "thanks":
            "✅ Спасибо! Ваш заказ принят.\n\n"
            "📞 Номер для связи: {}\n"
            "📞 Служба поддержки: {}",

        "thanks_warn":
            "✅ Ваш заказ принят.\n\n"
            "📞 Номер для связи: {}\n"
            "⚠️ Если с вами не свяжутся в течение 10 минут — "
            "позвоните: {}",

        "burger_list":
            "🍔 НАШИ БУРГЕРЫ:\n\n"
            "• Чизбургер классический — 28 000 сум\n"
            "• Шеф-Бургер с курицей — 26 000 сум",

        "drink_list":
            "🥤 НАШИ НАПИТКИ:\n\n"
            "• Coca-Cola 0.5л — 7 000 сум\n"
            "• Чай чёрный / зелёный — 5 000 сум",

        "combo_list":
            "📦 НАШИ ТОПОВЫЕ КОМБО:\n\n"
            "🔥 СУПЕР-КОМБО №1\n"
            "Состав: Бургер, фри, Coca-Cola.\n"
            "💰 Цена: 45 000 сум"
    },

    "uz": {
        "welcome": "Harakatni tanlang:",

        "menu_btn": "🍔 Menyuni ko'rish",
        "addr_btn": "📍 Manzilni bilish",
        "lang_btn": "🌐 Сменить язык / Tilni o'zgartirish",

        "select_cat": "📋 Kerakli bo'limni tanlang:",

        "burgers": "🍔 Burgerlar",
        "drinks": "🥤 Ichimliklar",
        "combo": "📦 Kombo-to'plamlar",

        "back": "🔙 Orqaga",

        "address":
            "📍 Demo-manzil: Toshkent, Mirobod tumani, "
            "mo'ljal: Gospitalniy bozori.",

        "add_burger": "🍔 Chizburger qo'shish",
        "add_chicken": "🍗 Shef-Burger qo'shish",

        "add_cola": "🥤 Coca-Cola qo'shish",
        "add_tea": "🍵 Choy qo'shish",

        "add_combo": "📦 Super-kombo qo'shish",

        "cart": "🧺 Savatim",
        "clear_cart": "🗑 Savatni tozalash",
        "order_btn": "🛒 Buyurtma berish",

        "cart_empty": "🧺 Savatingiz hozircha bo'sh.",
        "cart_title": "🧺 SAVATINGIZ:",
        "cart_total": "💰 Jami:",
        "currency": "so'm",

        "phone_req":
            "📱 Buyurtmani rasmiylashtirish uchun pastdagi "
            "tugmani bosib, telefon raqamingizni yuboring:",

        "phone_btn": "📞 Telefon raqamni yuborish",
        "phone_wrong":
            "❌ Iltimos, O'ZINGIZNING telefon raqamingizni yuboring — "
            "pastdagi tugmani bosing.",

        "cart_cleared": "🗑 Savat tozalandi.",

        "thanks":
            "✅ Rahmat! Buyurtmangiz qabul qilindi.\n\n"
            "📞 Aloqa raqamingiz: {}\n"
            "📞 Qo'llab-quvvatlash markazi: {}",

        "thanks_warn":
            "✅ Buyurtmangiz qabul qilindi.\n\n"
            "📞 Aloqa raqamingiz: {}\n"
            "⚠️ Agar 10 daqiqa ichida siz bilan bog'lanmasa — "
            "qo'ng'iroq qiling: {}",

        "burger_list":
            "🍔 BIZNING BURGERLAR:\n\n"
            "• Klassik chizburger — 28 000 so'm\n"
            "• Tovuqli Shef-Burger — 26 000 so'm",

        "drink_list":
            "🥤 ICHIMLIKLAR:\n\n"
            "• Coca-Cola 0.5l — 7 000 so'm\n"
            "• Qora / Ko'k choy — 5 000 so'm",

        "combo_list":
            "📦 BIZNING TOP KOMBOLAR:\n\n"
            "🔥 SUPER-KOMBO №1\n"
            "Tarkibi: Burger, fri, Coca-Cola.\n"
            "💰 Narxi: 45 000 so'm"
    }
}


# =========================
# ТОВАРЫ
# =========================

PRODUCTS = {
    "Чизбургер": 28000,
    "Шеф-Бургер": 26000,
    "Coca-Cola": 7000,
    "Чай": 5000,
    "Супер-комбо": 45000
}


# =========================
# ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ
# =========================

user_languages = {}
user_carts = {}

# Кто прямо сейчас оформляет заказ (защита от двойных)
processing_orders = set()


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_lang(user_id):
    return user_languages.get(user_id, "ru")


def add_to_cart(user_id, product):
    if product not in PRODUCTS:
        return

    user_carts.setdefault(user_id, {})
    user_carts[user_id][product] = (
        user_carts[user_id].get(product, 0) + 1
    )


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

    return sum(
        PRODUCTS[product] * quantity
        for product, quantity in cart.items()
        if product in PRODUCTS
    )


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

        subtotal = PRODUCTS[product] * quantity
        lines.append(
            f"• {product} × {quantity} = {subtotal:,} {currency}"
        )

    total = calculate_total(user_id)
    lines.append("")
    lines.append(
        f"{TEXTS[lang]['cart_total']} {total:,} {currency}"
    )

    return "\n".join(lines)


def build_phone_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(
            text=TEXTS[lang]["phone_btn"],
            request_contact=True
        )
    )
    return builder.as_markup(resize_keyboard=True)


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

async def show_main_menu(message: types.Message):

    lang = get_lang(message.from_user.id)

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=TEXTS[lang]["menu_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["addr_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["lang_btn"]))

    builder.adjust(1)

    await message.answer(
        TEXTS[lang]["welcome"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# КОРЗИНА
# =========================

async def show_cart(message: types.Message):

    user_id = message.from_user.id
    lang = get_lang(user_id)

    cart = user_carts.get(user_id, {})

    builder = ReplyKeyboardBuilder()

    # Кнопки +/− для каждого товара
    for product in cart.keys():
        if product not in PRODUCTS:
            continue

        builder.add(
            types.KeyboardButton(text=f"{MINUS_PREFIX}{product}")
        )
        builder.add(
            types.KeyboardButton(text=f"{PLUS_PREFIX}{product}")
        )

    # Основные кнопки
    builder.add(types.KeyboardButton(text=TEXTS[lang]["order_btn"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["clear_cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    # Раскладка: пары +/−, потом по одной
    adjust_sizes = [2] * len(cart) + [1, 1, 1]

    builder.adjust(*adjust_sizes)

    await message.answer(
        build_cart_text(user_id),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# START / СМЕНА ЯЗЫКА
# =========================

@dp.message(CommandStart())
@dp.message(
    lambda msg:
    msg.text == "🌐 Сменить язык / Tilni o'zgartirish"
)
async def choose_language(message: types.Message):

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text="🇷🇺 Русский"))
    builder.add(types.KeyboardButton(text="🇺🇿 O'zbekcha"))

    builder.adjust(2)

    await message.answer(
        "🇷🇺 Выберите язык / 🇺🇿 Tilni tanlang:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(
    lambda msg:
    msg.text in [
        "🇷🇺 Русский",
        "🇺🇿 O'zbekcha"
    ]
)
async def select_language(message: types.Message):

    if message.text == "🇷🇺 Русский":
        user_languages[message.from_user.id] = "ru"

    elif message.text == "🇺🇿 O'zbekcha":
        user_languages[message.from_user.id] = "uz"

    await show_main_menu(message)


# =========================
# КОМАНДЫ /cart и /help
# =========================

@dp.message(Command("cart"))
async def cmd_cart(message: types.Message):
    await show_cart(message)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):

    help_text = (
        "ℹ️ <b>Помощь по боту</b>\n\n"
        "🛒 /cart — открыть корзину\n"
        "🏠 /start — главное меню\n"
        f"📞 Поддержка: {SUPPORT_PHONE}"
    )

    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("test"))
async def cmd_test(message: types.Message):

    if not ADMIN_CHAT_ID:
        await message.answer(
            "❌ ADMIN_CHAT_ID не задан в .env"
        )
        return

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="🧪 ТЕСТ: связь с админом работает!"
        )
        await message.answer(
            "✅ Тестовое сообщение отправлено. "
            "Проверь чат с ботом (если админ = ты, "
            "сообщение придёт сюда же)."
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка: {e}\n\n"
            f"Скорее всего:\n"
            f"1) ADMIN_CHAT_ID = {ADMIN_CHAT_ID} — неверный\n"
            f"2) Ты не нажимал /start у бота\n"
            f"3) Ты заблокировал бота"
        )
    help_text = (
        "ℹ️ <b>Помощь по боту</b>\n\n"
        "🛒 /cart — открыть корзину\n"
        "🏠 /start — главное меню\n"
        f"📞 Поддержка: {SUPPORT_PHONE}"
    )

    await message.answer(help_text, parse_mode="HTML")


# =========================
# ГЛАВНОЕ МЕНЮ → КАТЕГОРИИ
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🍔 Посмотреть Меню",
        "🍔 Menyuni ko'rish"
    ]
)
async def menu_categories(message: types.Message):

    lang = get_lang(message.from_user.id)

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=TEXTS[lang]["burgers"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["drinks"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["combo"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    builder.adjust(2)

    await message.answer(
        TEXTS[lang]["select_cat"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# БУРГЕРЫ
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🍔 Бургеры",
        "🍔 Burgerlar"
    ]
)
async def burgers_menu(message: types.Message):

    lang = get_lang(message.from_user.id)

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=TEXTS[lang]["add_burger"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["add_chicken"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    builder.adjust(2)

    await message.answer(
        TEXTS[lang]["burger_list"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# НАПИТКИ
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🥤 Напитки",
        "🥤 Ichimliklar"
    ]
)
async def drinks_menu(message: types.Message):

    lang = get_lang(message.from_user.id)

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=TEXTS[lang]["add_cola"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["add_tea"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    builder.adjust(2)

    await message.answer(
        TEXTS[lang]["drink_list"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# КОМБО
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "📦 Комбо-наборы",
        "📦 Kombo-to'plamlar"
    ]
)
async def combo_menu(message: types.Message):

    lang = get_lang(message.from_user.id)

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=TEXTS[lang]["add_combo"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["cart"]))
    builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

    builder.adjust(2)

    await message.answer(
        TEXTS[lang]["combo_list"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# =========================
# ДОБАВЛЕНИЕ ТОВАРОВ
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🍔 Добавить чизбургер",
        "🍔 Chizburger qo'shish"
    ]
)
async def add_cheeseburger(message: types.Message):

    add_to_cart(message.from_user.id, "Чизбургер")

    await message.answer("✅ Чизбургер добавлен в корзину!")


@dp.message(
    lambda msg:
    msg.text in [
        "🍗 Добавить Шеф-Бургер",
        "🍗 Shef-Burger qo'shish"
    ]
)
async def add_chicken_burger(message: types.Message):

    add_to_cart(message.from_user.id, "Шеф-Бургер")

    await message.answer("✅ Шеф-Бургер добавлен в корзину!")


@dp.message(
    lambda msg:
    msg.text in [
        "🥤 Добавить Coca-Cola",
        "🥤 Coca-Cola qo'shish"
    ]
)
async def add_cola(message: types.Message):

    add_to_cart(message.from_user.id, "Coca-Cola")

    await message.answer("✅ Coca-Cola добавлена в корзину!")


@dp.message(
    lambda msg:
    msg.text in [
        "🍵 Добавить чай",
        "🍵 Choy qo'shish"
    ]
)
async def add_tea(message: types.Message):

    add_to_cart(message.from_user.id, "Чай")

    await message.answer("✅ Чай добавлен в корзину!")


@dp.message(
    lambda msg:
    msg.text in [
        "📦 Добавить Супер-комбо",
        "📦 Super-kombo qo'shish"
    ]
)
async def add_combo(message: types.Message):

    add_to_cart(message.from_user.id, "Супер-комбо")

    await message.answer("✅ Супер-комбо добавлено в корзину!")


# =========================
# ОТКРЫТИЕ КОРЗИНЫ (кнопка)
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🧺 Моя корзина",
        "🧺 Savatim"
    ]
)
async def open_cart(message: types.Message):
    await show_cart(message)


# =========================
# ИЗМЕНЕНИЕ КОЛИЧЕСТВА (➖ / ➕)
# =========================

@dp.message(
    lambda msg:
    msg.text is not None
    and msg.text.startswith(PLUS_PREFIX)
)
async def increase_item(message: types.Message):

    product = message.text[len(PLUS_PREFIX):].strip()

    if product in PRODUCTS:
        add_to_cart(message.from_user.id, product)

    await show_cart(message)


@dp.message(
    lambda msg:
    msg.text is not None
    and msg.text.startswith(MINUS_PREFIX)
)
async def decrease_item(message: types.Message):

    product = message.text[len(MINUS_PREFIX):].strip()

    if product in PRODUCTS:
        remove_from_cart(message.from_user.id, product)

    await show_cart(message)


# =========================
# ОЧИСТКА КОРЗИНЫ
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🗑 Очистить корзину",
        "🗑 Savatni tozalash"
    ]
)
async def clear_cart(message: types.Message):

    user_carts.pop(message.from_user.id, None)

    lang = get_lang(message.from_user.id)

    await message.answer(TEXTS[lang]["cart_cleared"])


# =========================
# АДРЕС
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "📍 Узнать Адрес",
        "📍 Manzilni bilish"
    ]
)
async def show_address(message: types.Message):

    lang = get_lang(message.from_user.id)

    await message.answer(TEXTS[lang]["address"])


# =========================
# ОФОРМЛЕНИЕ ЗАКАЗА
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🛒 Оформить заказ",
        "🛒 Buyurtma berish"
    ]
)
async def request_phone(message: types.Message):

    user_id = message.from_user.id
    lang = get_lang(user_id)

    if not user_carts.get(user_id):
        await message.answer(TEXTS[lang]["cart_empty"])
        return

    await message.answer(
        TEXTS[lang]["phone_req"],
        reply_markup=build_phone_keyboard(lang)
    )


# =========================
# ПОЛУЧЕНИЕ ТЕЛЕФОНА
# =========================

@dp.message(lambda msg: msg.contact is not None)
async def handle_contact(message: types.Message):

    user_id = message.from_user.id
    lang = get_lang(user_id)

    # 1) Чужой контакт — просим свой и снова показываем кнопку
    if message.contact.user_id != user_id:
        await message.answer(
            TEXTS[lang]["phone_wrong"],
            reply_markup=build_phone_keyboard(lang)
        )
        return

    # 2) Уже обрабатываем заказ этого пользователя — игнорируем
    if user_id in processing_orders:
        logger.info(f"Повторный контакт от {user_id} — игнорируем")
        return

    # 3) Корзина пуста
    cart = user_carts.get(user_id)

    if not cart:
        await message.answer(TEXTS[lang]["cart_empty"])
        return

    # 4) Помечаем, что обрабатываем
    processing_orders.add(user_id)

    try:
        phone = message.contact.phone_number
        currency = TEXTS[lang]["currency"]

        username = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "Нет юзернейма"
        )

        first_name = message.from_user.first_name

        # Список товаров
        order_text = ""

        for product, quantity in cart.items():
            if product not in PRODUCTS:
                continue

            subtotal = PRODUCTS[product] * quantity
            order_text += (
                f"• {product} × {quantity} "
                f"= {subtotal:,} {currency}\n"
            )

        total = calculate_total(user_id)

        admin_message = (
            "🔔 НОВЫЙ ЗАКАЗ!\n"
            "---------------------------\n"
            f"👤 Клиент: {first_name}\n"
            f"🔗 Telegram: {username}\n"
            f"📞 Телефон: {phone}\n"
            "---------------------------\n"
            "🍔 ЗАКАЗ:\n"
            f"{order_text}\n"
            f"💰 ИТОГО: {total:,} {currency}\n"
            "---------------------------\n"
            "⚠️ Свяжитесь с клиентом для уточнения деталей."
        )

        # Уведомляем админа
        admin_notified = False

        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=admin_message
                )
                admin_notified = True
            except Exception as e:
                logger.error(f"Ошибка отправки админу: {e}")
        else:
            logger.warning(
                "ADMIN_CHAT_ID не задан — заказ не отправлен"
            )

        # Сообщение клиенту
        thanks_key = "thanks" if admin_notified else "thanks_warn"

        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text=TEXTS[lang]["back"]))

        await message.answer(
            TEXTS[lang][thanks_key].format(phone, SUPPORT_PHONE),
            reply_markup=builder.as_markup(resize_keyboard=True)
        )

        # Очищаем корзину
        user_carts.pop(user_id, None)

    finally:
        # Гарантированно снимаем флаг, даже если что-то упало
        processing_orders.discard(user_id)


# =========================
# КНОПКА НАЗАД
# =========================

@dp.message(
    lambda msg:
    msg.text in [
        "🔙 Назад",
        "🔙 Orqaga"
    ]
)
async def back_button(message: types.Message):
    await show_main_menu(message)


# =========================
# FALLBACK (всегда последним!)
# =========================

@dp.message()
async def fallback(message: types.Message):
    await show_main_menu(message)


# =========================
# ОБРАБОТЧИК ОШИБОК
# =========================

@dp.error()
async def error_handler(event: types.ErrorEvent):

    logger.error(
        f"Необработанная ошибка: {event.exception}",
        exc_info=event.exception
    )

    # Пытаемся сообщить пользователю (но не зацикливаемся)
    try:
        if event.update.message:
            await event.update.message.answer(
                "⚠️ Что-то пошло не так. Попробуйте ещё раз."
            )
    except Exception:
        pass


# =========================
# ФОНОВЫЕ ЗАДАЧИ
# =========================

async def heartbeat():
    """Раз в 6 часов пишет админу: бот жив."""
    while True:
        await asyncio.sleep(6 * 60 * 60)

        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    "💚 Бот работает"
                )
            except Exception as e:
                logger.warning(f"Heartbeat не отправлен: {e}")


async def cleanup_carts():
    """Раз в сутки чистит пустые корзины из памяти."""
    while True:
        await asyncio.sleep(24 * 60 * 60)

        empty_ids = [
            uid for uid, cart in user_carts.items()
            if not cart
        ]

        for uid in empty_ids:
            user_carts.pop(uid, None)

        if empty_ids:
            logger.info(
                f"🧹 Очищено {len(empty_ids)} пустых корзин"
            )


# =========================
# ЗАПУСК
# =========================

async def main():

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не найден. Проверь файл .env"
        )

    logger.info("🚀 БОТ КАФЕ ЗАПУЩЕН!")

    # Регистрация команд
    try:
        await bot.set_my_commands([
            types.BotCommand(
                command="start",
                description="🏠 Главное меню"
            ),
            types.BotCommand(
                command="cart",
                description="🧺 Моя корзина"
            ),
            types.BotCommand(
                command="help",
                description="ℹ️ Помощь"
            ),
        ])
    except Exception as e:
        logger.warning(f"Не удалось установить команды: {e}")

    # Сброс вебхука
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Не удалось сбросить вебхук: {e}")

    # Фоновые задачи — держим ссылки, чтобы их не собрал GC
    heartbeat_task = asyncio.create_task(heartbeat())
    cleanup_task = asyncio.create_task(cleanup_carts())

    # Главный цикл с нарастающей задержкой при сбоях
    failed_attempts = 0

    while True:
        try:
            await dp.start_polling(
                bot,
                polling_timeout=30
            )

            failed_attempts = 0

        except Exception as e:
            failed_attempts += 1
            wait = min(5 * failed_attempts, 60)

            logger.error(
                f"⚠️ Сбой #{failed_attempts}: {e}. "
                f"Перезапуск через {wait} сек..."
            )

            await asyncio.sleep(wait)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен вручную")