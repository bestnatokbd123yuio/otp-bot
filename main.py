import asyncio
import json
import os
import re
import html
import time
import logging
import nest_asyncio
from playwright.async_api import async_playwright
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Apply Nest Asyncio
nest_asyncio.apply()

# ================= CONFIGURATION =================
BOT_TOKEN = "8521240210:AAEowgQTD_2ieMhRoXSazou0hyNc6E0Q8TI"
ADMIN_ID = 6368375127
OTP_GROUP_LINK = "https://t.me/ibgotp"
DATA_FILE = "data.json"

# Panel Configuration
PANELS_CONFIG = [
    {
        "name": "Hadi_Panel",
        "login_url": "http://185.2.83.39/ints/login",
        "otp_url": "http://185.2.83.39/ints/agent/SMSCDRStats",
        "username": "saadagent",
        "password": "saadagent"
    },
    {
        "name": "Lamix_Panel",
        "login_url": "http://139.99.208.63/ints/login",
        "otp_url": "http://139.99.208.63/ints/agent/SMSCDRStats",
        "username": "sbshoaib85",
        "password": "sbshoaib85"
    }
]

logging.basicConfig(level=logging.CRITICAL)

# ================= GLOBAL VARS =================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

processed_otps = set()
active_pages = {} 
cooldowns = {} 

# Country Flags
COUNTRY_FLAGS = {
    "Myanmar": "🇲🇲", "Zimbabwe": "🇿🇼", "Zambia": "🇿🇲", "Vietnam": "🇻🇳", "USA": "🇺🇸", "UK": "🇬🇧",
    "Uganda": "🇺🇬", "Turkey": "🇹🇷", "Tunisia": "🇹🇳", "Thailand": "🇹🇭", "Tanzania": "🇹🇿",
    "Taiwan": "🇹🇼", "Sweden": "🇸🇪", "Spain": "🇪🇸", "South Africa": "🇿🇦", "Somalia": "🇸🇴",
    "Singapore": "🇸🇬", "Sierra Leone": "🇸🇱", "Serbia": "🇷🇸", "Senegal": "🇸🇳", "Saudi Arabia": "🇸🇦",
    "Russia": "🇷🇺", "Romania": "🇷🇴", "Qatar": "🇶🇦", "Portugal": "🇵🇹", "Poland": "🇵🇱",
    "Philippines": "🇵🇭", "Peru": "🇵🇪", "Paraguay": "🇵🇾", "Pakistan": "🇵🇰", "Oman": "🇴🇲",
    "Norway": "🇳🇴", "Nigeria": "🇳🇬", "Niger": "🇳🇪", "New Zealand": "🇳🇿", "Netherlands": "🇳🇱",
    "Nepal": "🇳🇵", "Namibia": "🇳🇦", "Myanmar": "🇲🇲", "Mozambique": "🇲🇿", "Morocco": "🇲🇦",
    "Mongolia": "🇲🇳", "Mexico": "🇲🇽", "Mauritius": "🇲🇺", "Mauritania": "🇲🇷", "Malta": "🇲🇹",
    "Mali": "🇲🇱", "Maldives": "🇲🇻", "Malaysia": "🇲🇾", "Malawi": "🇲🇼", "Madagascar": "🇲🇬",
    "Macau": "🇲🇴", "Luxembourg": "🇱🇺", "Lithuania": "🇱🇹", "Libya": "🇱🇾", "Liberia": "🇱🇷",
    "Lesotho": "🇱🇸", "Lebanon": "🇱🇧", "Latvia": "🇱🇻", "Laos": "🇱🇦", "Kyrgyzstan": "🇰🇬",
    "Kuwait": "🇰🇼", "Kenya": "🇰🇪", "Kazakhstan": "🇰🇿", "Jordan": "🇯🇴", "Japan": "🇯🇵",
    "Jamaica": "🇯🇲", "Ivory Coast": "🇨🇮", "Italy": "🇮🇹", "Israel": "🇮🇱", "Ireland": "🇮🇪",
    "Iraq": "🇮🇶", "Iran": "🇮🇷", "Indonesia": "🇮🇩", "India": "🇮🇳", "Iceland": "🇮🇸",
    "Hungary": "🇭🇺", "Hong Kong": "🇭🇰", "Honduras": "🇭🇳", "Haiti": "🇭🇹", "Guyana": "🇬🇾",
    "Guinea": "🇬🇳", "Guatemala": "🇬🇹", "Grenada": "🇬🇩", "Greece": "🇬🇷", "Ghana": "🇬🇭",
    "Germany": "🇩🇪", "Georgia": "🇬🇪", "Gambia": "🇬🇲", "Gabon": "🇬🇦", "France": "🇫🇷",
    "Finland": "🇫🇮", "Fiji": "🇫🇯", "Ethiopia": "🇪🇹", "Estonia": "🇪🇪", "Egypt": "🇪🇬",
    "Ecuador": "🇪🇨", "Dominica": "🇩🇲", "Djibouti": "🇩🇯", "Denmark": "🇩🇰", "Czech": "🇨🇿",
    "Cyprus": "🇨🇾", "Cuba": "🇨🇺", "Croatia": "🇭🇷", "Costa Rica": "🇨🇷", "Congo": "🇨🇬",
    "Comoros": "🇰🇲", "Colombia": "🇨🇴", "China": "🇨🇳", "Chile": "🇨🇱", "Chad": "🇹🇩",
    "Canada": "🇨🇦", "Cameroon": "🇨🇲", "Cambodia": "🇰🇭", "Burundi": "🇧🇮", "Burkina Faso": "🇧🇫",
    "Bulgaria": "🇧🇬", "Brunei": "🇧🇳", "Brazil": "🇧🇷", "Botswana": "🇧🇼", "Bosnia": "🇧🇦",
    "Bolivia": "🇧🇴", "Bhutan": "🇧🇹", "Benin": "🇧🇯", "Belize": "🇧🇿", "Belgium": "🇧🇪",
    "Belarus": "🇧🇾", "Bangladesh": "🇧🇩", "Bahrain": "🇧🇭", "Azerbaijan": "🇦🇿", "Austria": "🇦🇹",
    "Australia": "🇦🇺", "Armenia": "🇦🇲", "Argentina": "🇦🇷", "Angola": "🇦🇴", "Andorra": "🇦🇩",
    "Algeria": "🇩🇿", "Albania": "🇦🇱", "Afghanistan": "🇦🇫"
}

# ================= HELPER FUNCTIONS =================
def get_country_with_flag(range_text):
    range_lower = range_text.lower()
    for country, flag in COUNTRY_FLAGS.items():
        if country.lower() in range_lower:
            return f"{flag} {country}"
    return f"🌍 {range_text.split('-')[0]}"

def clean_text(text):
    return re.sub(r'[\W_]+', '', text).lower()

def load_data():
    default = {"services": {}, "active_sessions": {}}
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f: json.dump(default, f, indent=4)
        return default
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if "services" not in data: data["services"] = {}
            if "active_sessions" not in data: data["active_sessions"] = {}
            return data
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")
        return default

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    except: pass

def make_keyboard(items, back_btn=True, extra_btn=None, step_back=False):
    kb = []
    row = []
    for item in items:
        row.append(KeyboardButton(text=item))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    if extra_btn: kb.append([KeyboardButton(text=extra_btn)])
    
    nav = []
    if step_back: nav.append(KeyboardButton(text="🔙 Back"))
    if back_btn: nav.append(KeyboardButton(text="🔙 Main Menu"))
    if nav: kb.append(nav)
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ================= STATES =================
class UserFlow(StatesGroup):
    select_service = State()
    select_country = State()

class AdminAdd(StatesGroup):
    choose_method = State()
    new_service_name = State()
    new_country_name = State()
    old_select_service = State()
    old_select_country = State()
    old_confirm_action = State()
    get_file = State()

class AdminDelete(StatesGroup):
    select_service = State()
    select_country = State()
    confirm = State()

# ================= PLAYWRIGHT WORKER (FIXED SELECTOR & CLICK) =================
async def start_panel_worker(browser, config):
    global active_pages
    panel_name = config["name"]
    print(f"🚀 Initializing {panel_name}...")

    context = await browser.new_context(viewport={'width': 1280, 'height': 800})
    page = await context.new_page()
    active_pages[panel_name] = page

    async def try_login():
        print(f"🔄 {panel_name}: Checking State...")
        try:
            await page.goto(config["otp_url"], timeout=60000, wait_until='domcontentloaded')

            if "login" in page.url or await page.locator('input[name="username"]').is_visible():
                print(f"🔑 {panel_name}: Login Required...")
                await page.fill('input[name="username"]', config['username'])
                await page.fill('input[name="password"]', config['password'])

                captcha_result = None
                try:
                    body = await page.inner_text("body")
                    matches = re.findall(r'(\d{1,2})\s*\+\s*(\d{1,2})', body)
                    if matches:
                        captcha_result = int(matches[-1][0]) + int(matches[-1][1])
                except: pass

                if captcha_result is not None:
                    print(f"🧮 {panel_name}: Solved Captcha {captcha_result}")
                    await page.fill('input[name="capt"]', str(captcha_result))
                    await page.press('input[name="capt"]', 'Enter')
                    await page.wait_for_load_state('domcontentloaded')
                    
                    await asyncio.sleep(2)
                    if "SMSDashboard" in page.url:
                        print(f"⏩ {panel_name}: Redirecting Dashboard -> CDRStats...")
                        await page.goto(config["otp_url"], wait_until='domcontentloaded')
                    return True
                else:
                    return False
            else:
                if "SMSDashboard" in page.url:
                    print(f"⏩ {panel_name}: Redirecting Dashboard -> CDRStats...")
                    await page.goto(config["otp_url"], wait_until='domcontentloaded')
                return True

        except Exception as e:
            print(f"❌ {panel_name} Login/Nav Error: {e}")
            await asyncio.sleep(5)
            return False

    while not await try_login():
        await asyncio.sleep(3)

    print(f"✅ {panel_name}: Ready & Monitoring...")

    while True:
        try:
            # === AGGRESSIVE REDIRECT CHECK ===
            if "SMSDashboard" in page.url:
                print(f"⚠️ {panel_name}: Stuck on Dashboard, Forcing Redirect...")
                await page.goto(config["otp_url"], wait_until='domcontentloaded')
                await asyncio.sleep(2)
                continue 

            # === REFRESH STRATEGY: CLICK "SHOW REPORT" ===
            # পেজ রিলোড করার বদলে 'Show Report' বাটনে ক্লিক করা হবে।
            try:
                # বাটন খোঁজার চেষ্টা (Value অথবা Text দিয়ে)
                await page.locator('input[value="Show Report"], button:has-text("Show Report")').first.click(timeout=3000)
                await page.wait_for_load_state('domcontentloaded')
            except:
                # বাটন না পেলে রিলোড (ফলব্যাক)
                # print(f"⚠️ {panel_name}: Report button not found, reloading...")
                try: await page.reload()
                except: pass
            
            # সেশন চেক
            if "login" in page.url or await page.locator('input[name="username"]').is_visible():
                print(f"⚠️ {panel_name}: Session Expired! Re-logging...")
                await try_login()
                continue
            
            rows_data = []
            try:
                # === GENERIC TABLE SELECTOR ===
                # এখন নির্দিষ্ট #dt আইডি ছাড়াও যেকোনো টেবিল খুঁজবে
                rows_data = await page.evaluate('''() => {
                    const rows = Array.from(document.querySelectorAll('table tbody tr'));
                    return rows.map(row => {
                        const cols = row.querySelectorAll('td');
                        if (cols.length >= 6) {
                            return {
                                range: cols[1].innerText.trim(),  
                                number: cols[2].innerText.trim(), 
                                cli: cols[3].innerText.trim(),    
                                msg: cols[5].innerText.trim(),    
                                valid: true
                            };
                        }
                        return { valid: false };
                    });
                }''')
                
                # Debugging Output: এটা কনসোলে দেখাবে যে টেবিল পাওয়া গেছে কি না
                if len(rows_data) > 0:
                     print(f"👀 {panel_name}: Found {len(rows_data)} rows in table.")
                else:
                     pass
                     # print(f"⚠️ {panel_name}: Table empty or not found.")

            except Exception as e:
                print(f"❌ {panel_name} Scraping Error: {e}")

            data = load_data()
            active = data.get("active_sessions", {})
            
            for row in rows_data:
                if not row.get('valid'): continue
                
                raw_range = row['range']
                phone = row['number']
                service_cli = row['cli']
                msg = row['msg']
                
                clean_phone = re.sub(r'\D', '', phone)
                if len(clean_phone) < 5: continue
                
                unique_id = f"{clean_phone}-{msg[:30]}"
                
                if unique_id not in processed_otps:
                    matched_user = None
                    
                    # === ULTIMATE MATCHING LOGIC (LAST 7 DIGITS) ===
                    for assigned_num, info in active.items():
                        user_num = re.sub(r'\D', '', str(assigned_num))
                        
                        # 1. Exact Match
                        if user_num == clean_phone:
                            matched_user = info["id"]; break
                        
                        # 2. Last 7 Digits (Best for Country Codes)
                        if len(user_num) >= 7 and len(clean_phone) >= 7:
                            if user_num[-7:] == clean_phone[-7:]:
                                matched_user = info["id"]; break
                        
                        # 3. Contains Match
                        if len(user_num) > 5 and len(clean_phone) > 5:
                            if user_num in clean_phone or clean_phone in user_num:
                                matched_user = info["id"]; break
                    
                    if matched_user:
                        print(f"📩 [{panel_name}] MATCHED: {clean_phone} -> User: {matched_user}")
                        
                        code = "N/A"
                        possible_codes = re.findall(r'\b\d{4,8}\b', msg)
                        for pc in possible_codes:
                            if pc not in clean_phone:
                                code = pc
                                break
                        
                        svc_name = service_cli if service_cli else "Unknown Service"
                        country_info = get_country_with_flag(raw_range)
                        
                        formatted_msg = (
                            f"🔔 <b>{svc_name} OTP Received!</b>\n\n"
                            f"📱 <b>Number:</b> <code>{phone}</code>\n"
                            f"🌍 <b>Country:</b> {country_info}\n"
                            f"🔢 <b>Code:</b> <code>{code}</code>\n"
                            f"📥 <b>Message:</b> {html.escape(msg)}"
                        )
                        try:
                            await bot.send_message(matched_user, formatted_msg, parse_mode="HTML")
                        except Exception as e:
                            print(f"❌ Failed to send msg: {e}")
                    else:
                        print(f"⚠️ [{panel_name}] Unclaimed: {clean_phone} (Msg: {msg[:10]}...)")
                    
                    processed_otps.add(unique_id)
            
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ {panel_name} Loop Error: {e}")
            await asyncio.sleep(2)

# ================= BOT COMMANDS =================
@dp.message(Command("screen"))
async def send_screenshot(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    if not active_pages:
        await message.answer("⚠️ No active browsers found.")
        return

    status_msg = await message.answer("📸 Capturing...")
    for p_name, page in active_pages.items():
        try:
            path = f"screen_{clean_text(p_name)}.jpg"
            await page.screenshot(path=path, full_page=False, type='jpeg', quality=60)
            photo = FSInputFile(path)
            await message.answer_photo(photo, caption=f"🖥️ <b>{p_name}</b>\n🔗 {page.url}", parse_mode="HTML")
            if os.path.exists(path): os.remove(path)
        except: pass
    await status_msg.delete()

@dp.message(F.text == "🔙 Main Menu")
async def global_main(message: types.Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    buttons = [[KeyboardButton(text="📱 Get Number")]]
    if message.from_user.id == ADMIN_ID:
        buttons.append([KeyboardButton(text="📥 Add Stock"), KeyboardButton(text="🗑️ Delete Stock")])
    try: await message.answer(f"👋 Welcome {message.from_user.first_name}!", reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))
    except: pass

@dp.message(F.text == "📱 Get Number")
async def user_select_service(message: types.Message, state: FSMContext):
    data = load_data()
    services = list(data["services"].keys())
    if not services: await message.answer("❌ Service not available."); return
    await state.set_state(UserFlow.select_service)
    await message.answer("🛠️ Select Service:", reply_markup=make_keyboard(services, step_back=False))

@dp.message(UserFlow.select_service)
async def user_select_country(message: types.Message, state: FSMContext):
    if message.text == "🔙 Back": await cmd_start(message, state); return
    service = message.text
    data = load_data()
    if service not in data["services"]: await message.answer("❌ Invalid Service"); return
    await state.update_data(service=service)
    countries = list(data["services"][service].keys())
    await state.set_state(UserFlow.select_country)
    await message.answer(f"🌍 Select Country for {service}:", reply_markup=make_keyboard(countries, step_back=True))

@dp.message(UserFlow.select_country)
async def user_get_number(message: types.Message, state: FSMContext):
    if message.text == "🔙 Back":
        data = load_data()
        services = list(data["services"].keys())
        await state.set_state(UserFlow.select_service)
        await message.answer("🛠️ Select Service:", reply_markup=make_keyboard(services, step_back=False))
        return

    country = message.text
    user_data = await state.get_data()
    service = user_data.get('service')
    user_id = str(message.from_user.id)
    
    data = load_data()
    if country not in data["services"][service]: await message.answer("❌ Invalid Country"); return
    
    if not data["services"][service][country]:
        await message.answer(f"❌ No numbers available for {service}-{country}.")
        return

    number = data["services"][service][country].pop(0)
    data["active_sessions"][number] = {"id": user_id, "service": service, "country": country}
    save_data(data)
    
    await state.clear() 
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Change Number", callback_data=f"change_{service}_{country}")],
        [InlineKeyboardButton(text="👥 OTP Group", url=OTP_GROUP_LINK)]
    ])

    await message.answer(
        f"✅ <b>Number Assigned!</b>\n\n"
        f"🛠️ Service: {service}\n"
        f"🌍 Country: {country}\n"
        f"📞 Number: <code>{number}</code>",
        parse_mode="HTML",
        reply_markup=inline_kb
    )

# --- Change Number ---
@dp.callback_query(F.data.startswith("change_"))
async def change_number_handler(callback: types.CallbackQuery):
    try:
        parts = callback.data.split("_")
        service = parts[1]
        country = parts[2]
    except: return

    user_id = callback.from_user.id
    current_time = time.time()
    last_time = cooldowns.get(user_id, 0)
    
    if current_time - last_time < 3:
        wait = 3 - int(current_time - last_time)
        await callback.answer(f"⚠️ Wait {wait}s", show_alert=True)
        return

    cooldowns[user_id] = current_time
    data = load_data()

    if not data["services"].get(service, {}).get(country):
        await callback.answer("❌ No Stock!", show_alert=True)
        return

    new_number = data["services"][service][country].pop(0)
    
    to_delete = [num for num, info in data["active_sessions"].items() if str(info["id"]) == str(user_id)]
    for num in to_delete: del data["active_sessions"][num]

    data["active_sessions"][new_number] = {"id": str(user_id), "service": service, "country": country}
    save_data(data)

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Change Number", callback_data=f"change_{service}_{country}")],
        [InlineKeyboardButton(text="👥 OTP Group", url=OTP_GROUP_LINK)]
    ])

    try:
        await callback.message.edit_text(
            f"🔄 <b>Number Changed!</b>\n\n"
            f"🛠️ Service: {service}\n"
            f"🌍 Country: {country}\n"
            f"📞 New Number: <code>{new_number}</code>",
            parse_mode="HTML",
            reply_markup=inline_kb
        )
    except: pass

# ================= ADMIN PANEL =================
@dp.message(F.text == "📥 Add Stock")
async def admin_add_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminAdd.choose_method)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🆕 Create New"), KeyboardButton(text="➕ Add to Old")], [KeyboardButton(text="🔙 Main Menu")]], resize_keyboard=True)
    await message.answer("Select Option:", reply_markup=kb)

@dp.message(AdminAdd.choose_method, F.text == "🆕 Create New")
async def admin_new_svc(message: types.Message, state: FSMContext):
    await state.set_state(AdminAdd.new_service_name)
    await message.answer("1️⃣ Service Name:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(AdminAdd.new_service_name)
async def admin_new_country(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(AdminAdd.new_country_name)
    await message.answer(f"2️⃣ Country Name for {message.text}:")

@dp.message(AdminAdd.new_country_name)
async def admin_new_file(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(AdminAdd.get_file)
    await message.answer("3️⃣ Send Numbers (File/Text):")

@dp.message(AdminAdd.choose_method, F.text == "➕ Add to Old")
async def admin_old_start(message: types.Message, state: FSMContext):
    data = load_data()
    if not data["services"]: await message.answer("Empty!"); return
    await state.set_state(AdminAdd.old_select_service)
    await message.answer("📂 Select Service:", reply_markup=make_keyboard(list(data["services"].keys())))

@dp.message(AdminAdd.old_select_service)
async def admin_old_country(message: types.Message, state: FSMContext):
    if message.text == "🔙 Main Menu": await cmd_start(message, state); return
    data = load_data()
    if message.text not in data["services"]: return
    await state.update_data(service=message.text)
    await state.set_state(AdminAdd.old_select_country)
    await message.answer("🌍 Select Country:", reply_markup=make_keyboard(list(data["services"][message.text].keys()), extra_btn="➕ Add Country"))

@dp.message(AdminAdd.old_select_country)
async def admin_old_action(message: types.Message, state: FSMContext):
    if message.text == "🔙 Main Menu": await cmd_start(message, state); return
    if message.text == "➕ Add Country":
        await state.set_state(AdminAdd.new_country_name)
        await message.answer("🆕 New Country Name:", reply_markup=types.ReplyKeyboardRemove())
        return
    
    data = load_data()
    u_data = await state.get_data()
    if message.text not in data["services"][u_data['service']]: return
    await state.update_data(country=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="➕ Add Numbers"), KeyboardButton(text="🔙 Back")]], resize_keyboard=True)
    await state.set_state(AdminAdd.old_confirm_action)
    await message.answer(f"Stock: {len(data['services'][u_data['service']][message.text])}", reply_markup=kb)

@dp.message(AdminAdd.old_confirm_action)
async def admin_req_file(message: types.Message, state: FSMContext):
    if message.text == "➕ Add Numbers":
        await state.set_state(AdminAdd.get_file)
        await message.answer("📤 Send File/Text:", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "🔙 Back": await cmd_start(message, state)

@dp.message(AdminAdd.get_file)
async def admin_save(message: types.Message, state: FSMContext):
    dt = await state.get_data()
    svc, cnt = dt['service'], dt['country']
    nums = []
    
    if message.document:
        f = await bot.get_file(message.document.file_id)
        await bot.download_file(f.file_path, "t.txt")
        with open("t.txt", "r") as fl: lines = fl.readlines()
        os.remove("t.txt")
    elif message.text: lines = message.text.split('\n')
    else: return

    for l in lines:
        c = re.sub(r'\D', '', l.strip())
        if len(c)>5: nums.append(c)
    
    if not nums: await message.answer("No valid numbers."); return
    
    db = load_data()
    if svc not in db["services"]: db["services"][svc] = {}
    if cnt not in db["services"][svc]: db["services"][svc][cnt] = []
    
    ex = set(db["services"][svc][cnt])
    add = 0
    for n in nums:
        if n not in ex:
            db["services"][svc][cnt].append(n)
            add+=1
    
    save_data(db)
    await state.clear()
    await message.answer(f"✅ Added {add} numbers to {svc}-{cnt}!")
    await cmd_start(message, state)

@dp.message(F.text == "🗑️ Delete Stock")
async def admin_del(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = load_data()
    if not data["services"]: await message.answer("Empty!"); return
    await state.set_state(AdminDelete.select_service)
    await message.answer("Select Service:", reply_markup=make_keyboard(list(data["services"].keys())))

@dp.message(AdminDelete.select_service)
async def admin_del_cnt(message: types.Message, state: FSMContext):
    if message.text == "🔙 Main Menu": await cmd_start(message, state); return
    await state.update_data(service=message.text)
    data = load_data()
    await state.set_state(AdminDelete.select_country)
    await message.answer("Select Country:", reply_markup=make_keyboard(list(data["services"][message.text].keys())))

@dp.message(AdminDelete.select_country)
async def admin_del_con(message: types.Message, state: FSMContext):
    if message.text == "🔙 Main Menu": await cmd_start(message, state); return
    await state.update_data(country=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✅ Confirm"), KeyboardButton(text="❌ Cancel")]], resize_keyboard=True)
    await state.set_state(AdminDelete.confirm)
    await message.answer("Confirm Delete?", reply_markup=kb)

@dp.message(AdminDelete.confirm)
async def admin_del_fin(message: types.Message, state: FSMContext):
    if message.text == "✅ Confirm":
        d = await state.get_data()
        db = load_data()
        try:
            del db["services"][d['service']][d['country']]
            if not db["services"][d['service']]: del db["services"][d['service']]
            save_data(db)
            await message.answer("✅ Deleted!")
        except: pass
    await cmd_start(message, state)

# ================= MAIN EXECUTION =================
async def main():
    print("🚀 Bot Started with Button Click Strategy...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        tasks = [dp.start_polling(bot)]
        for panel in PANELS_CONFIG:
            tasks.append(start_panel_worker(browser, panel))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("Bot Stopped")
