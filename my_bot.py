import asyncio
import logging
import os

from dotenv import load_dotenv
from aiohttp import web  # <--- ДОБАВЛЕНО ДЛЯ ВЕБХУКОВ

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# =========================
# НАСТРОЙКИ
# =========================

load_dotenv()

TOKEN = os.getenv("8712149697:AAFFO_wsiGudKkacoyJeEMcvE_5mhUE1kHo")

try:
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "8798573210"))
except ValueError:
    ADMIN_CHAT_ID = 8798573210

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
# (Блок TEXTS оставляем без изменений, чтобы не раздувать код. 
# Он точно такой же, как в твоем файле, я его просто пропущу для краткости,
# НО В ТВОЕМ ФАЙЛЕ ОН ДОЛЖЕН БЫТЬ!)
TEXTS = {
    "ru": { "welcome": "Выберите действие:", "menu_btn": "🍔 Посмотреть Меню", "addr_btn": "📍 Узнать Адрес", "lang_btn": "🌐 Сменить язык / Tilni o'zgartirish", "select_cat": "📋 Выберите интересующий вас раздел меню:", "burgers": "🍔 Бургеры", "drinks": "🥤 Напитки", "combo": "📦 Комбо-наборы", "back": "🔙 Назад", "address": "📍 Демо-адрес: Ташкент, Мирабадский район, ориентир: Госпитальный рынок.", "add_burger": "🍔 Добавить чизбургер", "add_chicken": "🍗 Добавить Шеф-Бургер", "add_cola": "🥤 Добавить Coca-Cola", "add_tea": "🍵 Добавить чай", "add_combo": "📦 Добавить Супер-комбо", "cart": "🧺 Моя корзина", "clear_cart": "🗑 Очистить корзину", "order_btn": "🛒 Оформить заказ", "cart_empty": "🧺 Ваша корзина пока пуста.", "cart_title": "🧺 ВАША КОРЗИНА:", "cart_total": "💰 Итого:", "currency": "сум", "phone_req": "📱 Для оформления заказа отправьте ваш номер телефона, нажав кнопку ниже:", "phone_btn": "📞 Отправить номер телефона", "phone_wrong": "❌ Пожалуйста, отправьте СВОЙ номер телефона — нажмите кнопку ниже.", "cart_cleared": "🗑 Корзина очищена.", "thanks": "✅ Спасибо! Ваш заказ принят.\n\n📞 Номер для связи: {}\n📞 Служба поддержки: {}", "thanks_warn": "✅ Ваш заказ принят.\n\n📞 Номер для связи: {}\n⚠️ Если с вами не свяжутся в течение 10 минут — позвоните: {}", "burger_list": "🍔 НАШИ БУРГЕРЫ:\n\n• Чизбургер классический — 28 000 сум\n• Шеф-Бургер с курицей — 26 000 сум", "drink_list": "🥤 НАШИ НАПИТКИ:\n\n• Coca-Cola 0.5л — 7 000 сум\n• Чай чёрный / зелёный — 5 000 сум", "combo_list": "📦 НАШИ ТОПОВЫЕ КОМБО:\n\n🔥 СУПЕР-КОМБО №1\nСостав: Бургер, фри, Coca-Cola.\n💰 Цена: 45 000 сум" },
    "uz": { "welcome": "Harakatni tanlang:", "menu_btn": "🍔 Menyuni ko'rish", "addr_btn": "📍 Manzilni bilish", "lang_btn": "🌐 Сменить язык / Tilni o'zgartirish", "select_cat": "📋 Kerakli bo'limni tanlang:", "burgers": "🍔 Burgerlar", "drinks": "🥤 Ichimliklar", "combo": "📦 Kombo-to'plamlar", "back": "🔙 Orqaga", "address": "📍 Demo-manzil: Toshkent, Mirobod tumani, mo'ljal: Gospitalniy bozori.", "add_burger": "🍔 Chizburger qo'shish", "add_chicken": "🍗 Shef-Burger qo'shish", "add_cola": "🥤 Coca-Cola qo'shish", "add_tea": "🍵 Choy qo'shish", "add_combo": "📦 Super-kombo qo'shish", "cart": "🧺 Savatim", "clear_cart": "🗑 Savatni tozalash", "order_btn": "🛒 Buyurtma berish", "cart_empty": "🧺 Savatingiz hozircha bo'sh.", "cart_title": "🧺 SAVATINGIZ:", "cart_total": "💰 Jami:", "currency": "so'm", "phone_req": "📱 Buyurtmani rasmiylashtirish uchun pastdagi tugmani bosib, telefon raqamingizni yuboring:", "phone_btn": "📞 Telefon raqamni yuborish", "phone_wrong": "❌ Iltimos, O'ZINGIZNING telefon raqamingizni yuboring — pastdagi tugmani bosing.", "cart_cleared": "🗑 Savat tozalandi.", "thanks": "✅ Rahmat! Buyurtmangiz qabul qilindi.\n\n📞 Aloqa raqamingiz: {}\n📞 Qo'llab-quvvatlash markazi: {}", "thanks_warn": "✅ Buyurtmangiz qabul qilindi.\n\n📞 Aloqa raqamingiz: {}\n⚠️ Agar 10 daqiqa ichida siz bilan bog'lanmasa — qo'ng'iroq qiling: {}", "burger_list": "🍔 BIZNING BURGERLAR:\n\n• Klassik chizburger — 28 000 so'm\n• Tovuqli Shef-Burger — 26 000 so'm", "drink_list": "🥤 ICHIMLIKLAR:\n\n• Coca-Cola 0.5l — 7 000 so'm\n• Qora / Ko'k choy — 5 000 so'm", "combo_list": "📦 BIZNING TOP KOMBOLAR:\n\n🔥 SUPER-KOMBO №1\nTarkibi: Burger, fri, Coca-Cola.\n💰 Narxi: 45 000 so'm" }
}

# =========================
# ТОВАРЫ И ДАННЫЕ
# =========================
PRODUCTS = {"Чизбургер": 28000, "Шеф-Бургер": 26000, "Coca-Cola": 7000, "Чай": 5000, "Супер-комбо": 45000}
user_languages = {}
user_carts = {}
processing_orders = set()

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
# (Все функции get_lang, add_to_cart, calculate_total, build_cart_text, build_phone_keyboard и т.д. 
# остаются без изменений, они у тебя правильные)

def get_lang(user_id): return user_languages.get(user_id, "ru")

def add_to_cart(user_id, product):
    if product not in PRODUCTS: return
    user_carts.setdefault(user_id, {})
    user_carts[user_id][product] = user_carts[user_id].get(product, 0) + 1

def remove_from_cart(user_id, product):
    cart = user_carts.get(user_id)
    if not cart or product not in cart: return
    cart[product] -= 1
    if cart[product] <= 0: del cart[product]
    if not cart: user_carts.pop(user_id, None)

def calculate_total(user_id):
    cart = user_carts.get(user_id)
    if not cart: return 0
    return sum(PRODUCTS[product] * quantity for product, quantity in cart.items() if product in PRODUCTS)

def build_cart_text(user_id):
    lang = get_lang(user_id)
    currency = TEXTS[lang]["currency"]
    cart = user_carts.get(user_id)
    if not cart: return TEXTS[lang]["cart_empty"]
    lines = [TEXTS[lang]["cart_title"], ""]
    for product, quantity in cart.items():
        if product not in PRODUCTS: continue
        subtotal = PRODUCTS[product] * quantity
        lines.append(f"• {product} × {quantity} = {subtotal:,} {currency}")
    total = calculate_total(user_id)
    lines.append("")
    lines.append(f"{TEXTS[lang]['cart_total']} {total:,} {currency}")
    return "\n".join(lines)

def build_phone_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=TEXTS[lang]["phone_btn"], request_contact=True))
    return builder.as_markup(resize_keyboard=True)

# =========================
# ХЕНДЛЕРЫ (ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ)
# =========================
# (Вставляешь сюда все свои @dp.message хендлеры: show_main_menu, show_cart, 
# choose_language, select_language, cmd_cart, cmd_help, cmd_test, menu_categories, 
# burgers_menu, drinks_menu, combo_menu, add_cheeseburger, add_chicken_burger, 
# add_cola, add_tea, add_combo, open_cart, increase_item, decrease_item, 
# clear_cart, show_address, request_phone, handle_contact, back_button, fallback, error_handler)

# --- ВСТАВЬ СЮДА СВОИ ХЕНДЛЕРЫ ИЗ СТАРОГО ФАЙЛА ---
# ... (они все правильные, я их не трогаю) ...

# =========================
# WEBHOOK СЕРВЕР
# =========================

async def handle_webhook(request: web.Request):
    """Обработчик входящих запросов от Telegram"""
    try:
        update_data = await request.json()
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
    return web.Response(status=200)

async def healthcheck(request: web.Request):
    """Чтобы Render видел, что сервер жив"""
    return web.Response(text="Bot is running!")
    
# =========================
# ФОНОВЫЕ ЗАДАЧИ
# =========================

async def heartbeat():
    """Раз в 6 часов пишет админу: бот жив."""
    while True:
        await asyncio.sleep(6 * 60 * 60)
        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(ADMIN_CHAT_ID, "💚 Бот работает")
            except Exception as e:
                logger.warning(f"Heartbeat не отправлен: {e}")

async def cleanup_carts():
    """Раз в сутки чистит пустые корзины из памяти."""
    while True:
        await asyncio.sleep(24 * 60 * 60)
        empty_ids = [uid for uid, cart in user_carts.items() if not cart]
        for uid in empty_ids:
            user_carts.pop(uid, None)
        if empty_ids:
            logger.info(f"🧹 Очищено {len(empty_ids)} пустых корзин")
            
async def on_startup(app: web.Application):
    """Действия при старте сервера"""
    # Render сам выдает URL сайта в переменную RENDER_EXTERNAL_URL
    # Если тестируешь локально - укажи свой ngrok URL в WEBHOOK_HOST
    webhook_host = os.getenv("WEBHOOK_HOST", os.getenv("RENDER_EXTERNAL_URL"))
    
    if not webhook_host:
        logger.error("❌ URL для вебхука не задан! Добавь WEBHOOK_HOST в переменные окружения.")
        return

    webhook_path = f"/webhook/{TOKEN}"
    webhook_url = f"{webhook_host}{webhook_path}"

    logger.info(f"Устанавливаю вебхук: {webhook_url}")

    try:
        # Регистрация команд
        await bot.set_my_commands([
            types.BotCommand(command="start", description="🏠 Главное меню"),
            types.BotCommand(command="cart", description="🧺 Моя корзина"),
            types.BotCommand(command="help", description="ℹ️ Помощь"),
        ])
        
        # Удаляем старый вебхук (на всякий случай) и ставим новый
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(webhook_url)
        
        # Запускаем фоновые задачи
        asyncio.create_task(heartbeat())
        asyncio.create_task(cleanup_carts())
        
    except Exception as e:
        logger.error(f"Ошибка при старте: {e}")

async def on_shutdown(app: web.Application):
    """Действия при выключении"""
    logger.info("🛑 Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не найден. Проверь файл .env")

    logger.info("🚀 ЗАПУСК БОТА В РЕЖИМЕ WEBHOOK...")
    
    # Render автоматически задает переменную PORT. Если ее нет, используем 8080.
    port = int(os.getenv("PORT", 8080))

    app = web.Application()
    app.router.add_post(f"/webhook/{TOKEN}", handle_webhook)
    app.router.add_get("/", healthcheck)  # Для проверки статуса

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=port)
