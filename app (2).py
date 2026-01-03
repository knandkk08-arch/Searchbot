import telebot
from telebot import types
import json
import os
import requests
from random import randint
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import time
import asyncio
import threading
import datetime
from concurrent.futures import ThreadPoolExecutor
from pyrogram.client import Client
from pyrogram.errors import FloodWait

# Bot Tokens
ADMIN_BOT_TOKEN = "8206676554:AAHBW0smVcvEJBDkLe-ypVj3HjEr3p2o-A0"
USER_BOT_TOKEN = "8432843027:AAEEz04mJVzCPe0iTuylD32laVPiLixAOkY"

# Pyrogram for Number Search (existing - don't touch)
NUMBER_SEARCH_PYROGRAM = {
    "api_id": 32612224,
    "api_hash": "9a3154504ec58fa48c175e3aa2973344",
    "phone": "+919341775612",
    "session_name": "number_search_account"
}

# Number Search Bot Username (configurable)
NUMBER_SEARCH_BOT_USERNAME = "@ZaverinBot"

# Pyrogram for Profile Search (Configure your account here)
PROFILE_SEARCH_PYROGRAM = {
    "api_id": 31342595,  # ← Enter your API ID here
    "api_hash": "5e0ebe64a090ee714bc1509258ace9be",  # ← Enter your API Hash here
    "phone": "+919904352414",  # ← Enter your phone number here
    "target_bot": "@pofliechecker17_bot",  # Target bot username
    "session_name": "profile_search_account"
}

# Pyrogram for Username Search - Configure your accounts here
USERNAME_SEARCH_PYROGRAMS = [
    {
        "api_id": 31055563,
        "api_hash": "56bf0baea8363da9a4ddf0d86fe6a536",
        "phone": "+917970421286",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_1"
    },
    {
        "api_id": 33577922,
        "api_hash": "7a091002eb54c52d89cc2909aa455b0f",
        "phone": "+916206785398",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_2"
    },
    {
        "api_id": 34925235,  # Account 3: Add your API ID
        "api_hash": "4f9b7b9fe20ebf60742714d4c850a8ce",
        "phone": "+916203363641",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_3"
    },
    {
        "api_id": 37195487,  # Account 4: Add your API ID
        "api_hash": "f630cc930e1ac56edcac9410b759de4a",
        "phone": "+919199316152",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_4"
    },
    {
        "api_id": 39782165,  # Account 5: Add your API ID
        "api_hash": "e0e665ae0de9e60ab4b1d77fcc71820c",
        "phone": "+919661948912",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_5"
    },
    {
        "api_id": 16402082,  # Account 6: Add your API ID
        "api_hash": "e1312302bf472a45b104b2a4028b34cc",
        "phone": "+917321831949",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_6"
    },
    {
        "api_id": 22546679,  # Account 7: Add your API ID
        "api_hash": "846b01bff0a64f1249b971e4524c82e8",
        "phone": "+919162696244",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_7"
    },
    {
        "api_id": 38391843,  # Account 8: Add your API ID
        "api_hash": "45eefeb83a6da7b92c959a52d648b8f9",
        "phone": "+918002619094",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_8"
    },
    {
        "api_id": 0,  # Account 9: Add your API ID
        "api_hash": "0",
        "phone": "0",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_9"
    },
    {
        "api_id":0,  # Account 10: Configure with unique API ID to enable
        "api_hash": "0",  # Add your unique API hash here
        "phone": "0",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_10"
    },
    {
        "api_id": 0,  # Account 11: Add your API ID
        "api_hash": "0",
        "phone": "0",
        "target_bot": "@Dfjyt_bot",
        "session_name": "username_search_account_11"
    }
]

# Currently active username search pyrogram index
ACTIVE_USERNAME_PYROGRAM_INDEX = 0

# Pyrogram account request limits (configurable per account)
USERNAME_PYROGRAM_LIMITS = {}  # Format: {account_index: limit}
USERNAME_PYROGRAM_REQUEST_COUNTS = {}  # Format: {account_index: current_count}

# Pricing Configuration (Handled by load_prices)
# NUMBER_SEARCH_PRICE = 4
# USERNAME_SEARCH_PRICE = 21
# PROFILE_SEARCH_PRICE = 10
MINIMUM_RECHARGE = 12

# Valid UTR for testing
VALID_UTR = "894569852152"

# Admin Configuration
ADMIN_CHAT_ID = 8023791486

# Channel Configuration
REQUIRED_CHANNELS = ["@weareinprime1", "@weareinprime"]

# Admin Control Flags
CHANNEL_MEMBERSHIP_REQUIRED = True  # Default: ON (require channel membership)
USERNAME_SEARCH_ENABLED = True  # Default: ON (allow username searches)

# Create bot instances with threading enabled for concurrent user handling
# Add skip_pending=True to avoid conflicts with previous instances
admin_bot = telebot.TeleBot(ADMIN_BOT_TOKEN, threaded=True, num_threads=4, skip_pending=True)
user_bot = telebot.TeleBot(USER_BOT_TOKEN, threaded=True, num_threads=4, skip_pending=True)

# Create Pyrogram clients
number_search_client = None
username_search_clients = []  # List of username search clients

# Initialize number search client (always available)
if NUMBER_SEARCH_PYROGRAM["api_id"] != 0:
    number_search_client = Client(
        NUMBER_SEARCH_PYROGRAM["session_name"],
        api_id=NUMBER_SEARCH_PYROGRAM["api_id"],
        api_hash=NUMBER_SEARCH_PYROGRAM["api_hash"],
        phone_number=NUMBER_SEARCH_PYROGRAM["phone"],
        workdir=".",
        no_updates=True  # Disable update handling to prevent loop conflicts
    )

# Initialize username search clients (if configured)
def init_username_search_clients():
    global username_search_clients
    username_search_clients = []

    for idx, config in enumerate(USERNAME_SEARCH_PYROGRAMS):
        if config["api_id"] != 0 and config["api_hash"]:
            try:
                client = Client(
                    config["session_name"],
                    api_id=config["api_id"],
                    api_hash=config["api_hash"],
                    phone_number=config["phone"],
                    workdir=".",
                    no_updates=True  # Disable update handling to prevent loop conflicts
                )
                username_search_clients.append(client)
            except Exception as e:
                print(f"Error initializing username search client {idx}: {e}")

# File paths
USERS_FILE = "users.json"
PROMO_CODES_FILE = "promo_codes.json"
PYROGRAM_CONFIG_FILE = "pyrogram_config.json"
SEARCHED_NO_DATA_FILE = "searched_no_data.json"
REFERRALS_FILE = "referrals.json"
INCOMPLETE_NUMBER_SEARCHES_FILE = "incomplete_number_searches.json"
PAYMENT_REVIEWS_FILE = "payment_reviews.json"  # Stores user_id -> review_message_id mapping
LOOKUPBLOCKED_FILE = "lookupblocked.json"
PRICES_FILE = "prices.json"

# Thread locks for concurrent access protection (using RLock for reentrancy)
users_lock = threading.RLock()
promo_codes_lock = threading.RLock()
searched_no_data_lock = threading.RLock()
referrals_lock = threading.RLock()
incomplete_number_lock = threading.RLock()
lookupblocked_lock = threading.RLock()
prices_lock = threading.RLock()

# Default prices
DEFAULT_PRICES = {
    "NUMBER_SEARCH_PRICE": 4,
    "USERNAME_SEARCH_PRICE": 21,
    "PROFILE_SEARCH_PRICE": 10
}

# Pricing variables (initialized with defaults, loaded from file later)
NUMBER_SEARCH_PRICE = DEFAULT_PRICES["NUMBER_SEARCH_PRICE"]
USERNAME_SEARCH_PRICE = DEFAULT_PRICES["USERNAME_SEARCH_PRICE"]
PROFILE_SEARCH_PRICE = DEFAULT_PRICES["PROFILE_SEARCH_PRICE"]

# Original prices for strikethrough logic
ORIGINAL_PRICES = {
    "NUMBER_SEARCH": 4,
    "USERNAME_SEARCH": 21,
    "PROFILE_SEARCH": 10
}

def load_json_safely(file_path, default_value=None):
    """Safely load JSON from a file, returning default_value if file is corrupted or empty"""
    if default_value is None:
        default_value = {}
    if not os.path.exists(file_path):
        return default_value
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Warning: Could not load {file_path}: {e}. Using default.")
        return default_value

def load_prices():
    global NUMBER_SEARCH_PRICE, USERNAME_SEARCH_PRICE, PROFILE_SEARCH_PRICE
    data = load_json_safely(PRICES_FILE, DEFAULT_PRICES)
    NUMBER_SEARCH_PRICE = data.get("NUMBER_SEARCH_PRICE", DEFAULT_PRICES["NUMBER_SEARCH_PRICE"])
    USERNAME_SEARCH_PRICE = data.get("USERNAME_SEARCH_PRICE", DEFAULT_PRICES["USERNAME_SEARCH_PRICE"])
    PROFILE_SEARCH_PRICE = data.get("PROFILE_SEARCH_PRICE", DEFAULT_PRICES["PROFILE_SEARCH_PRICE"])

def save_prices():
    data = {
        "NUMBER_SEARCH_PRICE": NUMBER_SEARCH_PRICE,
        "USERNAME_SEARCH_PRICE": USERNAME_SEARCH_PRICE,
        "PROFILE_SEARCH_PRICE": PROFILE_SEARCH_PRICE
    }
    with open(PRICES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_price_display(current_price, original_price):
    if current_price < original_price:
        # Using Telegram's HTML strikethrough tag <s>
        return f"<s>₹{int(original_price)}</s> ₹{int(current_price)} OFFER PRICE 🔥"
    else:
        return f"₹{int(current_price)}"

# Referral bonus amount
REFERRAL_BONUS = 4

# Save active index and limits to config
def save_active_pyrogram_index():
    data = {
        "active_index": ACTIVE_USERNAME_PYROGRAM_INDEX,
        "limits": USERNAME_PYROGRAM_LIMITS,
        "request_counts": USERNAME_PYROGRAM_REQUEST_COUNTS
    }
    with open(PYROGRAM_CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_active_pyrogram_index():
    global ACTIVE_USERNAME_PYROGRAM_INDEX, USERNAME_PYROGRAM_LIMITS, USERNAME_PYROGRAM_REQUEST_COUNTS
    data = load_json_safely(PYROGRAM_CONFIG_FILE, {"active_index": 0, "limits": {}, "request_counts": {}})
    if "active_index" in data:
        ACTIVE_USERNAME_PYROGRAM_INDEX = data["active_index"]
    if "limits" in data:
        # Convert string keys to int
        USERNAME_PYROGRAM_LIMITS = {int(k): v for k, v in data["limits"].items()}
    if "request_counts" in data:
        # Convert string keys to int
        USERNAME_PYROGRAM_REQUEST_COUNTS = {int(k): v for k, v in data["request_counts"].items()}

# Russian to English translation dictionary (for Profile Search)
RUSSIAN_TO_ENGLISH = {
    "Запрос": "Request",
    "Telegram ID": "Telegram ID",
    "История профиля": "Profile history",
    "Регистрация": "Registration",
    "~сентябрь": "~September",
    "~октябрь": "~October",
    "~ноябрь": "~November",
    "~декабрь": "~December",
    "~январь": "~January",
    "~февраль": "~February",
    "~март": "~March",
    "~апрель": "~April",
    "~май": "~May",
    "~июнь": "~June",
    "~июль": "~July",
    "~август": "~August",
    "Чаты": "Groups",
    "Нет сообщений": "No messages",
    "Всего": "Total",
    "страница": "page",
}

# Cache for search reports
cash_reports = {}

# User state tracking
user_states = {}

# Pending username searches (username -> {user_id, timestamp})
pending_username_searches = {}

# Track users in User ID search mode
user_id_search_mode = {}

# Track users in normal Username Search mode (for @Dfjyt_bot)
username_search_mode = {}

# Track users in Profile Search mode (for @pofliechecker17_bot)
profile_search_mode = {}

# Track users in Profile User ID Search mode
profile_userid_search_mode = {}

# Profile Search Pyrogram client (separate from main username search)
profile_search_client = None
_profile_search_loop = None
_profile_search_thread = None

# Main event loop reference for async operations
main_event_loop = None

# Profile search request queue
import queue
profile_search_queue = queue.Queue()
profile_search_results = {}  # {request_id: result}

# Promo codes storage
promo_codes = {}  # {code: {amount, max_uses, used_count, used_by: []}}

# Initialize files
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(PROMO_CODES_FILE):
        with open(PROMO_CODES_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(PYROGRAM_CONFIG_FILE):
        with open(PYROGRAM_CONFIG_FILE, 'w') as f:
            json.dump({"active_index": 0}, f)
    if not os.path.exists(SEARCHED_NO_DATA_FILE):
        with open(SEARCHED_NO_DATA_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(REFERRALS_FILE):
        with open(REFERRALS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(INCOMPLETE_NUMBER_SEARCHES_FILE):
        with open(INCOMPLETE_NUMBER_SEARCHES_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(PAYMENT_REVIEWS_FILE):
        with open(PAYMENT_REVIEWS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(LOOKUPBLOCKED_FILE):
        with open(LOOKUPBLOCKED_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(PRICES_FILE):
        save_prices()
    load_prices()
    load_active_pyrogram_index()
    init_username_search_clients()
    init_profile_search_client()

# Get or create dedicated event loop for profile search
def get_profile_search_loop():
    """Get or create dedicated event loop for profile search"""
    global _profile_search_loop, _profile_search_thread
    
    if _profile_search_loop is None:
        import threading
        
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        _profile_search_loop = asyncio.new_event_loop()
        _profile_search_thread = threading.Thread(target=start_loop, args=(_profile_search_loop,), daemon=True)
        _profile_search_thread.start()
    
    return _profile_search_loop

# Initialize profile search client
def init_profile_search_client():
    global profile_search_client
    if PROFILE_SEARCH_PYROGRAM["api_id"] != 0 and PROFILE_SEARCH_PYROGRAM["api_hash"] != "0":
        try:
            loop = get_profile_search_loop()
            # Create client on the dedicated loop
            future = asyncio.run_coroutine_threadsafe(
                _init_profile_search_async(),
                loop
            )
            profile_search_client = future.result(timeout=30)
            print(f"✅ Profile Search Pyrogram initialized")
        except Exception as e:
            print(f"⚠️ Profile Search Pyrogram init error: {e}")

# Async function to initialize profile search client
async def _init_profile_search_async():
    """Async initialization of profile search client"""
    global profile_search_client
    try:
        profile_search_client = Client(
            PROFILE_SEARCH_PYROGRAM["session_name"],
            api_id=PROFILE_SEARCH_PYROGRAM["api_id"],
            api_hash=PROFILE_SEARCH_PYROGRAM["api_hash"],
            phone_number=PROFILE_SEARCH_PYROGRAM["phone"],
            workdir=".",
            no_updates=True
        )
        return profile_search_client
    except Exception as e:
        print(f"⚠️ Profile Search Pyrogram async init error: {e}")
        return None

# Load data from files
def load_users():
    return load_json_safely(USERS_FILE, {})

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_promo_codes():
    return load_json_safely(PROMO_CODES_FILE, {})

def save_promo_codes(data):
    with open(PROMO_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_payment_reviews():
    return load_json_safely(PAYMENT_REVIEWS_FILE, {})

def save_payment_reviews(data):
    with open(PAYMENT_REVIEWS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_searched_no_data():
    return load_json_safely(SEARCHED_NO_DATA_FILE, {})

def save_searched_no_data(data):
    with open(SEARCHED_NO_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_to_searched_no_data(query, search_type):
    """Add username or user_id to searched no data list"""
    with searched_no_data_lock:
        data = load_searched_no_data()
        key = f"{search_type}_{query.lower()}"
        data[key] = {
            "query": query,
            "search_type": search_type,
            "timestamp": time.time()
        }
        save_searched_no_data(data)

def is_already_searched_no_data(query, search_type):
    """Check if username or user_id was already searched with no data"""
    with searched_no_data_lock:
        data = load_searched_no_data()
        # Normalize query: remove @ for username, keep as-is for user_id
        normalized_query = query.lstrip('@').lower() if search_type == "username" else query.lower()
        key = f"{search_type}_{normalized_query}"
        return key in data

def load_incomplete_number_searches():
    return load_json_safely(INCOMPLETE_NUMBER_SEARCHES_FILE, {})

def save_incomplete_number_searches(data):
    with open(INCOMPLETE_NUMBER_SEARCHES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_to_incomplete_numbers(number):
    """Add phone number to incomplete searches list"""
    with incomplete_number_lock:
        data = load_incomplete_number_searches()
        # Normalize number: remove + and spaces
        normalized_number = number.replace('+', '').replace(' ', '').strip()
        data[normalized_number] = {
            "number": number,
            "timestamp": time.time()
        }
        save_incomplete_number_searches(data)

def is_incomplete_number(number):
    """Check if number has incomplete data"""
    with incomplete_number_lock:
        data = load_incomplete_number_searches()
        # Normalize number: remove + and spaces
        normalized_number = number.replace('+', '').replace(' ', '').strip()
        return normalized_number in data

# Lookup block functions
def load_lookupblocked():
    return load_json_safely(LOOKUPBLOCKED_FILE, {})

def save_lookupblocked(data):
    with open(LOOKUPBLOCKED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_to_lookupblocked(query, lookup_type):
    """Add username or user_id to lookup blocked list"""
    with lookupblocked_lock:
        data = load_lookupblocked()
        # Normalize: remove @ for username, keep as-is for user_id
        normalized_query = query.lstrip('@').lower() if lookup_type == "username" else query.lower()
        key = f"{lookup_type}_{normalized_query}"
        data[key] = {
            "query": query,
            "lookup_type": lookup_type,
            "timestamp": time.time()
        }
        save_lookupblocked(data)

def is_lookup_blocked(query, lookup_type):
    """Check if username or user_id is blocked from lookup"""
    with lookupblocked_lock:
        data = load_lookupblocked()
        normalized_query = query.lstrip('@').lower() if lookup_type == "username" else query.lower()
        key = f"{lookup_type}_{normalized_query}"
        return key in data

def remove_from_lookupblocked(query, lookup_type):
    """Remove username or user_id from lookup blocked list"""
    with lookupblocked_lock:
        data = load_lookupblocked()
        normalized_query = query.lstrip('@').lower() if lookup_type == "username" else query.lower()
        key = f"{lookup_type}_{normalized_query}"
        if key in data:
            del data[key]
            save_lookupblocked(data)
            return True
        return False

# Referral system functions
def load_referrals():
    return load_json_safely(REFERRALS_FILE, {})

def save_referrals(data):
    with open(REFERRALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_referral_code(user_id):
    """Generate unique referral code in format REF123ABC"""
    import string
    import hashlib
    
    hash_input = f"{user_id}{time.time()}"
    hash_obj = hashlib.md5(hash_input.encode())
    hash_hex = hash_obj.hexdigest()[:6].upper()
    
    code = f"REF{hash_hex}"
    return code

def get_or_create_referral_code(user_id):
    """Get existing referral code or create new one"""
    with referrals_lock:
        referrals = load_referrals()
        user_id_str = str(user_id)
        
        if user_id_str not in referrals:
            referral_code = generate_referral_code(user_id)
            referrals[user_id_str] = {
                "referral_code": referral_code,
                "referred_by": None,
                "referrals": [],
                "total_earnings": 0,
                "first_recharge_done": False
            }
            save_referrals(referrals)
        
        return referrals[user_id_str]["referral_code"]

def set_referrer(user_id, referrer_code):
    """Set who referred this user"""
    with referrals_lock:
        referrals = load_referrals()
        user_id_str = str(user_id)
        
        if user_id_str not in referrals:
            own_code = generate_referral_code(user_id)
            referrals[user_id_str] = {
                "referral_code": own_code,
                "referred_by": None,
                "referrals": [],
                "total_earnings": 0,
                "first_recharge_done": False,
                "access_granted": False
            }
        
        if referrals[user_id_str]["referred_by"] is None:
            referrer_id = find_user_by_referral_code(referrer_code)
            if referrer_id and str(referrer_id) != user_id_str:
                referrals[user_id_str]["referred_by"] = referrer_code
                save_referrals(referrals)
                return True
        return False

def process_referral_on_access(user_id):
    """Process referral when user gains access to bot features"""
    with referrals_lock:
        referrals = load_referrals()
        user_id_str = str(user_id)
        
        if user_id_str not in referrals:
            return None
        
        # Check if already processed
        if referrals[user_id_str].get("access_granted", False):
            return None
        
        # Mark access as granted
        referrals[user_id_str]["access_granted"] = True
        
        referrer_code = referrals[user_id_str].get("referred_by")
        if not referrer_code:
            save_referrals(referrals)
            return None
        
        referrer_id = find_user_by_referral_code(referrer_code)
        if not referrer_id:
            save_referrals(referrals)
            return None
        
        if referrer_id not in referrals:
            save_referrals(referrals)
            return None
        
        # Add referral record
        referrals[referrer_id]["referrals"].append({
            "user_id": user_id_str,
            "timestamp": time.time(),
            "bonus": REFERRAL_BONUS
        })
        referrals[referrer_id]["total_earnings"] += REFERRAL_BONUS
        
        save_referrals(referrals)
        
        # Add bonus to referrer's balance
        with users_lock:
            users = load_users()
            if referrer_id in users:
                users[referrer_id]["balance"] = users[referrer_id].get("balance", 0) + REFERRAL_BONUS
                save_users(users)
        
        return referrer_id

def find_user_by_referral_code(code):
    """Find user ID by their referral code"""
    with referrals_lock:
        referrals = load_referrals()
        for user_id, data in referrals.items():
            if data.get("referral_code") == code:
                return user_id
        return None

def process_referral_bonus(user_id):
    """Process referral bonus when user completes first recharge"""
    with referrals_lock:
        referrals = load_referrals()
        user_id_str = str(user_id)
        
        if user_id_str not in referrals:
            return None
        
        if referrals[user_id_str].get("first_recharge_done", False):
            return None
        
        referrals[user_id_str]["first_recharge_done"] = True
        
        referrer_code = referrals[user_id_str].get("referred_by")
        if not referrer_code:
            save_referrals(referrals)
            return None
        
        referrer_id = find_user_by_referral_code(referrer_code)
        if not referrer_id:
            save_referrals(referrals)
            return None
        
        if referrer_id not in referrals:
            save_referrals(referrals)
            return None
        
        referrals[referrer_id]["referrals"].append({
            "user_id": user_id_str,
            "timestamp": time.time(),
            "bonus": REFERRAL_BONUS
        })
        referrals[referrer_id]["total_earnings"] += REFERRAL_BONUS
        
        save_referrals(referrals)
        
        with users_lock:
            users = load_users()
            if referrer_id in users:
                users[referrer_id]["balance"] = users[referrer_id].get("balance", 0) + REFERRAL_BONUS
                save_users(users)
        
        return referrer_id

def get_referral_stats(user_id):
    """Get referral statistics for a user"""
    with referrals_lock:
        referrals = load_referrals()
        user_id_str = str(user_id)
        
        if user_id_str not in referrals:
            return {
                "referral_code": get_or_create_referral_code(user_id),
                "total_referrals": 0,
                "total_earnings": 0,
                "recent_referrals": []
            }
        
        data = referrals[user_id_str]
        return {
            "referral_code": data["referral_code"],
            "total_referrals": len(data.get("referrals", [])),
            "total_earnings": data.get("total_earnings", 0),
            "recent_referrals": data.get("referrals", [])[-10:]
        }

def get_top_referrers(limit=10):
    """Get top referrers by earnings"""
    with referrals_lock:
        referrals = load_referrals()
        
        referrer_list = []
        for user_id, data in referrals.items():
            if data.get("total_earnings", 0) > 0:
                referrer_list.append({
                    "user_id": user_id,
                    "total_earnings": data["total_earnings"],
                    "total_referrals": len(data.get("referrals", []))
                })
        
        referrer_list.sort(key=lambda x: x["total_earnings"], reverse=True)
        return referrer_list[:limit]

def get_total_referral_stats():
    """Get overall referral statistics"""
    with referrals_lock:
        referrals = load_referrals()
        
        total_bonuses = 0
        total_referrals = 0
        total_users_with_referrals = 0
        
        for user_id, data in referrals.items():
            referral_count = len(data.get("referrals", []))
            if referral_count > 0:
                total_users_with_referrals += 1
                total_referrals += referral_count
                total_bonuses += data.get("total_earnings", 0)
        
        total_users = len(referrals)
        conversion_rate = (total_users_with_referrals / total_users * 100) if total_users > 0 else 0
        
        return {
            "total_bonuses": total_bonuses,
            "total_referrals": total_referrals,
            "conversion_rate": round(conversion_rate, 2)
        }

# Get or create user
def get_user(user_id, username=None, first_name=None):
    with users_lock:
        users = load_users()
        user_id_str = str(user_id)
        if user_id_str not in users:
            users[user_id_str] = {
                "balance": 0,
                "username": username if username else None,
                "first_name": first_name if first_name else None,
                "bonus_claimed": False
            }
            save_users(users)
        else:
            updated = False
            if username and users[user_id_str].get("username") != username:
                users[user_id_str]["username"] = username
                updated = True
            if first_name and users[user_id_str].get("first_name") != first_name:
                users[user_id_str]["first_name"] = first_name
                updated = True
            # Add bonus_claimed field if missing
            if "bonus_claimed" not in users[user_id_str]:
                users[user_id_str]["bonus_claimed"] = False
                updated = True
            if updated:
                save_users(users)
        return users[user_id_str]

def update_user_balance(user_id, amount):
    with users_lock:
        users = load_users()
        user_id_str = str(user_id)
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0}
        users[user_id_str]["balance"] = amount
        save_users(users)

def deduct_balance(user_id, amount):
    with users_lock:
        users = load_users()
        user_id_str = str(user_id)
        if user_id_str in users:
            users[user_id_str]["balance"] -= amount
            save_users(users)
            return True
        return False

# Check channel membership
def check_channel_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = user_bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# Check if channel membership is required and user is member
def require_channel_membership(message):
    """Check channel membership before allowing any action. Returns True if check passed, False if blocked."""
    if not CHANNEL_MEMBERSHIP_REQUIRED:
        return True  # Membership not required, allow action
    
    user_id = message.from_user.id
    
    if not check_channel_membership(user_id):
        markup = types.InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_membership"))

        user_bot.send_message(
            message.chat.id,
            "⚠️ **Channel Membership Required!** 🔒\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ **You must join our channels to use the bot!**\n\n"
            "📢 **Please join both channels below:**\n"
            "✅ Then click 'I Joined' to verify\n\n"
            "🎁 **Bonus:** Get FREE ₹5 after joining! 💎\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return False  # Block the action
    
    return True  # Allow the action

# Filter and format data - check for HiTeckGroop header, remove it, and extract records
def filter_response_data(raw_text):
    """Extract ALL records from bot response and convert to JSON array with English field names"""
    import re
    import json

    # ⚠️ Convert Pyrogram Message object to regular string to avoid UTF-16 encoding errors
    raw_text = str(raw_text)
    
    print(f"Raw text received: {raw_text[:500]}...")  # Debug log

    # ✅ CRITICAL VALIDATION: Check if response contains HiTeckGroop.in header
    hiteck_pattern = r"HiTeckGroop\.in.*?had nicknames and emails\."
    hiteck_match = re.search(hiteck_pattern, raw_text, re.IGNORECASE | re.DOTALL)
    
    if not hiteck_match:
        # ❌ No valid data source header found
        print("❌ HiTeckGroop.in header NOT found - Invalid data source")
        no_result_json = [{
            "status": "no_results_found",
            "message": "No valid data available for this number",
            "owned_and_developed_by": "@hackingteamx"
        }]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        result = f"```json\n{json_str}\n```"
        return result
    
    # ✅ Valid data source found - remove the header and process remaining data
    print("✅ HiTeckGroop.in header FOUND - Valid data source")
    
    # Remove the entire HiTeckGroop header block
    cleaned_text = raw_text[:hiteck_match.start()] + raw_text[hiteck_match.end():]
    print(f"🔪 Removed HiTeckGroop header - Processing remaining data")
    print(f"Remaining text: {cleaned_text[:500]}...")

    # Remove all emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

    clean_text = emoji_pattern.sub('', cleaned_text)

    # Remove bot usernames
    bot_patterns = [
        r'@\w*[Bb][Oo][Tt]\w*',
        r'@breacha_bot',
        r'@zervierbot',
        r'@jsjwhejbbwbeb_bot',
    ]

    for pattern in bot_patterns:
        clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)

    # Split text into paragraphs (records separated by blank lines)
    paragraphs = clean_text.split('\n\n')

    all_records = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Check if this paragraph has actual data (contains field:value pairs)
        if ":" not in paragraph:
            continue

        lines = paragraph.split('\n')
        record_fields = []
        has_data = False

        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue

            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            key = parts[0].strip()
            value = parts[1].strip()

            if not key or not value:
                continue

            # Translate Russian field names to English
            english_key = key
            for russian_key, english_translation in FIELD_TRANSLATIONS.items():
                if russian_key.lower() in key.lower():
                    english_key = english_translation
                    break

            # Add each field as a separate object with English key names
            record_fields.append({english_key: value})
            has_data = True

        # Only add record if it has actual data
        if has_data and record_fields:
            all_records.append(record_fields)

    # If no records found after removing header, return no results
    if not all_records:
        print("⚠️ HiTeckGroop header found but NO data records after processing")
        no_result_json = [{
            "status": "no_results_found",
            "message": "No data available for this number",
            "owned_and_developed_by": "@hackingteamx"
        }]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        result = f"```json\n{json_str}\n```"
        print("No data found - returning no results JSON")
        return result

    # ✅ Return as JSON array of arrays
    json_str = json.dumps(all_records, indent=2, ensure_ascii=False)
    result = f"```json\n{json_str}\n```"
    print(f"✅ Found {len(all_records)} records - returning formatted JSON")
    return result

# Global event loop for pyrogram
_pyrogram_loop = None
_pyrogram_thread = None

def get_pyrogram_loop():
    """Get or create dedicated event loop for pyrogram"""
    global _pyrogram_loop, _pyrogram_thread

    if _pyrogram_loop is None:
        import threading

        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        _pyrogram_loop = asyncio.new_event_loop()
        _pyrogram_thread = threading.Thread(target=start_loop, args=(_pyrogram_loop,), daemon=True)
        _pyrogram_thread.start()

    return _pyrogram_loop

# Extract Telegram data from bot response
def extract_telegram_data(raw_text):
    """Extract Telegram phone number from bot response - supports multiple formats"""
    import re

    print(f"DEBUG: Extracting phone from text: {raw_text[:500]}")

    # Try multiple patterns to find phone number (order matters - most specific first)
    patterns = [
        r'📞\s*[Тт]елефон:\s*(\d{10,15})',          # 📞 Телефон: pattern (exact format from bot)
        r'📞\s*[Тт]елефон\s*[:\s]+(\d{10,15})',     # 📞 Телефон: pattern with flexible spacing
        r'[Тт]елефон:\s*(\d{10,15})',               # Телефон: pattern (exact)
        r'[Тт]елефон\s*[:\s]+(\d{10,15})',          # Телефон: pattern with spacing
        r'[Pp]hone\s*[:\s]+(\+?\d{10,15})',         # Phone: pattern
        r'💬\s*ID:\s*\d+\s+📞\s*[Тт]елефон:\s*(\d{10,15})',  # Full Russian format
        r'ID:\s*\d+.*?[Тт]елефон:\s*(\d{10,15})',   # ID followed by Телефон
        r'(\d{11,12})\s*(?:\n|$)',                   # 11-12 digit number at end of line
        r'(?:^|\n)(\d{11,12})(?:\s|\n)',             # 11-12 digit number at start of line
        r'(?:number|номер).*?(\+?\d{10,15})',       # number/номер followed by digits
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            phone_number = match.group(1).replace('+', '').strip()
            print(f"DEBUG: Found phone number with pattern '{pattern}': {phone_number}")

            # Validate it's a proper phone number (not just any 12 digits)
            if len(phone_number) >= 10 and phone_number.isdigit():
                # Format as +XXXXXXXXXXXX
                if len(phone_number) == 12 and phone_number.startswith('91'):
                    result = '+' + phone_number
                elif len(phone_number) == 10:
                    result = '+91' + phone_number
                elif len(phone_number) == 11 and phone_number.startswith('91'):
                    result = '+' + phone_number
                elif len(phone_number) == 12:
                    # Assume it's already complete with country code
                    result = '+' + phone_number
                else:
                    result = '+' + phone_number
                
                print(f"DEBUG: Formatted as: {result}")
                return result

    print("DEBUG: No phone number found in response")
    return None

# Field name translation mapping (Russian to English)
FIELD_TRANSLATIONS = {
    'Имя фамилия': 'Full Name',
    'Имя': 'Full Name',
    'фамилия': 'Full Name',
    'Имя отца': "Father's Name",
    'отца': "Father's Name",
    'Альтернативный номер': 'Alternative Numbers',
    'Альтернативный': 'Alternative Numbers',
    'номер': 'Alternative Numbers',
    'Домашний адрес': 'Home Address',
    'адрес': 'Home Address',
    'Документ номер': 'Document Number (Aadhaar)',
    'Документ': 'Document Number (Aadhaar)',
    'Регион': 'Region',
    'Region': 'Region'
}

# Generate report from Target Bot using Pyrogram (Automated)
async def generate_report_from_bot(query, query_id, is_username_search=False):
    global cash_reports
    try:
        # Select appropriate client based on search type
        if is_username_search:
            if not username_search_clients or ACTIVE_USERNAME_PYROGRAM_INDEX >= len(username_search_clients):
                return [json.dumps([{
                    "status": "error",
                    "message": "Username search Pyrogram not configured. Contact admin.",
                    "owned_and_developed_by": "@hackingteamx"
                }], indent=2)]
            client = username_search_clients[ACTIVE_USERNAME_PYROGRAM_INDEX]
            target_bot = USERNAME_SEARCH_PYROGRAMS[ACTIVE_USERNAME_PYROGRAM_INDEX].get("target_bot", "")
            if not target_bot:
                return [json.dumps([{
                    "status": "error",
                    "message": "Target bot not configured. Contact admin.",
                    "owned_and_developed_by": "@hackingteamx"
                }], indent=2)]
        else:
            if not number_search_client:
                return [json.dumps([{
                    "status": "error",
                    "message": "Number search Pyrogram not configured",
                    "owned_and_developed_by": "@hackingteamx"
                }], indent=2)]
            client = number_search_client
            target_bot = NUMBER_SEARCH_BOT_USERNAME  # Configurable bot username

        # Check if client is connected
        if not client.is_connected:
            await client.start()

        # Convert @username to t.me/username format for username searches
        if is_username_search and query.startswith('@'):
            converted_query = query.replace('@', 't.me/', 1)
            print(f"🔄 Converting username: {query} → {converted_query}")
        else:
            converted_query = query

        # Record start time BEFORE sending message
        start_time = time.time()
        
        # Send message to target bot with parse_mode=None to handle underscores
        await client.send_message(target_bot, converted_query, parse_mode=None)
        print(f"📤 Query sent to {target_bot} at timestamp: {start_time}")

        # Response ka wait karo
        response_text = ""
        max_wait = 90

        # For username search, wait for response without clicking buttons
        if is_username_search:
            # Wait 7 seconds before starting to check for response
            print(f"⏳ Waiting 7 seconds for bot response...")
            await asyncio.sleep(7)
            
            attempts = 0
            max_attempts = 40  # Poll for up to 80 seconds after initial wait (40 attempts * 2 seconds)
            
            print(f"🔍 Starting to poll for response...")

            response_found = False  # Flag to track if response found
            
            while attempts < max_attempts and (time.time() - start_time) < max_wait:
                async for msg in client.get_chat_history(target_bot, limit=50):
                    if msg.from_user and msg.from_user.username == target_bot.replace("@", ""):
                        msg_timestamp = msg.date.timestamp()
                        time_diff = msg_timestamp - start_time
                        
                        # More permissive time window: allow messages from 60 seconds BEFORE to 120 seconds AFTER
                        if -60 <= time_diff <= 120:
                            msg_text = msg.text or msg.caption or ""
                            
                            # 🔴 FETCH ANY MESSAGE - print to console regardless of content
                            if msg_text and len(msg_text) > 10:
                                print(f"\n{'='*60}")
                                print(f"📩 BOT RESPONSE RECEIVED (time_diff: {time_diff:.2f}s)")
                                print(f"{'='*60}")
                                print(f"{msg_text}")
                                print(f"{'='*60}\n")
                                
                                # 🔴 DON'T SKIP ANYTHING - Check directly for phone term
                                # Look for the phone number term: 📞 Телефон
                                if '📞 Телефон' in msg_text or 'Телефон:' in msg_text:
                                    response_text = msg_text
                                    print(f"✅ Valid response with phone number detected!")
                                    response_found = True
                                    break
                                else:
                                    # No phone term found - this is the FINAL response (STOP POLLING INSTANTLY)
                                    print(f"❌ No phone number found in response - treating as NO DATA")
                                    print(f"🛑 STOPPING POLLING - Sending instant NO DATA response")
                                    response_text = None  # Set to None to indicate no data found
                                    response_found = True
                                    break

                # 🔴 CRITICAL: Exit outer loop immediately if response found (with or without phone number)
                if response_found:
                    break

                await asyncio.sleep(2)  # Check every 2 seconds
                attempts += 1
                
                # Only print every 3rd attempt to reduce console spam
                if attempts % 3 == 0:
                    print(f"⏳ Polling... attempt {attempts}/{max_attempts} ({int(time.time() - start_time)}s elapsed)")
        else:
            # For phone number search
            await asyncio.sleep(5)
            attempts = 0
            max_attempts = 30

            while attempts < max_attempts and (time.time() - start_time) < max_wait:
                async for message in client.get_chat_history(target_bot, limit=10):
                    if message.from_user and message.from_user.username == target_bot.replace("@", ""):
                        if message.date.timestamp() > (start_time - 2):
                            msg_text = message.text or message.caption or ""
                            if msg_text and len(msg_text) > 50:
                                response_text = msg_text
                                break

                if response_text:
                    break

                await asyncio.sleep(3)
                attempts += 1

        if not response_text:
            print(f"No response received from bot after {max_wait} seconds")
            return None

        # For username search, extract phone number directly
        if is_username_search:
            print(f"\n{'='*60}")
            print(f"USERNAME SEARCH RESPONSE PROCESSING")
            print(f"{'='*60}")
            print(f"Full response text:\n{response_text}")
            print(f"{'='*60}\n")

            phone_number = extract_telegram_data(response_text)

            if phone_number:
                print(f"✅ SUCCESS: Phone number extracted: {phone_number}")
                return [phone_number]
            else:
                print("❌ FAILED: No phone number found in response")
                print(f"Response was:\n{response_text}")
                return None

        # For number search, filter the response data
        filtered_text = filter_response_data(response_text)

        # Response ko format karo
        cash_reports[str(query_id)] = []

        # Check if no results
        if "no_results_found" in filtered_text.lower():
            cash_reports[str(query_id)].append(filtered_text) # filter_response_data already returns JSON
            return cash_reports[str(query_id)]

        # Split response into chunks if needed
        if len(filtered_text) > 3500:
            chunks = [filtered_text[i:i+3500] for i in range(0, len(filtered_text), 3500)]
            for chunk in chunks:
                cash_reports[str(query_id)].append(chunk)
        else:
            cash_reports[str(query_id)].append(filtered_text)

        return cash_reports[str(query_id)]

    except FloodWait as e:
        print(f"FloodWait: Wait for {e.value} seconds")
        await asyncio.sleep(e.value)
        return await generate_report_from_bot(query, query_id)
    except Exception as e:
        print(f"Pyrogram Error: {e}")
        import traceback
        traceback.print_exc()
        # Return JSON format for error
        no_result_json = [{
            "status": "error",
            "message": f"An internal error occurred: {str(e)}",
            "number": query,
            "owned_and_developed_by": "@hackingteamx"
        }]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        return f"```json\n{json_str}\n```"

# Sync wrapper for generate_report
def generate_report(query, query_id, is_username_search=False):
    """Synchronous wrapper to call async generate_report_from_bot"""
    try:
        loop = get_pyrogram_loop()
        future = asyncio.run_coroutine_threadsafe(
            generate_report_from_bot(query, query_id, is_username_search),
            loop
        )
        return future.result(timeout=100)
    except Exception as e:
        print(f"Error in generate_report wrapper: {e}")
        import traceback
        traceback.print_exc()
        # Return JSON format for error
        no_result_json = [{
            "status": "error",
            "message": f"An internal error occurred during report generation: {str(e)}",
            "number": query,
            "owned_and_developed_by": "@hackingteamx"
        }]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        return [f"```json\n{json_str}\n```"] # Return as list to match expected format

# Create inline keyboard for pagination
def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()
    if count_page == 0: # Handle case with no pages
        return markup

    # Ensure page_id is within bounds
    if page_id < 0:
        page_id = count_page - 1
    elif page_id >= count_page:
        page_id = 0 # Wrap around if exceeding max page

    if count_page == 1:
        return markup # No pagination needed for a single page

    markup.row_width = 3
    markup.add(
        InlineKeyboardButton(text="<<", callback_data=f"/page {query_id} {page_id-1}"),
        InlineKeyboardButton(text=f"{page_id+1}/{count_page}", callback_data="page_list"), # This callback might not be needed if not used elsewhere
        InlineKeyboardButton(text=">>", callback_data=f"/page {query_id} {page_id+1}")
    )
    return markup

# Format any number to +91XXXXXXXXXX
def format_indian_number(number):
    """Convert any number format to +91XXXXXXXXXX"""
    # Remove all spaces and special characters except +
    cleaned = ''.join(c for c in number if c.isdigit() or c == '+')

    # Remove leading + if exists
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]

    # Remove leading 91 if exists
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]

    # Now should have 10 digits
    if len(cleaned) == 10 and cleaned.isdigit():
        return f"+91{cleaned}"

    return None

# Validate Indian phone number format
def validate_indian_number(number):
    formatted = format_indian_number(number)
    return formatted is not None

# Check if input is username (starts with @)
def is_username(text):
    cleaned = text.strip()
    if not cleaned.startswith("@"):
        return False
    # Remove @ and check if rest is valid username format
    username_part = cleaned[1:]
    if not username_part:
        return False
    # Accept any username that starts with @ and has at least 1 character after it
    # This allows for flexible username matching
    return len(username_part) >= 1 and len(username_part) <= 32

# Check if input is user ID (only digits)
def is_user_id(text):
    cleaned = text.strip()
    return cleaned.isdigit() and len(cleaned) >= 5

# Check if input is phone number (starts with +91)
def is_phone_number(text):
    return validate_indian_number(text.strip())

# Send JSON results with FAST typing effect (5x speed, no hanging) - BIG TEXT FORMAT
def send_with_typing_effect(chat_id, json_text, reply_markup=None):
    """Send message with ultra-fast typing animation - big text format for better visibility"""
    try:
        # Extract JSON content from markdown code block
        if json_text.startswith("```json\n"):
            json_content = json_text[8:-4]  # Remove ```json\n and \n```
        elif json_text.startswith("```\n"):
            json_content = json_text[4:-4]  # Remove ```\n and \n```
        else:
            json_content = json_text
        
        total_len = len(json_content)
        
        # Start with empty code box with cursor using HTML format (better font rendering)
        typing_msg = user_bot.send_message(chat_id, "<pre>▌</pre>", parse_mode="HTML")
        
        batch_size = 80  # LARGE batch - 80 chars per update (5x faster)
        delay = 0.001   # VERY FAST delay (almost instant between updates)
        
        # Type characters progressively inside the code box with BIG FONT
        for i in range(0, total_len, batch_size):
            current_content = json_content[:i + batch_size]
            # Add cursor at end while typing (escaped for HTML)
            if i + batch_size < total_len:
                # HTML format with larger font size for better visibility
                current_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{current_content}▌</code></pre>"
            else:
                current_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{current_content}</code></pre>"
            
            try:
                user_bot.edit_message_text(
                    current_text,
                    chat_id,
                    typing_msg.message_id,
                    parse_mode="HTML"
                )
                time.sleep(delay)  # Super fast - no hanging
            except Exception as e:
                error_str = str(e).lower()
                if "message is not modified" in error_str:
                    continue
                elif "flood" in error_str or "too many requests" in error_str:
                    # If rate limited, just send the rest directly
                    try:
                        final_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{json_content}</code></pre>"
                        user_bot.edit_message_text(
                            final_text,
                            chat_id,
                            typing_msg.message_id,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    except:
                        pass
                    return typing_msg
                else:
                    # On any other error, complete typing instantly
                    try:
                        final_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{json_content}</code></pre>"
                        user_bot.edit_message_text(
                            final_text,
                            chat_id,
                            typing_msg.message_id,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    except:
                        pass
                    return typing_msg
        
        # Final message with complete JSON in HTML format (bigger text)
        try:
            final_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{json_content}</code></pre>"
            user_bot.edit_message_text(
                final_text,
                chat_id,
                typing_msg.message_id,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                print(f"Final edit error: {e}")
                
        return typing_msg
    except Exception as e:
        print(f"Typing effect error: {e}")
        try:
            final_text = f"<pre><code style='font-size: 16px; line-height: 1.5;'>{json_content}</code></pre>"
            if reply_markup:
                return user_bot.send_message(chat_id, final_text, parse_mode="HTML", reply_markup=reply_markup)
            else:
                return user_bot.send_message(chat_id, final_text, parse_mode="HTML")
        except:
            if reply_markup:
                return user_bot.send_message(chat_id, json_text, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                return user_bot.send_message(chat_id, json_text, parse_mode="Markdown")

# Extract username without @ symbol for storage
def get_username_key(username_with_at):
    """Remove @ and convert to lowercase for consistent storage"""
    return username_with_at.lstrip('@').lower()

# Show loading animation
def show_loading_animation(chat_id, message_text):
    progress_msg = user_bot.send_message(chat_id, f"🔄 {message_text}\n\n▱▱▱▱▱▱▱▱▱▱ 0%")

    stages = [
        ("▰▱▱▱▱▱▱▱▱▱", "10%"),
        ("▰▰▱▱▱▱▱▱▱▱", "20%"),
        ("▰▰▰▱▱▱▱▱▱▱", "30%"),
        ("▰▰▰▰▱▱▱▱▱▱", "40%"),
        ("▰▰▰▰▰▱▱▱▱▱", "50%"),
        ("▰▰▰▰▰▰▱▱▱▱", "60%"),
        ("▰▰▰▰▰▰▰▱▱▱", "70%"),
        ("▰▰▰▰▰▰▰▰▱▱", "80%"),
        ("▰▰▰▰▰▰▰▰▰▱", "90%"),
        ("▰▰▰▰▰▰▰▰▰▰", "100%")
    ]

    for bar, percent in stages:
        try:
            user_bot.edit_message_text(
                f"🔄 {message_text}\n\n{bar} {percent}",
                chat_id,
                progress_msg.message_id
            )
            time.sleep(0.3)
        except:
            pass

    return progress_msg

# ============= USER BOT =============

@user_bot.message_handler(commands=['start'])
def user_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Check for referral code in /start command
    referral_code = None
    if len(message.text.split()) > 1:
        potential_code = message.text.split()[1]
        if potential_code.startswith("REF"):
            referral_code = potential_code

    # Check if user is new (doesn't exist in database) and create user atomically
    with users_lock:
        users = load_users()
        is_new_user = str(user_id) not in users
        # Save user info within same lock to prevent race condition
        get_user(user_id, username, first_name)
    
    # Initialize referral code for this user and process referrer if applicable
    get_or_create_referral_code(user_id)
    
    # If there's a referral code and user is new, set the referrer
    if is_new_user and referral_code:
        referrer_set = set_referrer(user_id, referral_code)
        if referrer_set:
            try:
                # Notify new user
                user_bot.send_message(
                    message.chat.id,
                    "🎉 **Welcome!** You've been referred by a friend!\n\n"
                    "💰 Your friend will get **₹4 bonus** when you gain access to the bot!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
                time.sleep(1)
            except Exception as e:
                print(f"Error sending referral welcome: {e}")

    # Check channel membership only if CHANNEL_MEMBERSHIP_REQUIRED is True
    if CHANNEL_MEMBERSHIP_REQUIRED and not check_channel_membership(user_id):
        markup = types.InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_membership"))

        user_bot.send_message(
            message.chat.id,
            "╔═══════════════════════════╗\n"
            "║  **MEMBERSHIP REQUIRED** 🔒  ║\n"
            "╚═══════════════════════════╝\n\n"
            "**To access premium services:**\n\n"
            "📢 **Step 1:** Join both channels below\n"
            "✅ **Step 2:** Click 'I Joined' to verify\n\n"
            "**🔐 Why join?**\n"
            "├─ 📰 Get latest updates\n"
            "├─ 🎁 Get instant FREE ₹5 bonus after joining!\n"
            "├─ 🎁 Exclusive offers\n"
            "└─ ⚡ Priority support\n\n"
            "╔═══════════════════════════╗\n"
            "║    👇 **JOIN NOW** 👇    ║\n"
            "╚═══════════════════════════╝",
            reply_markup=markup,
            parse_mode="Markdown"
        )

        # Send voice message after channel join prompt
        try:
            voice_file = open('attached_assets/1Justafterchannellink_1762169791968.mp3', 'rb')
            user_bot.send_voice(message.chat.id, voice_file)
            voice_file.close()
        except Exception as e:
            print(f"Error sending voice: {e}")
        return
    
    # If channel membership not required or user is already member, grant access and process referral
    if not CHANNEL_MEMBERSHIP_REQUIRED or check_channel_membership(user_id):
        # Give automatic 5 RS bonus to new users after joining channel
        if is_new_user:
            user = get_user(user_id)
            new_balance = user['balance'] + 5
            update_user_balance(user_id, new_balance)
            
            # Mark bonus as claimed
            with users_lock:
                users = load_users()
                users[str(user_id)]["bonus_claimed"] = True
                save_users(users)
        
        # Process referral since user has direct access
        if is_new_user and referral_code:
            referrer_id = process_referral_on_access(user_id)
            if referrer_id:
                try:
                    referrer_user = get_user(int(referrer_id))
                    new_user_name = first_name if first_name else "A new user"
                    user_bot.send_message(
                        int(referrer_id),
                        f"🎉 **Referral Successful!** 🎊\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 **{new_user_name}** just gained access to the bot using your referral link!\n\n"
                        f"💰 **You earned ₹{REFERRAL_BONUS}!**\n"
                        f"💵 **New Balance:** ₹{referrer_user.get('balance', 0)} 🚀\n\n"
                        f"🔥 **Keep sharing to earn more!** 📤\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Error notifying referrer: {e}")

    # Show loading animation
    loading_msg = user_bot.send_message(
        message.chat.id,
        "🔄 *Initializing your account...*\n\n▱▱▱▱▱▱▱▱▱▱ 0%",
        parse_mode="Markdown"
    )

    time.sleep(0.5)
    user_bot.edit_message_text("🔄 *Setting up interface...*\n\n▰▰▰▰▰▱▱▱▱▱ 50%", message.chat.id, loading_msg.message_id, parse_mode="Markdown")
    time.sleep(0.5)
    user_bot.edit_message_text("✅ *Account Ready!* 🎉\n\n▰▰▰▰▰▰▰▰▰▰ 100%", message.chat.id, loading_msg.message_id, parse_mode="Markdown")
    time.sleep(0.5)

    user_bot.delete_message(message.chat.id, loading_msg.message_id)
    show_main_menu(message.chat.id)

def reset_user_to_home(user_id, chat_id):
    """Clear all search modes and return user to home menu"""
    # Remove user from all search modes
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    if user_id in username_search_mode:
        del username_search_mode[user_id]
    if user_id in user_id_search_mode:
        del user_id_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    
    # Show home menu
    show_main_menu(chat_id)

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📞 Search Number")
    btn2 = types.KeyboardButton("👤 Search Username")
    btn_profile = types.KeyboardButton("👤 PROFILE LOOKUP")
    btn3 = types.KeyboardButton("💰 Check Balance")
    btn4 = types.KeyboardButton("➕ Add Balance")
    btn6 = types.KeyboardButton("🎟️ Claim Promo Code")
    btn7 = types.KeyboardButton("🚀 Buy API")
    btn8 = types.KeyboardButton("👨‍💻 Support")
    btn9 = types.KeyboardButton("🎁 Refer and Earn")
    markup.add(btn1, btn2, btn_profile, btn3, btn4, btn6, btn9, btn7, btn8)

    user_bot.send_message(
        chat_id,
        "🔍 PREMIUM SEARCH BOT 💎\n\n"
        f"📱 Number Search ({get_price_display(NUMBER_SEARCH_PRICE, ORIGINAL_PRICES['NUMBER_SEARCH'])}): Get full name, father's name, alternative numbers, home address, document number (Aadhaar), and region\n\n"
        f"👤 Username Search ({get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH'])}): Get phone number from Telegram username\n\n"
        f"👤 Profile Lookup ({get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}): Get complete profile data, all groups & channels, message history (HTML file)\n\n"
        f"💰 Current Pricing:\n"
        f"├─ 📞 Phone Search: {get_price_display(NUMBER_SEARCH_PRICE, ORIGINAL_PRICES['NUMBER_SEARCH'])}\n"
        f"├─ 👤 Username Search: {get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH'])}\n"
        f"└─ 👤 Profile Lookup: {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}",
        reply_markup=markup,
        parse_mode="HTML"
    )

@user_bot.callback_query_handler(func=lambda call: call.data == "sel_username_prompt")
def handle_sel_username_prompt(call):
    user_id = call.from_user.id
    username_search_mode[user_id] = True
    user_bot.delete_message(call.message.chat.id, call.message.message_id)
    search_username_prompt(call.message)

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("sel_profile_"))
def handle_sel_profile_prompt(call):
    user_id = call.from_user.id
    username = call.data.replace("sel_profile_", "")
    
    # Check balance for profile search
    user = get_user(user_id)
    if user['balance'] < PROFILE_SEARCH_PRICE:
        user_bot.answer_callback_query(call.id, f"❌ Insufficient Balance! Need ₹{PROFILE_SEARCH_PRICE}", show_alert=True)
        return
        
    user_bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Create a dummy message object for perform_search
    class DummyMessage:
        def __init__(self, chat_id, from_user_id, text):
            self.chat = type('obj', (object,), {'id': chat_id})
            self.from_user = type('obj', (object,), {'id': from_user_id})
            self.text = text
            
    dummy_msg = DummyMessage(call.message.chat.id, user_id, f"@{username}")
    
    # Activate profile search mode for this user so perform_search routes correctly
    profile_search_mode[user_id] = True
    perform_search(dummy_msg, f"@{username}", search_type="profile_lookup")

@user_bot.callback_query_handler(func=lambda call: call.data == "switch_to_userid")
def callback_switch_to_userid(call):
    user_id = call.from_user.id
    # Clear all search modes and set user ID search mode
    if user_id in username_search_mode:
        del username_search_mode[user_id]
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    user_id_search_mode[user_id] = True
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("👤 Search Username"), types.KeyboardButton("🏠 Main Menu"))
    
    user_bot.delete_message(call.message.chat.id, call.message.message_id)
    user_bot.send_message(
        call.message.chat.id,
        "🆔 <b>Telegram User ID Search</b> 🔍\n\n"
        "📊 You'll get:\n"
        "✅ Phone number linked to account\n"
        "✅ Deep search across billions of records\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>Cost:</b> " + get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH']) + " ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 <b>Enter User ID:</b>\n"
        "   • Format: <code>853269852</code>\n"
        "   • Only numeric digits\n\n"
        "⏳ <b>Search takes 10-20 seconds</b> ⚡",
        reply_markup=markup,
        parse_mode="HTML"
    )

@user_bot.callback_query_handler(func=lambda call: call.data == "switch_to_profile_userid")
def callback_switch_to_profile_userid(call):
    user_id = call.from_user.id
    # Clear all search modes and set profile user ID search mode
    if user_id in username_search_mode:
        del username_search_mode[user_id]
    if user_id in user_id_search_mode:
        del user_id_search_mode[user_id]
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    profile_userid_search_mode[user_id] = True
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("👤 PROFILE LOOKUP"), types.KeyboardButton("🏠 Main Menu"))
    
    user_bot.delete_message(call.message.chat.id, call.message.message_id)
    user_bot.send_message(
        call.message.chat.id,
        "🆔 <b>LOOKUP BY USER ID</b> 🆔\n\n"
        "📊 You'll get:\n"
        "✅ Profile info, bio, status\n"
        "✅ All groups & channels\n"
        "✅ Message history (HTML file)\n\n"
        f"💰 <b>Cost:</b> {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n\n"
        "🔢 <b>Enter Telegram User ID:</b>\n"
        "   Example: <code>8457239528</code>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("enter_utr_"))
def handle_utr_button(call):
    amount = float(call.data.replace("enter_utr_", ""))
    user_id = call.from_user.id

    user_states[user_id] = {"amount": amount, "waiting_utr": True, "utr_attempts": 0}

    user_bot.answer_callback_query(call.id, "✅ Please send your 12-digit UTR number")

    user_bot.delete_message(call.message.chat.id, call.message.message_id)
    
    user_bot.send_message(
        call.message.chat.id,
        "📝 **Send your 12-digit UTR number** 💳",
        parse_mode="Markdown"
    )

@user_bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def verify_membership(call):
    user_id = call.from_user.id
    username = call.from_user.username
    first_name = call.from_user.first_name

    get_user(user_id, username, first_name)

    user_bot.edit_message_text(
        "🔄 **Verifying membership...** 🔍\n\n▰▰▰▰▰▱▱▱▱▱ 50%",
        call.message.chat.id,
        call.message.message_id
    )
    time.sleep(1)

    if check_channel_membership(user_id):
        user_bot.edit_message_text(
            "✅ *Verification Successful!* 🎉\n\n▰▰▰▰▰▰▰▰▰▰ 100%",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        time.sleep(1)
        user_bot.delete_message(call.message.chat.id, call.message.message_id)

        # Get user and check if bonus already claimed
        user = get_user(user_id)
        bonus_message = ""
        
        # Give automatic 5 RS bonus to new users only (one-time)
        if not user.get("bonus_claimed", False):
            new_balance = user['balance'] + 5
            update_user_balance(user_id, new_balance)
            
            # Mark bonus as claimed
            with users_lock:
                users = load_users()
                users[str(user_id)]["bonus_claimed"] = True
                save_users(users)
            
            bonus_message = (
                "🎉 *INSTANT BONUS RECEIVED!* 🎊\n\n"
                "✅ *You received ₹5 free bonus!* 💎\n"
                "💵 *New Balance:* ₹" + str(new_balance) + " 🚀\n\n"
                "⚠️ *This is a ONE-TIME ONLY bonus for new users!*\n\n"
            )
        else:
            bonus_message = (
                "✅ *You already claimed your bonus!* 💎\n\n"
            )

        # Process referral now that user has gained access
        referrer_id = process_referral_on_access(user_id)
        if referrer_id:
            try:
                referrer_user = get_user(int(referrer_id))
                new_user_name = first_name if first_name else "A new user"
                user_bot.send_message(
                    int(referrer_id),
                    f"🎉 *Referral Successful!* 🎊\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 *{new_user_name}* just gained access to the bot using your referral link!\n\n"
                    f"💰 *You earned ₹{REFERRAL_BONUS}!*\n"
                    f"💵 *New Balance:* ₹{referrer_user.get('balance', 0)} 🚀\n\n"
                    f"🔥 *Keep sharing to earn more!* 📤\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Error notifying referrer: {e}")

        # Send bonus info message with bonus status
        user_bot.send_message(
            call.message.chat.id,
            "🎉 *Welcome!* You're all set! 🚀\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            + bonus_message +
            "🚀 *Start searching now!* You're ready to go! ⚡\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )

        show_main_menu(call.message.chat.id)

        # Send voice message AFTER all text messages
        try:
            voice_file = open('attached_assets/2afterjoiningchannel_1762169792077.mp3', 'rb')
            user_bot.send_voice(call.message.chat.id, voice_file)
            voice_file.close()
        except Exception as e:
            print(f"Error sending voice: {e}")
    else:
        user_bot.answer_callback_query(call.id, "❌ You must join all channels first! 🔒", show_alert=True)

        markup = types.InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_membership"))

        user_bot.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║  *MEMBERSHIP REQUIRED* 🔒  ║\n"
            "╚═══════════════════════════╝\n\n"
            "*To access premium services:*\n\n"
            "📢 *Step 1:* Join both channels below\n"
            "✅ *Step 2:* Click 'I Joined' to verify\n\n"
            "*🔐 Why join?*\n"
            "├─ 📰 Get latest updates\n"
            "├─ 🎁 Exclusive offers\n"
            "└─ ⚡ Priority support\n\n"
            "╔═══════════════════════════╗\n"
            "║    👇 *JOIN NOW* 👇    ║\n"
            "╚═══════════════════════════╝",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

@user_bot.message_handler(func=lambda message: message.text == "🚀 Buy API")
def buy_unlimited_api(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👤 Contact Personal", url="https://t.me/hackingteamx"))
    markup.add(types.InlineKeyboardButton("🤖 Contact Bot", url="https://t.me/Hackingteamx_bot"))

    user_bot.send_message(
        message.chat.id,
        "╔═══════════════════════════════╗\n"
        "║   *UNLIMITED SEARCH API* 🚀   ║\n"
        "╚═══════════════════════════════╝\n\n"
        "🔥 *Get Unlimited Access to Premium Search!* 🔥\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 *API FEATURES:*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ *Unlimited Phone Number Searches* 📞\n"
        "✅ *Unlimited Username Searches* 👤\n"
        "✅ *Access to Billions of Records* 🌐\n"
        "✅ *Lightning Fast Results* ⚡\n"
        "✅ *Priority API Support* 🛠️\n"
        "✅ *Direct Integration Available* 🔗\n"
        "✅ *99.9% Uptime Guarantee* 💯\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 *PRICING PLANS:*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📅 *15 Days Access*\n"
        "   └─ *₹799* Only 💎\n"
        "   └─ Perfect for testing!\n\n"
        "📅 *30 Days Access*\n"
        "   └─ *₹1,299* Only 🚀\n"
        "   └─ Most Popular Choice!\n\n"
        "📅 *3 Months Access*\n"
        "   └─ *₹1,999* Only ⚡\n"
        "   └─ Best Value for Money!\n\n"
        "♾️ *LIFETIME Access*\n"
        "   └─ *₹5,000* Only 🔥\n"
        "   └─ One-time payment, Forever access!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 *WHY CHOOSE OUR API?*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔐 *100% Secure & Private*\n"
        "📊 *Real-time Data Access*\n"
        "💪 *High Performance & Scalability*\n"
        "🎁 *Special Discounts for Bulk Purchase*\n"
        "📞 *24/7 Dedicated Support*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Perfect for:*\n"
        "   • Developers & Programmers 💻\n"
        "   • Businesses & Agencies 🏢\n"
        "   • Research & Analytics 📊\n"
        "   • Heavy Users 🚀\n\n"
        "╔═══════════════════════════════╗\n"
        "║  👇 *CONTACT NOW TO BUY* 👇  ║\n"
        "╚═══════════════════════════════╝\n\n"
        "⚡ *Click the button below to purchase!* 💎",
        reply_markup=markup,
        parse_mode="Markdown"
    )

    # Send voice message
    try:
        with open("attached_assets/whensomeoneclickbuyunlimitedapi_1762169792052.mp3", "rb") as voice:
            user_bot.send_voice(message.chat.id, voice)
    except Exception as e:
        print(f"Error sending voice: {e}")

@user_bot.message_handler(func=lambda message: message.text == "🎟️ Claim Promo Code")
def claim_promo_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    msg = user_bot.send_message(
        message.chat.id,
        "🎟️ **Enter your promo code:**\n\n"
        "📝 Type the promo code to claim your reward! ⚡",
        parse_mode="Markdown"
    )
    user_bot.register_next_step_handler(msg, process_promo_code)

def process_promo_code(message):
    user_id = message.from_user.id
    promo_code = message.text.strip().upper()

    with promo_codes_lock:
        promo_codes = load_promo_codes()

        if promo_code not in promo_codes:
            user_bot.send_message(
                message.chat.id,
                "❌ **Invalid Promo Code!**\n\n"
                "The promo code you entered doesn't exist.\n\n"
                "🔄 **Please check and try again** ⚡",
                parse_mode="Markdown"
            )
            return

        promo_data = promo_codes[promo_code]

        # Check if user already claimed
        if str(user_id) in promo_data.get("used_by", []):
            user_bot.send_message(
                message.chat.id,
                "⚠️ **Already Claimed!**\n\n"
                "You have already used this promo code.\n\n"
                "🎟️ **Each code can be used only once per user** 💎",
                parse_mode="Markdown"
            )
            return

        # Check if promo code is exhausted
        if promo_data["used_count"] >= promo_data["max_uses"]:
            user_bot.send_message(
                message.chat.id,
                "😔 **Promo Code Exhausted!**\n\n"
                "This promo code has reached its usage limit.\n\n"
                "🔍 **Try another promo code** ⚡",
                parse_mode="Markdown"
            )
            return

        # Claim the promo code
        amount = promo_data["amount"]
        user = get_user(user_id)
        new_balance = user['balance'] + amount
        update_user_balance(user_id, new_balance)

        # Update promo code usage
        if "used_by" not in promo_data:
            promo_data["used_by"] = []
        promo_data["used_by"].append(str(user_id))
        promo_data["used_count"] += 1
        save_promo_codes(promo_codes)

    user_bot.send_message(
        message.chat.id,
        f"🎉 **Promo Code Claimed!** 💎\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 **Bonus Amount:** ₹{amount}\n"
        f"💵 **New Balance:** ₹{new_balance} 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ **Enjoy your bonus!** ⚡",
        parse_mode="Markdown"
    )


@user_bot.message_handler(func=lambda message: message.text == "👨‍💻 Support")
def contact_developer(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 **Contact Developer**", url="https://t.me/hackingteamx"))
    user_bot.send_message(
        message.chat.id,
        "👨‍💻 **Customer Support Center** 🎯\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 **Need assistance?** Our team is here!\n\n"
        "⚡ **We Help With:**\n"
        "   • Payment issues 💳\n"
        "   • Search queries 🔍\n"
        "   • Technical support 🛠️\n"
        "   • Account problems 👤\n\n"
        "📞 **Click below to contact us:** 👇\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@user_bot.message_handler(func=lambda message: message.text == "🎁 Refer and Earn")
def share_referral_link(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    user_id = message.from_user.id
    stats = get_referral_stats(user_id)
    referral_code = stats['referral_code']
    bot_username = "searchanything07_bot"
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    # Calculate time remaining until next Sunday 8:00 AM (IST - Indian Standard Time)
    import datetime
    import pytz
    
    # Get current time in IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    
    # Calculate next Sunday 8:00 AM IST
    # weekday(): Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
    current_weekday = now.weekday()
    
    # Days until next Sunday (6 = Sunday)
    if current_weekday == 6:  # Today is Sunday
        if now.hour < 8 or (now.hour == 8 and now.minute < 1):
            # Before 8:00 AM Sunday - target is today at 8:00 AM
            next_sunday = now.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            # At or after 8:00 AM Sunday - target is NEXT Sunday 8:00 AM (reset)
            next_sunday = now + datetime.timedelta(days=7)
            next_sunday = next_sunday.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        # Calculate days to next Sunday
        days_ahead = 6 - current_weekday
        next_sunday = now + datetime.timedelta(days=days_ahead)
        next_sunday = next_sunday.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Calculate time difference - PRECISE calculation with days, hours, and minutes
    time_remaining = next_sunday - now
    days_left = time_remaining.days
    total_seconds = time_remaining.seconds
    hours_left = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes_left = remaining_seconds // 60
    
    # Format time display
    if days_left > 0:
        time_display = f"{days_left} days, {hours_left} hours, {minutes_left} minutes"
    else:
        if hours_left > 0:
            time_display = f"{hours_left} hours, {minutes_left} minutes"
        else:
            time_display = f"{minutes_left} minutes"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📤 Share Referral Link", url=f"https://t.me/share/url?url={referral_link}"))
    markup.row(types.InlineKeyboardButton("🏆 View Top Referrers", callback_data="view_top_referrers"))
    
    user_bot.send_message(
        message.chat.id,
        "╔═══════════════════════════════╗\n"
        "║   *YOUR REFERRAL STATS* 🎁   ║\n"
        "╚═══════════════════════════════╝\n\n"
        f"*📊 Your Statistics:*\n\n"
        f"├─ 👥 Total Referrals: *{stats['total_referrals']}*\n"
        f"├─ 💰 Total Earnings: *₹{stats['total_earnings']}*\n"
        f"└─ 🎯 Bonus Per Referral: *₹{REFERRAL_BONUS}*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*🏆 WEEKLY TOP REFERRER CONTEST 🏆*\n\n"
        "╔═══════════════════════════════╗\n"
        "║  💰 *WIN ₹150 BONUS!* 💰  ║\n"
        "╚═══════════════════════════════╝\n\n"
        "🎯 The user with the *HIGHEST number of referrals* at the end of each week will receive:\n\n"
        "💸 *GRAND PRIZE: ₹150 BONUS* 💸\n\n"
        "📅 *Results Announcement:* Every Sunday at 8:00 AM\n"
        f"⏰ *Time Remaining:* {time_display}\n"
        "📢 *Check Results:* [Click Here](https://t.me/weareinprime1)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*🔗 YOUR REFERRAL LINK:*\n\n"
        "╔═══════════════════════════════╗\n"
        f"║ `{referral_link}` ║\n"
        "╚═══════════════════════════════╝\n\n"
        f"*💰 Earn ₹{REFERRAL_BONUS} per referral!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*How it works:*\n\n"
        "1️⃣ Share your link with friends\n"
        "2️⃣ They join using your link\n"
        "3️⃣ They gain access to bot features *(No recharge required!)*\n"
        f"4️⃣ You get ₹{REFERRAL_BONUS} bonus instantly!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 *Click buttons below to share or view top referrers!*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@user_bot.message_handler(func=lambda message: message.text == "🅾 Instagram Username to Number")
def instagram_search_info(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    user_id = message.from_user.id
    
    # Ask for access key
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Exit", callback_data="instagram_exit"))
    
    msg = user_bot.send_message(
        message.chat.id,
        "🔐 *INSTAGRAM ACCESS KEY REQUIRED* 🅾\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔑 *Please enter your access key:*\n\n"
        "📝 *Note:* Enter the access key to continue.\n\n"
        "💡 *Don't have an access key?*\n"
        "👇 *Buy from developer:*\n\n"
        "👤 *Developer:* @hackingteamx\n"
        "🤖 *Bot:* @Hackingteamx\\_bot\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    # Set user state to awaiting access key
    user_states[user_id] = {"awaiting_instagram_access_key": True}
    
@user_bot.callback_query_handler(func=lambda call: call.data == "instagram_exit")
def instagram_exit_handler(call):
    user_id = call.from_user.id
    
    # Clear user state
    if user_id in user_states:
        if user_states[user_id].get("awaiting_instagram_access_key") or user_states[user_id].get("awaiting_instagram_username"):
            del user_states[user_id]
    
    user_bot.edit_message_text(
        "❌ **Access Key Entry Cancelled** 🚫\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "You have exited the Instagram search interface.\n\n"
        "💡 Return anytime using the **🅾 Instagram Username to Number** button!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    
    user_bot.answer_callback_query(call.id, "✅ Exited successfully!")

@user_bot.callback_query_handler(func=lambda call: call.data == "instagram_retry")
def instagram_retry_handler(call):
    user_id = call.from_user.id
    
    # Set user state back to awaiting access key
    user_states[user_id] = {"awaiting_instagram_access_key": True}
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Exit", callback_data="instagram_exit"))
    
    user_bot.edit_message_text(
        "🔐 *INSTAGRAM ACCESS KEY REQUIRED* 🅾\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔑 *Please enter your access key:*\n\n"
        "📝 *Note:* Enter the access key to continue.\n\n"
        "💡 *Don't have an access key?*\n"
        "👇 *Buy from developer:*\n\n"
        "👤 *Developer:* @hackingteamx\n"
        "🤖 *Bot:* @Hackingteamx\\_bot\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    user_bot.answer_callback_query(call.id, "🔄 Please enter access key")

@user_bot.message_handler(func=lambda message: message.text == "📞 Search Number")
def search_number_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    user_bot.send_message(
        message.chat.id,
        "📞 <b>Phone Number Search</b> 🔍\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>Cost:</b> " + get_price_display(NUMBER_SEARCH_PRICE, ORIGINAL_PRICES['NUMBER_SEARCH']) + " 💎\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 <b>Enter phone number:</b>\n"
        "   • Format: <code>+91XXXXXXXXXX</code>\n"
        "   • Example: <code>+919876543210</code>\n\n"
        "⚡ <b>Results in seconds!</b> 🚀",
        parse_mode="HTML"
    )

@user_bot.message_handler(func=lambda message: message.text == "👤 Search Username")
def search_username_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Check if username search is enabled
    if not USERNAME_SEARCH_ENABLED:
        user_bot.send_message(
            message.chat.id,
            "⚠️ **Username Search Disabled** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Username search is currently **unavailable**.\n\n"
            "📞 **You can still use:**\n"
            "   • Phone Number Search ✅\n\n"
            "💡 **Contact support** for more info: @hackingteamx\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Directly activate username search mode
    user_id = message.from_user.id
    # Clear any previous search modes to avoid conflicts
    if user_id in user_id_search_mode:
        del user_id_search_mode[user_id]
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    username_search_mode[user_id] = True

    # Create keyboard with User ID search and Main Menu buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🆔 SEARCH BY USER ID")
    btn2 = types.KeyboardButton("🏠 Main Menu")
    markup.add(btn1, btn2)

    # Inline button for switching
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("🆔 Search by User ID", callback_data="switch_to_userid"))

    user_bot.send_message(
        message.chat.id,
        "👤 <b>Username Search</b> 🔍\n\n"
        "📊 You'll get:\n"
        "✅ Phone number linked to account\n"
        "✅ Deep search across billions of records\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 Cost: " + get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH']) + " ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 Enter your search\n\n"
        "🔍 Search By Username:\n"
        "   Example: @elonmusk\n\n"
        "🆔 Want Telegram User ID search? Click button below",
        reply_markup=inline_markup,
        parse_mode="HTML"
    )

@user_bot.message_handler(func=lambda message: message.text == "🔍 Search by Telegram Username")
def search_by_username_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Check if username search is enabled
    if not USERNAME_SEARCH_ENABLED:
        user_bot.send_message(
            message.chat.id,
            "⚠️ **Username Search Disabled** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Username search is currently **unavailable**.\n\n"
            "📞 **You can still use:**\n"
            "   • Phone Number Search ✅\n\n"
            "💡 **Contact support** for more info: @hackingteamx\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Set flag to indicate user is in normal username search mode (uses @Dfjyt_bot)
    user_id = message.from_user.id
    # Clear any previous search modes to avoid conflicts
    if user_id in user_id_search_mode:
        del user_id_search_mode[user_id]
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    username_search_mode[user_id] = True
    
    user_bot.send_message(
        message.chat.id,
        "👤 <b>Telegram Username Search</b> 🔍\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 Cost: " + get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH']) + " ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 <b>Enter username:</b>\n"
        "   • Format: @username\n"
        "   • Example: @john_doe\n\n"
        "🔐 <b>Deep search across billions of records!</b> 🌐",
        parse_mode="HTML"
    )

# Helper functions for profile search data formatting
def parse_profile_data(text):
    """Parse profile data from the response"""
    lines = text.split('\n')
    profile_data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.count('└') > 2 or line.count('├') > 2:
            continue
            
        clean_line = line.replace('└', '').replace('├', '').strip()
        
        if clean_line and (
            'ID' in clean_line or 
            '@' in clean_line or 
            'Telegram' in clean_line or
            'Request' in clean_line or
            'Profile' in clean_line or
            'Registration' in clean_line or
            any(char.isdigit() for char in clean_line)
        ):
            profile_data.append(clean_line)
    
    return profile_data

def parse_groups_data(text):
    """Parse groups/chats data from the response"""
    lines = text.split('\n')
    groups = []
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        
        clean_line = clean_line.replace('├', '').replace('└', '').replace('─', '').strip()
        
        if '@' in clean_line and any(char.isdigit() for char in clean_line):
            parts = clean_line.split()
            group_name = None
            
            for part in parts:
                if part.startswith('@'):
                    group_name = part
                    break
            
            if group_name:
                groups.append(group_name)
    
    return groups

def translate_russian(text):
    """Translate Russian text to English"""
    result = text
    for rus, eng in RUSSIAN_TO_ENGLISH.items():
        result = result.replace(rus, eng)
    return result

def format_profile_message(profile_text):
    """Format profile data for sending to user"""
    translated = translate_russian(profile_text)
    
    lines = translated.split('\n')
    formatted_lines = []
    
    for line in lines:
        clean_line = line.replace('└', '').replace('├', '').strip()
        if not clean_line:
            continue
        
        if 'Groups:' in clean_line or 'Messages:' in clean_line or 'Сообщения' in clean_line:
            continue
        
        formatted_lines.append(clean_line)
        
        if 'Registration:' in clean_line:
            break
    
    formatted_msg = "📊 Profile Data:\n\n"
    for line in formatted_lines:
        if line:
            formatted_msg += f"{line}\n"
    
    return formatted_msg

def format_groups_message(groups):
    """Format groups data for sending to user"""
    if not groups:
        return "👥 Groups:\n\nNo groups found"
    
    formatted_msg = "👥 Groups in which the user has joined:\n\n"
    
    for idx, group in enumerate(groups, 1):
        if idx == 1:
            formatted_msg += f"{idx}st - {group}\n"
        elif idx == 2:
            formatted_msg += f"{idx}nd - {group}\n"
        elif idx == 3:
            formatted_msg += f"{idx}rd - {group}\n"
        else:
            formatted_msg += f"{idx}th - {group}\n"
    
    return formatted_msg

# Async function to download profile file
async def _download_profile_file_async(html_message, clean_filename):
    """Download HTML file asynchronously"""
    try:
        actual_file = await profile_search_client.download_media(
            html_message,
            file_name=clean_filename
        )
        return actual_file
    except Exception as e:
        print(f"Error downloading profile file: {e}")
        return None

async def profile_userid_search_coroutine(user_id_str):
    """Profile search by User ID - same backend as username search"""
    print(f"\n{'='*70}")
    print(f"🔍 PROFILE SEARCH STARTED (BY USER ID)")
    print(f"{'='*70}")
    print(f"🆔 User ID: {user_id_str}")
    print(f"🤖 Target Bot: {PROFILE_SEARCH_PYROGRAM['target_bot']}")
    print(f"⏱️  Timestamp: {str(datetime.datetime.now())}")
    print(f"{'='*70}\n")
    
    profile_text = ""
    groups = []
    html_file = None
    
    try:
        # Step 1: Send User ID to target bot
        print(f"📤 STEP 1: Sending User ID to target bot...")
        await profile_search_client.send_message(PROFILE_SEARCH_PYROGRAM["target_bot"], user_id_str)
        print(f"✅ User ID sent successfully")
        print(f"⏳ Waiting for response (2 seconds)...\n")
        await asyncio.sleep(2)
        
        # Step 2: Get initial response
        print(f"📥 STEP 2: Fetching initial response from bot...")
        messages = []
        async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=5):
            messages.append(msg)
        print(f"📊 Response count: {len(messages)}")
        
        if messages:
            profile_text = messages[0].text or messages[0].caption or ""
            print(f"✅ Response received successfully")
            print(f"📄 Profile data length: {len(profile_text)} characters")
            print(f"📝 Profile preview: {profile_text[:100]}...\n")
            
            # Step 3: Try to extract profile data from buttons
            if messages[0].reply_markup:
                print(f"🔘 STEP 4: Found inline buttons in response")
                try:
                    buttons = messages[0].reply_markup.inline_keyboard
                    print(f"📊 Button rows found: {len(buttons)}")
                    
                    if buttons and buttons[0]:
                        target_button = buttons[0][0]
                        if hasattr(target_button, 'callback_data'):
                            print(f"✅ Button found at [0][0]")
                            print(f"🔐 Clicking button to get groups...")
                            
                            await profile_search_client.request_callback_answer(
                                chat_id=messages[0].chat.id,
                                message_id=messages[0].id,
                                callback_data=target_button.callback_data
                            )
                            print(f"✅ Button clicked successfully")
                            print(f"⏳ Waiting for groups data (2 seconds)...\n")
                            await asyncio.sleep(2)
                            
                            # Extract groups
                            print(f"📥 STEP 4.1: Fetching groups data...")
                            messages2 = []
                            async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                                messages2.append(msg)
                            print(f"📊 Groups response messages: {len(messages2)}")
                            
                            if messages2:
                                groups_text = messages2[0].text or messages2[0].caption or ""
                                print(f"📄 Groups data preview: {groups_text[:100]}...\n")
                                
                                for line in groups_text.split('\n'):
                                    if '@' in line:
                                        for word in line.split():
                                            if word.startswith('@'):
                                                groups.append(word)
                                print(f"✅ Groups extracted: {len(groups)} groups found")
                                for idx, grp in enumerate(groups[:10], 1):
                                    print(f"   {idx}. {grp}")
                                if len(groups) > 10:
                                    print(f"   ... and {len(groups) - 10} more groups\n")
                except Exception as e:
                    print(f"⚠️  Error extracting groups: {e}\n")
            else:
                print(f"⚠️  No inline buttons found in initial response\n")
            
            # Step 5: Send second query
            print(f"🔄 STEP 5: Sending second query to bot...")
            await profile_search_client.send_message(PROFILE_SEARCH_PYROGRAM["target_bot"], user_id_str)
            print(f"✅ Second query sent")
            print(f"⏳ Waiting for response (2 seconds)...\n")
            await asyncio.sleep(2)
            
            # Step 6: Get second response
            print(f"📥 STEP 6: Fetching second response...")
            messages3 = []
            async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=5):
                messages3.append(msg)
            print(f"📊 Response messages: {len(messages3)}")
            
            if messages3 and messages3[0].reply_markup:
                print(f"✅ Second response has buttons\n")
                try:
                    buttons = messages3[0].reply_markup.inline_keyboard
                    print(f"🔘 STEP 7: Processing second set of buttons...")
                    print(f"📊 Button rows: {len(buttons)}")
                    
                    if len(buttons) > 1 and buttons[1]:
                        target_button = buttons[1][0]
                        if hasattr(target_button, 'callback_data'):
                            print(f"✅ Button found at [1][0]")
                            print(f"🔐 Clicking to get message history...")
                            
                            await profile_search_client.request_callback_answer(
                                chat_id=messages3[0].chat.id,
                                message_id=messages3[0].id,
                                callback_data=target_button.callback_data
                            )
                            print(f"✅ Button clicked successfully")
                            print(f"⏳ Waiting for message history (2 seconds)...\n")
                            await asyncio.sleep(2)
                            
                            # Get message history
                            print(f"📥 STEP 7.1: Fetching message history...")
                            messages4 = []
                            async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                                messages4.append(msg)
                            print(f"📊 History messages: {len(messages4)}")
                            
                            if messages4 and messages4[0].reply_markup:
                                print(f"✅ Message history has download button\n")
                                print(f"🔘 STEP 8: Looking for download button...")
                                
                                found_download = False
                                for btn_row in messages4[0].reply_markup.inline_keyboard:
                                    for btn in btn_row:
                                        if hasattr(btn, 'text'):
                                            print(f"   • Button: {btn.text}")
                                            if 'скачать' in btn.text.lower() or 'download' in btn.text.lower():
                                                found_download = True
                                                print(f"\n✅ Download button found: {btn.text}")
                                                print(f"🔐 Clicking download button...")
                                                
                                                await profile_search_client.request_callback_answer(
                                                    chat_id=messages4[0].chat.id,
                                                    message_id=messages4[0].id,
                                                    callback_data=btn.callback_data
                                                )
                                                print(f"✅ Download button clicked")
                                                print(f"⏳ Waiting for file (3 seconds)...\n")
                                                await asyncio.sleep(3)
                                                
                                                # Get file
                                                print(f"📥 STEP 8.1: Fetching HTML file...")
                                                messages5 = []
                                                async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                                                    messages5.append(msg)
                                                print(f"📊 File messages: {len(messages5)}")
                                                
                                                if messages5:
                                                    for msg in messages5:
                                                        if msg.document:
                                                            html_file = msg
                                                            print(f"✅ HTML file found!")
                                                            print(f"📄 File name: {msg.document.file_name}")
                                                            print(f"📊 File size: {msg.document.file_size} bytes")
                                                            break
                except Exception as e:
                    print(f"⚠️  Error in step 7: {e}\n")
        else:
            print(f"⚠️  No initial response received\n")
        
        print(f"{'='*70}")
        print(f"✅ PROFILE SEARCH COMPLETED")
        print(f"{'='*70}")
        print(f"📊 Summary:")
        print(f"   • Profile data: ✅ Extracted")
        print(f"   • Groups found: {len(groups)}")
        print(f"   • HTML file: {'✅ Downloaded' if html_file else '❌ Not found'}")
        print(f"{'='*70}\n")
        
        return {"profile": profile_text, "groups": groups, "html_file": html_file}
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR IN PROFILE SEARCH")
        print(f"{'='*70}")
        print(f"🔴 Error: {str(e)}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def profile_search_coroutine(username):
    """Pure async function - with detailed logging for every step"""
    try:
        print(f"\n{'='*70}")
        print(f"🔍 PROFILE SEARCH STARTED")
        print(f"{'='*70}")
        print(f"👤 Username: @{username}")
        print(f"🤖 Target Bot: {PROFILE_SEARCH_PYROGRAM['target_bot']}")
        print(f"⏱️  Timestamp: {__import__('datetime').datetime.now()}")
        print(f"{'='*70}\n")
        
        # Step 1: Send username to bot
        print(f"📤 STEP 1: Sending username to target bot...")
        await profile_search_client.send_message(PROFILE_SEARCH_PYROGRAM["target_bot"], f"@{username}")
        print(f"✅ Username sent successfully")
        print(f"⏳ Waiting for response (2 seconds)...\n")
        await asyncio.sleep(2)
        
        # Step 2: Retrieve initial response
        print(f"📥 STEP 2: Fetching initial response from bot...")
        messages = []
        async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=5):
            messages.append(msg)
        print(f"📊 Response count: {len(messages)} messages")
        
        if not messages:
            print(f"❌ No response received from target bot")
            return {"error": "No response from target bot"}
        
        # Step 3: Extract profile data
        print(f"✅ Response received successfully\n")
        response = messages[0]
        profile_text = response.text or response.caption or ""
        groups = []
        html_file = None
        
        # Check if bot is still searching (Russian: Выполняется поиск)
        if "Выполняется поиск" in profile_text:
            print(f"⚠️  Bot still searching, no results found")
            return {"error": "No results found"}
        
        print(f"📋 STEP 3: Extracting profile data...")
        print(f"📄 Profile data length: {len(profile_text)} characters")
        print(f"📝 Profile preview: {profile_text[:100]}...\n")
        
        # Step 4: Check for buttons and extract groups
        if response.reply_markup:
            print(f"🔘 STEP 4: Found inline buttons in response")
            try:
                buttons = response.reply_markup.inline_keyboard
                print(f"📊 Button rows found: {len(buttons)}")
                
                if buttons and len(buttons) > 0:
                    target_button = buttons[0][0] if buttons[0] else None
                    if target_button and hasattr(target_button, 'callback_data'):
                        print(f"✅ Button found at [0][0]")
                        print(f"🔐 Clicking button to get groups...")
                        
                        await profile_search_client.request_callback_answer(
                            chat_id=response.chat.id,
                            message_id=response.id,
                            callback_data=target_button.callback_data
                        )
                        print(f"✅ Button clicked successfully")
                        print(f"⏳ Waiting for groups data (2 seconds)...\n")
                        await asyncio.sleep(2)
                        
                        # Extract groups
                        print(f"📥 STEP 4.1: Fetching groups data...")
                        messages2 = []
                        async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                            messages2.append(msg)
                        print(f"📊 Groups response messages: {len(messages2)}")
                        
                        if messages2:
                            groups_text = messages2[0].text or messages2[0].caption or ""
                            print(f"📄 Groups data preview: {groups_text[:100]}...\n")
                            
                            for line in groups_text.split('\n'):
                                if '@' in line:
                                    for word in line.split():
                                        if word.startswith('@'):
                                            groups.append(word)
                            print(f"✅ Groups extracted: {len(groups)} groups found")
                            for idx, grp in enumerate(groups[:10], 1):
                                print(f"   {idx}. {grp}")
                            if len(groups) > 10:
                                print(f"   ... and {len(groups) - 10} more groups\n")
            except Exception as e:
                print(f"⚠️  Error extracting groups: {e}\n")
        else:
            print(f"⚠️  No inline buttons found in initial response\n")
        
        # Step 5: Send second query
        print(f"🔄 STEP 5: Sending second query to bot...")
        await profile_search_client.send_message(PROFILE_SEARCH_PYROGRAM["target_bot"], f"@{username}")
        print(f"✅ Second query sent")
        print(f"⏳ Waiting for response (2 seconds)...\n")
        await asyncio.sleep(2)
        
        # Step 6: Get second response
        print(f"📥 STEP 6: Fetching second response...")
        messages3 = []
        async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=5):
            messages3.append(msg)
        print(f"📊 Response messages: {len(messages3)}")
        
        if messages3 and messages3[0].reply_markup:
            print(f"✅ Second response has buttons\n")
            try:
                buttons = messages3[0].reply_markup.inline_keyboard
                print(f"🔘 STEP 7: Processing second set of buttons...")
                print(f"📊 Button rows: {len(buttons)}")
                
                if len(buttons) > 1 and buttons[1]:
                    target_button = buttons[1][0]
                    if hasattr(target_button, 'callback_data'):
                        print(f"✅ Button found at [1][0]")
                        print(f"🔐 Clicking to get message history...")
                        
                        await profile_search_client.request_callback_answer(
                            chat_id=messages3[0].chat.id,
                            message_id=messages3[0].id,
                            callback_data=target_button.callback_data
                        )
                        print(f"✅ Button clicked successfully")
                        print(f"⏳ Waiting for message history (2 seconds)...\n")
                        await asyncio.sleep(2)
                        
                        # Get message history
                        print(f"📥 STEP 7.1: Fetching message history...")
                        messages4 = []
                        async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                            messages4.append(msg)
                        print(f"📊 History messages: {len(messages4)}")
                        
                        if messages4 and messages4[0].reply_markup:
                            print(f"✅ Message history has download button\n")
                            print(f"🔘 STEP 8: Looking for download button...")
                            
                            found_download = False
                            for btn_row in messages4[0].reply_markup.inline_keyboard:
                                for btn in btn_row:
                                    if hasattr(btn, 'text'):
                                        print(f"   • Button: {btn.text}")
                                        if 'скачать' in btn.text.lower() or 'download' in btn.text.lower():
                                            found_download = True
                                            print(f"\n✅ Download button found: {btn.text}")
                                            print(f"🔐 Clicking download button...")
                                            
                                            await profile_search_client.request_callback_answer(
                                                chat_id=messages4[0].chat.id,
                                                message_id=messages4[0].id,
                                                callback_data=btn.callback_data
                                            )
                                            print(f"✅ Download button clicked")
                                            print(f"⏳ Waiting for file (3 seconds)...\n")
                                            await asyncio.sleep(3)
                                            
                                            # Get file
                                            print(f"📥 STEP 8.1: Fetching HTML file...")
                                            messages5 = []
                                            async for msg in profile_search_client.get_chat_history(PROFILE_SEARCH_PYROGRAM["target_bot"], limit=3):
                                                messages5.append(msg)
                                            print(f"📊 File messages: {len(messages5)}")
                                            
                                            for msg in messages5:
                                                if msg.document:
                                                    html_file = msg
                                                    print(f"✅ HTML file found!")
                                                    print(f"📄 File name: {msg.document.file_name}")
                                                    print(f"📊 File size: {msg.document.file_size} bytes\n")
                                                    break
                                            
                                            print(f"{'='*70}")
                                            print(f"✅ PROFILE SEARCH COMPLETED SUCCESSFULLY")
                                            print(f"{'='*70}")
                                            print(f"📊 Summary:")
                                            print(f"   • Profile data: ✅ Extracted")
                                            print(f"   • Groups found: {len(groups)}")
                                            print(f"   • HTML file: {'✅ Downloaded' if html_file else '❌ Not found'}")
                                            print(f"{'='*70}\n")
                                            
                                            return {"profile": profile_text, "groups": groups, "html_file": html_file}
                            
                            if not found_download:
                                print(f"⚠️  No download button found in buttons\n")
            except Exception as e:
                print(f"⚠️  Error in step 7: {e}\n")
        else:
            print(f"⚠️  No buttons in second response or no response\n")
        
        print(f"{'='*70}")
        print(f"✅ PROFILE SEARCH COMPLETED")
        print(f"{'='*70}")
        print(f"📊 Summary:")
        print(f"   • Profile data: ✅ Extracted")
        print(f"   • Groups found: {len(groups)}")
        print(f"   • HTML file: {'✅ Downloaded' if html_file else '❌ Not found'}")
        print(f"{'='*70}\n")
        
        return {"profile": profile_text, "groups": groups, "html_file": html_file}
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR IN PROFILE SEARCH")
        print(f"{'='*70}")
        print(f"🔴 Error: {str(e)}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@user_bot.message_handler(func=lambda message: message.text == "👤 PROFILE LOOKUP")
def profile_search_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Set profile search mode directly (no submenu)
    user_id = message.from_user.id
    # Clear any previous search modes to avoid conflicts
    if user_id in username_search_mode:
        del username_search_mode[user_id]
    if user_id in user_id_search_mode:
        del user_id_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    profile_search_mode[user_id] = True

    # Create keyboard with User ID search and Main Menu buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🆔 LOOKUP BY USER ID")
    btn2 = types.KeyboardButton("🏠 Main Menu")
    markup.add(types.KeyboardButton("🆔 LOOKUP BY USER ID"), types.KeyboardButton("🏠 Main Menu"))

    # Inline button for switching
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("🆔 Lookup by User ID", callback_data="switch_to_profile_userid"))

    user_bot.send_message(
        message.chat.id,
        "👤 PROFILE LOOKUP 🔍\n\n"
        "📊 You'll get:\n"
        "✅ Profile info, Registration time\n"
        "✅ Groups & channels where user is joined\n"
        "✅ Messages done by user in group/channel (HTML file)\n\n"
        f"💰 Cost: {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n\n"
        "📝 Enter username:\n"
        "   Example - @elonmusk\n\n"
        "🆔 Want User ID search? Click button below",
        reply_markup=inline_markup,
        parse_mode="HTML"
    )


# Handle Main Menu button to properly exit all search modes
@user_bot.message_handler(func=lambda message: message.text == "🏠 Main Menu")
def global_main_menu_handler(message):
    """Exit all search modes and return to main menu"""
    user_id = message.from_user.id
    # Clear all search modes
    if user_id in profile_search_mode: del profile_search_mode[user_id]
    if user_id in profile_userid_search_mode: del profile_userid_search_mode[user_id]
    if user_id in username_search_mode: del username_search_mode[user_id]
    if user_id in user_id_search_mode: del user_id_search_mode[user_id]
    
    # Clear user states
    if user_id in user_states:
        user_states[user_id].pop("waiting_utr", None)
        user_states[user_id].pop("awaiting_instagram_access_key", None)
        user_states[user_id].pop("awaiting_instagram_username", None)
        
    show_main_menu(message.chat.id)

# Redundant specific handlers can be removed or kept as they won't interfere
@user_bot.message_handler(func=lambda message: message.text == "🏠 Main Menu" and message.from_user.id in profile_search_mode)
def profile_search_exit_to_menu(message):
    """Exit profile search mode and return to main menu"""
    user_id = message.from_user.id
    # Clear profile search mode
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    # Clear profile user ID search mode too if set
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    # Call the main menu handler
    show_main_menu(message.chat.id)


# HIGH PRIORITY: Check specific buttons BEFORE generic profile search mode
@user_bot.message_handler(func=lambda message: message.text == "🆔 LOOKUP BY USER ID" and message.from_user.id in profile_search_mode)
def profile_search_to_userid(message):
    """Route from profile search to user ID search"""
    user_id = message.from_user.id
    # Clear profile search mode and set user ID search mode
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    profile_userid_search_mode[user_id] = True
    
    user_bot.send_message(
        message.chat.id,
        "🆔 <b>LOOKUP BY USER ID</b> 🆔\n\n"
        "📊 You'll get:\n"
        "✅ Profile info, bio, status\n"
        "✅ All groups & channels\n"
        "✅ Message history (HTML file)\n\n"
        f"💰 <b>Cost:</b> {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n\n"
        "🔢 <b>Enter Telegram User ID:</b>\n"
        "   Example: <code>8457239528</code>",
        parse_mode="HTML"
    )

@user_bot.message_handler(func=lambda message: message.from_user.id in profile_userid_search_mode and profile_userid_search_mode.get(message.from_user.id) and message.text)
def handle_profile_userid_search_query(message):
    user_id = message.from_user.id
    query = message.text.strip()
    
    # Clear profile user ID search mode
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    
    # Validate query (should be numeric)
    if not query or query.startswith('/') or query in ["🏠 Main Menu"]:
        return
    
    if not query.isdigit() or len(query) < 8:
        user_bot.send_message(
            message.chat.id,
            "❌ Invalid User ID format!\n\n"
            "Please enter only numeric digits (8-11 digits)\n"
            "Example: 85369635"
        )
        return
    
    if not profile_search_client:
        user_bot.send_message(
            message.chat.id,
            "⚠️ Profile Search Not Configured 🚫\n\n"
            "Please configure with API ID, Hash, and phone\n"
            "Contact: @hackingteamx"
        )
        return
    
    # Check if user_id is blocked from lookup
    if is_lookup_blocked(query, "user_id"):
        user_bot.send_message(
            message.chat.id,
            f"🚫 **Profile Lookup Prevented** 🔒\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ **User ID {query}** is blocked from profile lookup\n\n"
            f"This profile is unavailable due to security restrictions.\n\n"
            f"💡 Try searching a different profile\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Check balance before searching
    user = get_user(user_id)
    if user['balance'] < PROFILE_SEARCH_PRICE:
        user_bot.send_message(
            message.chat.id,
            f"⚠️ **Insufficient Balance** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Current Balance:** ₹{user['balance']}\n"
            f"💎 **Required Amount:** {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n"
            f"❌ **Need:** ₹{PROFILE_SEARCH_PRICE - user['balance']} more\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚀 **Please add balance to continue!** ⚡",
            parse_mode="Markdown"
        )

        # Send appropriate voice alert
        try:
            voice_file = open('attached_assets/insufficientbalancewhenusernamesearch_1762169792094.mp3', 'rb')
            user_bot.send_voice(message.chat.id, voice_file)
            voice_file.close()
        except Exception as e:
            print(f"Error sending voice: {e}")

        return
    
    try:
        processing = user_bot.send_message(
            message.chat.id,
            "🔄 Looking up User ID 🔍\n\n"
            f"🆔 User ID: {query}\n"
            "📊 Status: Fetching profile data...\n\n"
            "⏳ Please wait..."
        )
        
        # Run search on profile search event loop
        try:
            loop = get_profile_search_loop()
            future = asyncio.run_coroutine_threadsafe(
                profile_userid_search_coroutine(query),
                loop
            )
            result = future.result(timeout=120)
        except Exception as e:
            result = {"error": f"Search failed: {str(e)}"}
        
        # Edit processing message
        user_bot.edit_message_text(
            "✅ User Found! 🎯\n\n"
            f"🆔 User ID: {query}\n"
            "📊 Status: Preparing data...\n\n"
            "⏳ Sending results...",
            message.chat.id,
            processing.message_id
        )
        
        time.sleep(1)
        user_bot.delete_message(message.chat.id, processing.message_id)
        
        if "error" in result:
            user_bot.send_message(
                message.chat.id,
                f"❌ **Profile Search Failed**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Unable to retrieve profile information at this moment.\n\n"
                f"💰 **Balance Status:** No charge applied ✅\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Please try again later.",
                parse_mode="Markdown"
            )
            return
        
        # Parse and check groups information
        groups_text_from_result = result.get("groups", [])
        groups = groups_text_from_result if isinstance(groups_text_from_result, list) else []
        
        # If no groups found, show message and don't deduct balance
        if not groups:
            user_bot.send_message(
                message.chat.id,
                f"ℹ️ **No Results Available** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **User ID:** {query}\n\n"
                f"⚠️ **Profile information is not available** in our database.\n\n"
                f"💰 **Balance Status:** No charge applied ✅\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Try searching for a different profile.",
                parse_mode="Markdown"
            )
            return
        
        # Send profile data with proper formatting
        profile_text = result.get("profile", "")
        if profile_text:
            profile_msg = format_profile_message(profile_text)
            user_bot.send_message(
                message.chat.id,
                profile_msg
            )
        
        # Send groups information
        groups_msg = format_groups_message(groups)
        user_bot.send_message(
            message.chat.id,
            groups_msg
        )
        
        # Send HTML file if available
        html_message = result.get("html_file")
        if html_message and html_message.document:
            try:
                clean_filename = f"listofmessagesById{query}.html"
                
                # Download file using async wrapper to downloads folder
                loop = get_profile_search_loop()
                download_future = asyncio.run_coroutine_threadsafe(
                    _download_profile_file_async(html_message, clean_filename),
                    loop
                )
                downloaded_path = download_future.result(timeout=60)
                
                if downloaded_path and os.path.exists(downloaded_path):
                    # Move to downloads folder
                    downloads_dir = "./downloads"
                    os.makedirs(downloads_dir, exist_ok=True)
                    
                    final_path = os.path.join(downloads_dir, clean_filename)
                    
                    # If file exists in current location, move it
                    if downloaded_path != final_path:
                        import shutil
                        shutil.move(downloaded_path, final_path)
                    
                    print(f"📋 HTML file saved to: {final_path}")
                    
                    # Send file to user
                    with open(final_path, 'rb') as f:
                        user_bot.send_document(
                            message.chat.id,
                            f,
                            caption=f"📋 List of messages by User ID {query}\n\nMessages in groups/channels"
                        )
                    
                    print(f"✅ HTML file sent to user: {clean_filename}")
                    
                    # Delete after sending
                    if os.path.exists(final_path):
                        os.remove(final_path)
                        print(f"🗑️  HTML file deleted: {final_path}")
            except Exception as e:
                print(f"⚠️ Could not send HTML file: {e}")
                import traceback
                traceback.print_exc()
        
        # Balance is deducted in perform_search function to avoid duplicate charges
        # Do NOT deduct here to prevent double charging
        
        user_bot.send_message(
            message.chat.id,
            f"✅ <b>User ID Search Completed!</b> 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💸 <b>Deducted:</b> {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n"
            f"💵 <b>Remaining Balance:</b> ₹{get_user(user_id)['balance']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Retrieved:</b>\n"
            f"  • ✅ Profile Data\n"
            f"  • ✅ {len(groups)} Groups/Channels\n"
            f"  • ✅ Message History\n\n"
            f"Click Main Menu to continue",
            parse_mode="HTML"
        )
    
    except Exception as e:
        user_bot.send_message(
            message.chat.id,
            f"❌ Error: {str(e)}"
        )

@user_bot.message_handler(func=lambda message: message.from_user.id in profile_search_mode and profile_search_mode.get(message.from_user.id) and message.text)
def handle_profile_search_query(message):
    user_id = message.from_user.id
    query = message.text.strip()
    
    # Clear profile search mode
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    
    # Validate query
    if not query or query.startswith('/') or query in ["🏠 Main Menu", "🆔 LOOKUP BY USER ID"]:
        return
    
    clean_username = query.lstrip('@')
    
    # Check if username is blocked from lookup
    if is_lookup_blocked(clean_username, "username"):
        user_bot.send_message(
            message.chat.id,
            f"🚫 **Profile Lookup Prevented** 🔒\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ **@{clean_username}** is blocked from profile lookup\n\n"
            f"This profile is unavailable due to security restrictions.\n\n"
            f"💡 Try searching a different profile\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    if not profile_search_client:
        user_bot.send_message(
            message.chat.id,
            "⚠️ **Profile Search Not Configured** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Please configure with:\n"
            "  • api_id\n"
            "  • api_hash\n"
            "  • phone\n\n"
            "📞 Contact: @hackingteamx\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Check balance before searching
    user = get_user(user_id)
    if user['balance'] < PROFILE_SEARCH_PRICE:
        user_bot.send_message(
            message.chat.id,
            f"⚠️ **Insufficient Balance** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Current Balance:** ₹{user['balance']}\n"
            f"💎 **Required Amount:** {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n"
            f"❌ **Need:** ₹{PROFILE_SEARCH_PRICE - user['balance']} more\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚀 **Please add balance to continue!** ⚡",
            parse_mode="Markdown"
        )

        # Send appropriate voice alert
        try:
            voice_file = open('attached_assets/insufficientbalancewhenusernamesearch_1762169792094.mp3', 'rb')
            user_bot.send_voice(message.chat.id, voice_file)
            voice_file.close()
        except Exception as e:
            print(f"Error sending voice: {e}")

        return
    
    try:
        processing = user_bot.send_message(
            message.chat.id,
            "🔄 Searching Profile 🔍\n\n"
            f"📝 Username: {clean_username}\n"
            "📊 Status: Fetching profile data...\n\n"
            "⏳ Please wait..."
        )
        
        # Run search on profile search event loop
        try:
            loop = get_profile_search_loop()
            future = asyncio.run_coroutine_threadsafe(
                profile_search_coroutine(clean_username),
                loop
            )
            result = future.result(timeout=120)
        except Exception as e:
            result = {"error": f"Search failed: {str(e)}"}
        
        # Edit processing message
        user_bot.edit_message_text(
            "✅ Profile Found! 🎯\n\n"
            f"📝 Username: {clean_username}\n"
            "📊 Status: Preparing data...\n\n"
            "⏳ Sending results...",
            message.chat.id,
            processing.message_id
        )
        
        time.sleep(1)
        user_bot.delete_message(message.chat.id, processing.message_id)
        
        if "error" in result:
            user_bot.send_message(
                message.chat.id,
                f"❌ **Profile Search Failed**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Unable to retrieve profile information at this moment.\n\n"
                f"💰 **Balance Status:** No charge applied ✅\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Please try again later.",
                parse_mode="Markdown"
            )
            return
        
        # Check if groups information was found
        groups_text_from_result = result.get("groups", [])
        groups = groups_text_from_result if isinstance(groups_text_from_result, list) else []
        
        # If no groups found, show message and don't deduct balance
        if not groups:
            user_bot.send_message(
                message.chat.id,
                f"ℹ️ **No Results Available** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Username:** @{clean_username}\n\n"
                f"⚠️ **Profile information is not available** in our database.\n\n"
                f"💰 **Balance Status:** No charge applied ✅\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Try searching for a different profile.",
                parse_mode="Markdown"
            )
            return
        
        # Send profile data with proper formatting
        profile_text = result.get("profile", "")
        if profile_text:
            profile_msg = format_profile_message(profile_text)
            user_bot.send_message(
                message.chat.id,
                profile_msg
            )
        
        # Send groups information
        groups_msg = format_groups_message(groups)
        user_bot.send_message(
            message.chat.id,
            groups_msg
        )
        
        # Send HTML file if available
        html_message = result.get("html_file")
        if html_message and html_message.document:
            try:
                clean_filename = f"listofmessagesBy{clean_username}.html"
                
                # Download file using async wrapper to downloads folder
                loop = get_profile_search_loop()
                download_future = asyncio.run_coroutine_threadsafe(
                    _download_profile_file_async(html_message, clean_filename),
                    loop
                )
                downloaded_path = download_future.result(timeout=60)
                
                if downloaded_path and os.path.exists(downloaded_path):
                    # Move to downloads folder
                    downloads_dir = "./downloads"
                    os.makedirs(downloads_dir, exist_ok=True)
                    
                    final_path = os.path.join(downloads_dir, clean_filename)
                    
                    # If file exists in current location, move it
                    if downloaded_path != final_path:
                        import shutil
                        shutil.move(downloaded_path, final_path)
                    
                    print(f"📋 HTML file saved to: {final_path}")
                    
                    # Send file to user
                    with open(final_path, 'rb') as f:
                        user_bot.send_document(
                            message.chat.id,
                            f,
                            caption=f"📋 List of messages by {clean_username}\n\nMessages in groups/channels"
                        )
                    
                    print(f"✅ HTML file sent to user: {clean_filename}")
                    
                    # Delete after sending
                    if os.path.exists(final_path):
                        os.remove(final_path)
                        print(f"🗑️  HTML file deleted: {final_path}")
            except Exception as e:
                print(f"⚠️ Could not send HTML file: {e}")
                import traceback
                traceback.print_exc()
        
        # Balance is deducted in perform_search function to avoid duplicate charges
        # Do NOT deduct here to prevent double charging
        
        user_bot.send_message(
            message.chat.id,
            f"✅ <b>Profile Search Completed!</b> 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💸 <b>Deducted:</b> {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n"
            f"💵 <b>Remaining Balance:</b> ₹{get_user(user_id)['balance']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Retrieved:</b>\n"
            f"  • ✅ Profile Data\n"
            f"  • ✅ {len(groups)} Groups/Channels\n"
            f"  • ✅ Message History\n\n"
            f"Click Main Menu to continue",
            parse_mode="HTML"
        )
    
    except Exception as e:
        user_bot.send_message(
            message.chat.id,
            f"❌ **Error:** {str(e)}",
            parse_mode="Markdown"
        )

@user_bot.message_handler(func=lambda message: message.text == "🆔 LOOKUP BY USER ID" and message.from_user.id not in profile_search_mode)
def search_profile_by_user_id_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Set flag to indicate user is in profile User ID search mode
    user_id = message.from_user.id
    profile_userid_search_mode[user_id] = True

    user_bot.send_message(
        message.chat.id,
        "🆔 LOOKUP BY USER ID 🆔\n\n"
        "📊 You'll get:\n"
        "✅ Profile info, bio, status\n"
        "✅ All groups & channels\n"
        "✅ Message history (HTML file)\n\n"
        f"💰 Cost: {get_price_display(PROFILE_SEARCH_PRICE, ORIGINAL_PRICES['PROFILE_SEARCH'])}\n\n"
        "🔢 Enter Telegram User ID:\n"
        "   Example: 845494856"
    )

@user_bot.message_handler(func=lambda message: message.text == "🆔 SEARCH BY USER ID")
def search_by_user_id_prompt(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Check if username search is enabled
    if not USERNAME_SEARCH_ENABLED:
        user_bot.send_message(
            message.chat.id,
            "⚠️ **User ID Search Disabled** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "User ID search is currently **unavailable**.\n\n"
            "📞 **You can still use:**\n"
            "   • Phone Number Search ✅\n\n"
            "💡 **Contact support** for more info: @hackingteamx\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    user_id = message.from_user.id
    # Clear any previous search modes to avoid conflicts
    if user_id in username_search_mode:
        del username_search_mode[user_id]
    if user_id in profile_search_mode:
        del profile_search_mode[user_id]
    if user_id in profile_userid_search_mode:
        del profile_userid_search_mode[user_id]
    # Set flag to indicate user is in User ID search mode
    user_id_search_mode[user_id] = True

    user_bot.send_message(
        message.chat.id,
        "🆔 **Telegram User ID Search** 🔍\n\n"
        "📊 You'll get:\n"
        "✅ Phone number linked to account\n"
        "✅ Deep search across billions of records\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 **Cost:** ₹" + str(USERNAME_SEARCH_PRICE) + " ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 **Enter User ID:**\n"
        "   • Format: `853269852`\n"
        "   • Only numeric digits\n\n"
        "⏳ **Search takes 10-20 seconds** ⚡",
        parse_mode="Markdown"
    )


@user_bot.message_handler(func=lambda message: message.text and message.text.startswith("@") and 
                         message.from_user.id not in username_search_mode and
                         message.from_user.id not in user_id_search_mode and 
                         message.from_user.id not in profile_search_mode and
                         message.from_user.id not in profile_userid_search_mode)
def auto_start_username_search(message):
    """Auto-start username search when user enters @username from home tab only"""
    user_id = message.from_user.id
    
    # IMPORTANT: Auto-trigger should NOT work when user is in any search mode
    # Check if user is explicitly in profile search mode (even though handler shouldn't trigger)
    # as extra safety check
    if user_id in profile_search_mode or user_id in profile_userid_search_mode:
        return
    
    # Check channel membership
    if not require_channel_membership(message):
        return
    
    username = message.text.strip()
    
    # Validate username
    if not is_username(username):
        user_bot.send_message(
            message.chat.id,
            "❌ **Invalid Username Format**\n\n"
            "Please enter a valid Telegram username starting with @\n"
            "Example: @elonmusk"
        )
        return
    
    # Check if already searched with no data
    clean_username = username.lstrip('@').lower()
    if is_already_searched_no_data(clean_username, "username"):
        # Send in JSON format like regular searches
        no_result_json = [
            [
                {
                    "Username": username
                },
                {
                    "Status": "Already Searched"
                },
                {
                    "Message": "No data available for this username"
                }
            ]
        ]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        json_result = f"```json\n{json_str}\n```"
        send_with_typing_effect(message.chat.id, json_result)
        
        user_bot.send_message(
            message.chat.id,
            f"⚠️ **Search Not Allowed** 🚫\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Username:** {username}\n\n"
            f"❌ **This username has no data in our records.**\n\n"
            f"💰 **Your balance is safe** ✅\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Check if username search is enabled
    if not USERNAME_SEARCH_ENABLED:
        user_bot.send_message(
            message.chat.id,
            "⚠️ **Username Search Disabled** 🚫"
        )
        return
    
    # Check balance
    user = get_user(user_id)
    if user['balance'] < USERNAME_SEARCH_PRICE:
        user_bot.send_message(
            message.chat.id,
            f"⚠️ **Insufficient Balance** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Current Balance:** ₹{user['balance']}\n"
            f"💎 **Required Amount:** ₹{USERNAME_SEARCH_PRICE}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return
    
    # Valid username - Show choice buttons
    clean_username = username.lstrip('@')
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("👤 Search Username", callback_data="sel_username_prompt")
    btn2 = types.InlineKeyboardButton("🔍 Profile Lookup", callback_data=f"sel_profile_{clean_username}")
    markup.add(btn1, btn2)

    user_bot.send_message(
        message.chat.id,
        f"✨ <b>Username Detected:</b> <code>@{clean_username}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 <b>Select Search Type:</b>\n\n"
        "👤 <b>Username Search:</b> Get phone number\n"
        "🔍 <b>Profile Lookup:</b> Get group history & more\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup,
        parse_mode="HTML"
    )
    return


def perform_search(message, query, search_type=None, process_msg=None):
    user_id = message.from_user.id
    original_query = query
    
    # Define navigation markups for persistence
    def get_nav_markup():
        if user_id in profile_search_mode:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("🆔 LOOKUP BY USER ID"), types.KeyboardButton("🏠 Main Menu"))
            return markup
        elif user_id in username_search_mode or user_id in user_id_search_mode:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("🏠 Main Menu"))
            return markup
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📞 Search Number")
            btn2 = types.KeyboardButton("👤 Search Username")
            btn_profile = types.KeyboardButton("👤 PROFILE LOOKUP")
            btn3 = types.KeyboardButton("💰 Check Balance")
            btn4 = types.KeyboardButton("➕ Add Balance")
            btn6 = types.KeyboardButton("🎟️ Claim Promo Code")
            btn7 = types.KeyboardButton("🚀 Buy API")
            btn8 = types.KeyboardButton("👨‍💻 Support")
            btn9 = types.KeyboardButton("🎁 Refer and Earn")
            markup.add(btn1, btn2, btn_profile, btn3, btn4, btn6, btn9, btn7, btn8)
            return markup

    current_reply_markup = get_nav_markup()

    # ===== CONTEXT-AWARE SEARCH LOGIC =====
    if search_type is None:
        # Priority 1: Check user's CURRENT MODE
        if user_id in profile_search_mode:
            if is_username(query) or (query.isdigit() and len(query) > 5):
                search_type = "profile_lookup"
                price = PROFILE_SEARCH_PRICE
                search_icon = "👤"
                search_label = "Profile"
                original_query = query.lstrip('@') if is_username(query) else query
            else:
                user_bot.send_message(message.chat.id, "❌ **Invalid Query** 🚫\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n📝 **Profile lookup requires:**\n• Username (e.g., @username)\n• OR User ID (digits)\n\n💡 **Try again!**", parse_mode="Markdown", reply_markup=current_reply_markup)
                return
        elif user_id in username_search_mode:
            if is_username(query):
                search_type = "username"
                price = USERNAME_SEARCH_PRICE
                search_icon = "👤"
                search_label = "Username"
                original_query = query.lstrip('@')
            else:
                user_bot.send_message(message.chat.id, "❌ **Invalid Format** 🚫\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n📝 **Username search requires @username**\n\n💡 **Please try again!**", parse_mode="Markdown", reply_markup=current_reply_markup)
                return
        elif user_id in user_id_search_mode:
            if query.isdigit():
                search_type = "user_id"
                price = USERNAME_SEARCH_PRICE
                search_icon = "🆔"
                search_label = "User ID"
                original_query = query
            else:
                user_bot.send_message(message.chat.id, "❌ **Invalid User ID** 🚫\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n📝 **User ID search requires digits only**\n\n💡 **Please try again!**", parse_mode="Markdown", reply_markup=current_reply_markup)
                return
        else:
            # HOME TAB logic
            if is_username(query):
                search_type = "username"
                price = USERNAME_SEARCH_PRICE
                search_icon = "👤"
                search_label = "Username"
                original_query = query.lstrip('@')
            elif is_phone_number(query):
                formatted = format_indian_number(query)
                if formatted:
                    search_type = "phone"
                    price = NUMBER_SEARCH_PRICE
                    search_icon = "📞"
                    search_label = "Phone Number"
                    query = formatted
                    original_query = formatted
                else: return
            else: return
    else:
        # search_type provided by button
        if search_type == "username":
            price = USERNAME_SEARCH_PRICE
            search_icon = "👤"
            search_label = "Username"
            original_query = query.lstrip('@')
        elif search_type == "profile_lookup":
            price = PROFILE_SEARCH_PRICE
            search_icon = "🔍"
            search_label = "Profile"
            original_query = query.lstrip('@')

    # Define display variables
    if search_type == "username":
        display_label = "Username"
        display_query = f"@{original_query}"
        display_query_escaped = display_query.replace("_", "\\_")
    elif search_type == "user_id":
        display_label = "User ID"
        display_query = original_query
        display_query_escaped = display_query
    elif search_type == "profile_lookup":
        display_label = "Profile"
        display_query = f"@{original_query}" if not original_query.isdigit() else original_query
        display_query_escaped = display_query.replace("_", "\\_") if "@" in display_query else display_query
    else:
        display_label = "Phone Number"
        display_query = query
        display_query_escaped = display_query

    # Check if already searched with no data
    if search_type in ["username", "user_id"]:
        check_query = original_query.lower()
        if is_already_searched_no_data(check_query, search_type):
            user_bot.send_message(message.chat.id, f"⚠️ **Search Not Allowed** 🚫\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n{search_icon} **{display_label}:** `{display_query_escaped}`\n\n❌ **No data in our records.**\n\n💰 **Balance safe** ✅\n━━━━━━━━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=current_reply_markup)
            return

    # Check channel membership
    if CHANNEL_MEMBERSHIP_REQUIRED and not check_channel_membership(user_id):
        markup = types.InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS: markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_membership"))
        user_bot.send_message(message.chat.id, "⚠️ *Channel Membership Required!* 🔒", reply_markup=markup, parse_mode="Markdown")
        return

    # Check balance
    user = get_user(user_id)
    if user['balance'] < price:
        user_bot.send_message(message.chat.id, f"⚠️ **Insufficient Balance** 💰\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n💵 **Balance:** ₹{user['balance']}\n💎 **Required:** ₹{price}\n━━━━━━━━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=current_reply_markup)
        return

    # Show processing animation if not already provided
    if not process_msg:
        process_msg = user_bot.send_message(message.chat.id, f"🔄 **Processing {display_label} Search** 🚀\n\n{search_icon} **Query:** `{display_query_escaped}`\n\n▱▱▱▱▱▱▱▱▱▱ 0%", parse_mode="Markdown", reply_markup=current_reply_markup)
    else:
        # If process_msg was passed, update it to 0% with context (if needed)
        try:
            user_bot.edit_message_text(
                f"🔄 **Processing {display_label} Search** 🚀\n\n"
                f"{search_icon} **Query:** `{display_query_escaped}`\n\n"
                f"▱▱▱▱▱▱▱▱▱▱ 0%",
                message.chat.id,
                process_msg.message_id,
                parse_mode="Markdown"
            )
        except:
            pass

    # Process Search (Automated via Pyrogram or Profile Bot)
    try:
        if search_type == "phone":
            if is_incomplete_number(query):
                user_bot.delete_message(message.chat.id, process_msg.message_id)
                send_with_typing_effect(message.chat.id, f"```json\n[{{\"Request\": \"{query.replace('+', '')}\"}}]\n```")
                return
            
            query_id = randint(0, 9999999)
            report = generate_report(query, query_id)
            user_bot.delete_message(message.chat.id, process_msg.message_id)
            
            if not report:
                user_bot.send_message(message.chat.id, "❌ **Search Error** - Try again later.", reply_markup=current_reply_markup)
                return
                
            has_valid_data = any("no_results_found" not in str(r) for r in report)
            if has_valid_data:
                deduct_balance(user_id, price)
                markup = create_inline_keyboard(query_id, 0, len(report))
                send_with_typing_effect(message.chat.id, report[0], reply_markup=markup)
                user_bot.send_message(message.chat.id, f"✅ **Search Completed!**\n💸 **Deducted:** ₹{price}", parse_mode="Markdown", reply_markup=current_reply_markup)
            else:
                send_with_typing_effect(message.chat.id, report[0])
                user_bot.send_message(message.chat.id, "ℹ️ **No data found in records.**", reply_markup=current_reply_markup)

        elif search_type in ["username", "user_id"]:
            pyrogram_query = query if search_type == "username" else f"/tg{query}"
            # user_bot.delete_message(message.chat.id, process_msg.message_id) # REMOVED: Don't delete process bar
            # loading_msg = user_bot.send_message(message.chat.id, f"🔍 **Fetching data...** 🤖\n\n{search_icon} `{display_query_escaped}`", parse_mode="Markdown") # REMOVED: Extra message
            
            query_id = randint(0, 9999999)
            report = None
            global ACTIVE_USERNAME_PYROGRAM_INDEX, USERNAME_PYROGRAM_REQUEST_COUNTS
            try:
                report = generate_report(pyrogram_query, query_id, is_username_search=True)
            finally:
                USERNAME_PYROGRAM_REQUEST_COUNTS[ACTIVE_USERNAME_PYROGRAM_INDEX] = USERNAME_PYROGRAM_REQUEST_COUNTS.get(ACTIVE_USERNAME_PYROGRAM_INDEX, 0) + 1
                save_active_pyrogram_index()

            # user_bot.delete_message(message.chat.id, loading_msg.message_id) # REMOVED
            user_bot.delete_message(message.chat.id, process_msg.message_id) # Delete progress bar ONLY after search is done
            
            if not report:
                add_to_searched_no_data(original_query, search_type)
                user_bot.send_message(message.chat.id, "❌ **No Results Found**", reply_markup=current_reply_markup)
                return

            telegram_number = next((r for r in report if isinstance(r, str) and (r.startswith('+') or r.isdigit())), None)
            if telegram_number:
                deduct_balance(user_id, USERNAME_SEARCH_PRICE)
                res_json = f"```json\n[{{\"Username\": \"{display_query}\", \"Telephone\": \"{telegram_number.replace('+', '')}\"}}]\n```"
                btn_markup = types.InlineKeyboardMarkup()
                btn_markup.add(types.InlineKeyboardButton("🔍 Get Number Details", callback_data=f"search_number_{telegram_number}"))
                send_with_typing_effect(message.chat.id, res_json, reply_markup=btn_markup)
                user_bot.send_message(message.chat.id, f"✅ **Success!**\n💸 **Deducted:** ₹{USERNAME_SEARCH_PRICE}", reply_markup=current_reply_markup)
            else:
                add_to_searched_no_data(original_query, search_type)
                user_bot.send_message(message.chat.id, "❌ **No data available for this query.**", reply_markup=current_reply_markup)

        # REMOVED: Old profile lookup code path
        # The new profile lookup code is now handled in the updated perform_search function
        # This prevents double deduction of balance

    except Exception as e:
        print(f"Search Error: {e}")
        user_bot.send_message(message.chat.id, f"❌ **Error:** {str(e)}", reply_markup=current_reply_markup)

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("sel_username_") or call.data.startswith("sel_profile_"))
def handle_search_selection(call):
    user_id = call.from_user.id
    data = call.data
    
    class DummyMessage:
        def __init__(self, chat_id, user_id, text):
            self.chat = type("obj", (object,), {"id": chat_id})
            self.from_user = type("obj", (object,), {"id": user_id})
            self.text = text
            self.first_name = "User"

    if data == "sel_username_prompt":
        user_bot.answer_callback_query(call.id, "👤 Enter username to search")
        
        # 1. Clear other modes
        if user_id in profile_search_mode: del profile_search_mode[user_id]
        if user_id in user_id_search_mode: del user_id_search_mode[user_id]
        
        # 2. Set username search mode (EXACTLY like keyboard button)
        username_search_mode[user_id] = True
        
        # 3. Ask for username with EXACT same prompt as keyboard flow
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🏠 Main Menu"))
        
        user_bot.send_message(
            call.message.chat.id,
            "👤 **Username Search** 🔍\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **Please enter the Telegram username again:**\n"
            "   • Format: `@username` or `username`\n"
            "   • Example: `@elonmusk` or `elonmusk`\n\n"
            "💡 **Enter the username below:**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        query = data.replace("sel_profile_", "")
        user_bot.answer_callback_query(call.id, "🚀 Starting Profile Search...")
        dummy_msg = DummyMessage(call.message.chat.id, user_id, query)
        handle_profile_search_query(dummy_msg)

@user_bot.message_handler(func=lambda message: message.text == "💰 Check Balance")
def check_balance_handler(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    show_balance(message)



@user_bot.message_handler(func=lambda message: message.text == "➕ Add Balance")
def add_balance(message):
    # Check channel membership first
    if not require_channel_membership(message):
        return
    
    # Create inline keyboard with predefined amounts and custom option
    markup = types.InlineKeyboardMarkup()
    
    # Add predefined amount buttons in 2 columns
    markup.row(
        types.InlineKeyboardButton("₹12", callback_data="select_amount_12"),
        types.InlineKeyboardButton("₹20", callback_data="select_amount_20")
    )
    markup.row(
        types.InlineKeyboardButton("₹50", callback_data="select_amount_50"),
        types.InlineKeyboardButton("₹100", callback_data="select_amount_100")
    )
    markup.row(
        types.InlineKeyboardButton("₹500", callback_data="select_amount_500"),
        types.InlineKeyboardButton("₹1000", callback_data="select_amount_1000")
    )
    
    # Add custom amount button
    markup.add(types.InlineKeyboardButton("✏️ Enter Custom Amount", callback_data="custom_amount"))
    
    user_bot.send_message(
        message.chat.id,
        f"💳 **Add Balance** 🚀\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 **Select an amount below:**\n\n"
        f"✅ **Quick Select:** Choose a predefined amount\n"
        f"✏️ **Custom Amount:** Enter any amount you prefer\n\n"
        f"⚠️ **Minimum Recharge:** ₹{MINIMUM_RECHARGE}\n\n"
        f"💎 Your balance will be updated instantly after payment approval!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@user_bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 12)
def handle_potential_utr(message):
    user_id = message.from_user.id

    # Only process if user is actually waiting for UTR in deposit flow
    if user_id in user_states and user_states[user_id].get("waiting_utr"):
        process_utr_input(message)

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("select_amount_"))
def handle_predefined_amount(call):
    user_id = call.from_user.id
    amount = float(call.data.replace("select_amount_", ""))
    user_states[user_id] = {"amount": amount}
    
    user_bot.answer_callback_query(call.id, f"✅ Amount ₹{amount} selected!")
    
    process_msg = user_bot.send_message(call.message.chat.id, "🔄 **Generating payment QR...** 💳\n\n▰▰▰▰▰▱▱▱▱▱ 50%")
    time.sleep(0.8)
    user_bot.edit_message_text("✅ **QR Generated!** ✨\n\n▰▰▰▰▰▰▰▰▰▰ 100%", call.message.chat.id, process_msg.message_id)
    time.sleep(0.5)
    user_bot.delete_message(call.message.chat.id, process_msg.message_id)
    
    markup_qr = types.InlineKeyboardMarkup()
    
    # Add two buttons vertically: Redirect to Payment App and Payment Done
    markup_qr.add(types.InlineKeyboardButton("💳 Redirect to Payment App", url=f"https://searchanything11bot.vercel.app/?am={int(amount)}"))
    markup_qr.add(types.InlineKeyboardButton("✅ Payment Done", callback_data=f"enter_utr_{amount}"))
    
    # Send QR photo from file
    try:
        user_bot.send_photo(
            call.message.chat.id,
            open('attached_assets/IMG_20250904_120641_1761313497327.jpg', 'rb'),
            caption=f"💳 **Payment Instructions** 🚀\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💵 **Amount to Pay:** ₹{amount} 💎\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📱 **How to Pay:**\n\n"
                    f"**Option 1: Scan QR Code** 📸\n"
                    f"• Open your UPI app (Google Pay, PhonePe, etc.)\n"
                    f"• Scan the QR code above\n"
                    f"• Pay exactly ₹{amount}\n"
                    f"• Copy your **12-digit UTR number**\n\n"
                    f"**Option 2: Use Payment App** 💳\n"
                    f"• Click **Redirect to Payment App** button below\n"
                    f"• Complete payment directly in app\n"
                    f"• Copy your **12-digit UTR number**\n\n"
                    f"**After Payment:**\n"
                    f"• Click **Payment Done** button below\n"
                    f"• Send your 12-digit UTR",
            reply_markup=markup_qr,
            parse_mode="Markdown"
        )
        user_states[user_id]["waiting_utr"] = True
    except Exception as e:
        print(f"❌ QR Photo Error: {e}")
        # Fallback to text message with buttons
        user_bot.send_message(
            call.message.chat.id,
            f"💳 **Payment Instructions** 🚀\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Amount to Pay:** ₹{amount} 💎\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 **How to Pay:**\n\n"
            f"**Option 1: Scan QR Code** 📸\n"
            f"• Open your UPI app (Google Pay, PhonePe, etc.)\n"
            f"• Scan the QR code above\n"
            f"• Pay exactly ₹{amount}\n"
            f"• Copy your **12-digit UTR number**\n\n"
            f"**Option 2: Use Payment App** 💳\n"
            f"• Click **Redirect to Payment App** button below\n"
            f"• Complete payment directly in app\n"
            f"• Copy your **12-digit UTR number**\n\n"
            f"**After Payment:**\n"
            f"• Click **Payment Done** button below\n"
            f"• Send your 12-digit UTR",
            reply_markup=markup_qr,
            parse_mode="Markdown"
        )
        user_states[user_id]["waiting_utr"] = True

@user_bot.callback_query_handler(func=lambda call: call.data == "custom_amount")
def handle_custom_amount(call):
    user_bot.answer_callback_query(call.id, "✏️ Enter your custom amount")
    msg = user_bot.send_message(
        call.message.chat.id,
        f"💳 **Custom Amount** 💰\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 **Enter the amount to add:**\n\n"
        f"⚠️ **Minimum Recharge:** ₹{MINIMUM_RECHARGE} 💎\n\n"
        f"📝 **Type your amount and send:**\n"
        f"   • Example: 250 or 500\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    user_bot.register_next_step_handler(msg, process_recharge_amount)

@user_bot.message_handler(func=lambda message: message.text and len(message.text.strip()) > 0)
def handle_search_input(message):
    user_id = message.from_user.id
    query = message.text.strip()

    # Handle Instagram access key input
    if user_id in user_states and user_states[user_id].get("awaiting_instagram_access_key"):
        valid_key = "RXPRIME62"
        
        if query == valid_key:
            # Valid key - proceed to Instagram search
            user_states[user_id] = {"awaiting_instagram_username": True}
            
            user_bot.send_message(
                message.chat.id,
                "✅ **Access Key Verified!** 🎉\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔓 **Access Granted!**\n\n"
                "📝 **Now enter Instagram username:**\n"
                "   • Format: `username` or `@username`\n"
                "   • Example: `cristiano` or `@cristiano`\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return
        else:
            # Invalid key
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("👤 Contact Developer", url="https://t.me/hackingteamx"))
            markup.add(types.InlineKeyboardButton("🤖 Contact Bot", url="https://t.me/Hackingteamx_bot"))
            markup.add(types.InlineKeyboardButton("🔄 Try Again", callback_data="instagram_retry"))
            markup.add(types.InlineKeyboardButton("❌ Exit", callback_data="instagram_exit"))
            
            user_bot.send_message(
                message.chat.id,
                "❌ *Invalid Access Key!* 🚫\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 *The access key you entered is incorrect.*\n\n"
                "💰 *Want to buy access key?*\n"
                "👇 *Contact developer:*\n\n"
                "👤 *Developer:* @hackingteamx\n"
                "🤖 *Bot:* @Hackingteamx\\_bot\n\n"
                "💡 *Or try entering the key again!*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            return
    
    # Handle Instagram username search
    if user_id in user_states and user_states[user_id].get("awaiting_instagram_username"):
        # Normalize username
        username = query.lstrip('@').strip()
        
        if not username or len(username) < 1:
            user_bot.send_message(
                message.chat.id,
                "❌ **Invalid Username!**\n\n"
                "Please enter a valid Instagram username.\n\n"
                "📝 **Try again:**",
                parse_mode="Markdown"
            )
            return
        
        # Show searching animation
        process_msg = user_bot.send_message(
            message.chat.id,
            f"🔄 **Searching Instagram** 🅾\n\n"
            f"📝 **Username:** @{username}\n\n"
            f"▱▱▱▱▱▱▱▱▱▱ 0%",
            parse_mode="Markdown"
        )
        
        stages = [
            ("▰▰▱▱▱▱▱▱▱▱", "20%", "Connecting to Instagram..."),
            ("▰▰▰▰▱▱▱▱▱▱", "40%", "Fetching profile data..."),
            ("▰▰▰▰▰▰▱▱▱▱", "60%", "Analyzing information..."),
            ("▰▰▰▰▰▰▰▰▱▱", "80%", "Processing results..."),
            ("▰▰▰▰▰▰▰▰▰▰", "100%", "Finalizing...")
        ]
        
        for bar, percent, status in stages:
            try:
                user_bot.edit_message_text(
                    f"🔄 **Searching Instagram** 🅾\n\n"
                    f"📝 **Username:** @{username}\n"
                    f"📊 **Status:** {status}\n\n"
                    f"{bar} {percent}",
                    message.chat.id,
                    process_msg.message_id,
                    parse_mode="Markdown"
                )
                time.sleep(0.5)
            except:
                pass
        
        user_bot.delete_message(message.chat.id, process_msg.message_id)
        
        # Show no results found
        user_bot.send_message(
            message.chat.id,
            "❌ **No Results Found** 😔\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Instagram Username:** @{username}\n\n"
            "⚠️ **No phone number data available for this Instagram account.**\n\n"
            "**Possible Reasons:**\n"
            "├─ Account is private\n"
            "├─ No phone number linked\n"
            "├─ Account doesn't exist\n"
            "└─ Data not in database\n\n"
            "💡 **Try another username!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        
        # Keep user in search mode
        return

    # If it's a username (starts with @) AND user is NOT already in a specific mode, show choice buttons
    if is_username(query) and user_id not in username_search_mode and user_id not in user_id_search_mode and user_id not in profile_search_mode:
        clean_username = query.lstrip("@")
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("👤 Search Username", callback_data="sel_username_prompt")
        btn2 = types.InlineKeyboardButton("🔍 Profile Lookup", callback_data=f"sel_profile_{clean_username}")
        markup.add(types.KeyboardButton("🆔 SEARCH BY USER ID"), types.KeyboardButton("🏠 Main Menu"))

        current_reply_markup = show_main_menu(user_id, return_markup=True)

        user_bot.send_message(
            message.chat.id,
            f"✨ **Username Detected:** `@{clean_username}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **Select Search Type:**\n\n"
            f"👤 **Username Search:** Get phone number\n"
            f"🔍 **Profile Lookup:** Get group history & more\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        user_bot.send_message(message.chat.id, "💡 Choose a search type above or use the menu below:", reply_markup=current_reply_markup)
        return

    # Store original query for username/user_id searches
    original_query = query
    search_type = None

    # ===== CONTEXT-AWARE SEARCH LOGIC =====
    # Priority 1: Check user's CURRENT MODE to determine search type
    
    # 🔴 If user is in PROFILE SEARCH MODE → Profile lookup (regardless of input format)
    if user_id in profile_search_mode:
        if is_username(query) or (query.isdigit() and len(query) > 5):
            search_type = "profile_lookup"
            price = PROFILE_SEARCH_PRICE
            search_icon = "👤"
            search_label = "Profile"
            original_query = query.lstrip('@') if is_username(query) else query
            # Don't clear profile_search_mode yet - keep user in profile mode for next search
        else:
            user_bot.send_message(
                message.chat.id,
                "❌ **Invalid Query** 🚫\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📝 **Profile lookup requires:**\n"
                "• Username (e.g., @username)\n"
                "• OR User ID (digits)\n\n"
                "💡 **Try again with valid input!**",
                parse_mode="Markdown"
            )
            return
    
    elif user_id in username_search_mode:
        if is_username(query):
            # Check if username search is enabled
            if not USERNAME_SEARCH_ENABLED:
                user_bot.send_message(
                    message.chat.id,
                    "⚠️ **Username Search Disabled** 🚫\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Username search is currently **unavailable**.\n\n"
                    "📞 **You can still use:**\n"
                    "   • Phone Number Search ✅\n\n"
                    "💡 **Contact support** for more info: @hackingteamx\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
                del username_search_mode[user_id]
                return
            
            # Use ACTIVE_USERNAME_PYROGRAM_INDEX from config instead of always resetting
            load_active_pyrogram_index()
            
            search_type = "username"
            price = USERNAME_SEARCH_PRICE
            search_icon = "👤"
            search_label = "Username"
            original_query = query.lstrip('@')
            del username_search_mode[user_id]  # Clear mode after assignment
        else:
            user_bot.send_message(
                message.chat.id,
                "❌ **Invalid Format** 🚫\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📝 **Username search requires:**\n"
                "Format: @username\n"
                "Example: @elonmusk\n\n"
                "💡 **Please enter a valid username!**",
                parse_mode="Markdown"
            )
            return
    
    # 🔴 If user is in USER ID SEARCH MODE → User ID search
    elif user_id in user_id_search_mode and query.isdigit():
        # Check if username search is enabled (user ID search uses same toggle)
        if not USERNAME_SEARCH_ENABLED:
            if user_id in user_id_search_mode:
                del user_id_search_mode[user_id]
            user_bot.send_message(
                message.chat.id,
                "⚠️ **User ID Search Disabled** 🚫\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "User ID search is currently **unavailable**.\n\n"
                "📞 **You can still use:**\n"
                "   • Phone Number Search ✅\n\n"
                "💡 **Contact support** for more info: @hackingteamx\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return
        
        search_type = "user_id"
        price = USERNAME_SEARCH_PRICE
        search_icon = "🆔"
        search_label = "User ID"
        original_query = query
        del user_id_search_mode[user_id]  # Clear mode after assignment

    # 🔴 If user is in USER ID SEARCH MODE but entered non-digits → error
    elif user_id in user_id_search_mode and not query.isdigit():
        user_bot.send_message(
            message.chat.id,
            "❌ **Invalid User ID Format** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **User ID search requires digits only**\n"
            "Example: 123456789\n\n"
            "💡 **Please enter a valid User ID!**",
            parse_mode="Markdown"
        )
        del user_id_search_mode[user_id]
        return
    
    # 🔴 If HOME MODE (not in any mode) → Check input format
    elif user_id not in profile_userid_search_mode:
        # HOME TAB: Determine by input format
        if is_username(query):
            # Check if username search is enabled
            if not USERNAME_SEARCH_ENABLED:
                user_bot.send_message(
                    message.chat.id,
                    "⚠️ **Username Search Disabled** 🚫\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Username search is currently **unavailable**.\n\n"
                    "📞 **You can still use:**\n"
                    "   • Phone Number Search ✅\n\n"
                    "💡 **Contact support** for more info: @hackingteamx\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
                return
            
            search_type = "username"
            price = USERNAME_SEARCH_PRICE
            search_icon = "👤"
            search_label = "Username"
            original_query = query.lstrip('@')
        
        elif is_phone_number(query):
            formatted = format_indian_number(query)
            if formatted:
                search_type = "phone"
                price = NUMBER_SEARCH_PRICE
                search_icon = "📞"
                search_label = "Phone Number"
                query = formatted
                original_query = formatted
            else:
                return
        else:
            # Invalid input from home - ignore silently
            return
    else:
        # Invalid input or wrong mode - ignore silently
        return

    # Define display variables before any checks
    if search_type == "username":
        display_label = "Username"
        display_query = f"@{original_query}"
        display_query_escaped = display_query.replace("_", "\\_")
    elif search_type == "user_id":
        display_label = "User ID"
        display_query = original_query
        display_query_escaped = display_query
    elif search_type == "profile_lookup":
        display_label = "Profile"
        display_query = f"@{original_query}" if not original_query.isdigit() else original_query
        display_query_escaped = display_query.replace("_", "\\_") if "@" in display_query else display_query
    else:  # phone
        display_label = "Phone Number"
        display_query = query
        display_query_escaped = display_query

    # CRITICAL: Check if already searched with no data BEFORE any processing
    if search_type in ["username", "user_id"]:
        # For username, check without @ symbol (normalize)
        check_query = query.lstrip('@').lower() if search_type == "username" else query

        if is_already_searched_no_data(check_query, search_type):
            user_bot.send_message(
                message.chat.id,
                f"⚠️ **Search Not Allowed** 🚫\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{search_icon} **{display_label}:** `{display_query_escaped}`\n\n"
                f"❌ **This {display_label.lower()} has no data in our records.**\n\n"
                f"🚨 **WARNING:** Don't search this {display_label.lower()} again, otherwise you will be charged!\n\n"
                f"💰 **Your balance is safe** - This search was blocked automatically. 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']} 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💡 **Please search a different {display_label.lower()}** ⚡",
                parse_mode="Markdown"
            )

            # Disable User ID search mode
            if user_id in user_id_search_mode:
                del user_id_search_mode[user_id]

            return

    # Check channel membership before allowing search (applies to all search types) - only if enabled
    if CHANNEL_MEMBERSHIP_REQUIRED and not check_channel_membership(user_id):
        markup = types.InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined", callback_data="check_membership"))

        user_bot.send_message(
            message.chat.id,
            "⚠️ *Channel Membership Required!* 🔒\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ *You must join our channels to search!*\n\n"
            "📢 *Please join both channels below:*\n"
            "✅ Then click 'I Joined' to verify\n\n"
            "🎁 *Bonus:* Get FREE ₹5 after joining! 💎\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    user = get_user(user_id)

    # Check balance
    if user['balance'] < price:
        user_bot.send_message(
            message.chat.id,
            f"⚠️ **Insufficient Balance** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Current Balance:** ₹{user['balance']}\n"
            f"💎 **Required Amount:** ₹{price}\n"
            f"❌ **Need:** ₹{price - user['balance']} more\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚀 **Please add balance to continue!** ⚡",
            parse_mode="Markdown"
        )

        # Send appropriate voice based on search type
        try:
            if search_type == "phone":
                voice_file = open('attached_assets/insufficienbalancewhennumbersearch_1762169792085.mp3', 'rb')
            else:  # username
                voice_file = open('attached_assets/insufficientbalancewhenusernamesearch_1762169792094.mp3', 'rb')
            user_bot.send_voice(message.chat.id, voice_file)
            voice_file.close()
        except Exception as e:
            print(f"Error sending voice: {e}")

        return

    # Determine which search type and bot to use
    # If user is in username_search_mode -> use username search (@Dfjyt_bot)
    # If user is in profile_search_mode -> use profile search (@pofliechecker17_bot)
    is_profile_search = user_id in profile_search_mode and search_type == "username"
    
    # Show processing animation
    process_msg = user_bot.send_message(
        message.chat.id,
        f"🔄 **Processing {display_label} Search** 🚀\n\n"
        f"{search_icon} **Query:** `{display_query_escaped}`\n\n"
        f"▱▱▱▱▱▱▱▱▱▱ 0%",
        parse_mode="Markdown"
    )

    stages = [
        ("▰▰▱▱▱▱▱▱▱▱", "20%", "Validating query... 🔍"),
        ("▰▰▰▰▱▱▱▱▱▱", "40%", "Connecting to database... 🌐"),
        ("▰▰▰▰▰▰▱▱▱▱", "60%", "Searching records... 📊"),
        ("▰▰▰▰▰▰▰▰▱▱", "80%", "Compiling results... 📋"),
        ("▰▰▰▰▰▰▰▰▰▰", "100%", "Finalizing... ✨")
    ]

    for bar, percent, status in stages:
        try:
            user_bot.edit_message_text(
                f"🔄 **Processing {display_label} Search** 🚀\n\n"
                f"{search_icon} **Query:** `{display_query_escaped}`\n"
                f"📊 **Status:** {status}\n\n"
                f"{bar} {percent}",
                message.chat.id,
                process_msg.message_id,
                parse_mode="Markdown"
            )
            time.sleep(0.4)
        except:
            pass

    # Process based on search type
    if search_type == "phone":
        # Check if number already has incomplete data
        if is_incomplete_number(query):
            user_bot.delete_message(message.chat.id, process_msg.message_id)
            
            # Create JSON format for incomplete number
            incomplete_json = [
                [
                    {
                        "Request": query.replace('+', '')
                    }
                ]
            ]
            json_str = json.dumps(incomplete_json, indent=2, ensure_ascii=False)
            json_result = f"```json\n{json_str}\n```"
            
            # Send JSON result with typing effect
            send_with_typing_effect(message.chat.id, json_result)
            
            user_bot.send_message(
                message.chat.id,
                f"⚠️ **Search Not Allowed** 🚫\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📞 **Number:** `{display_query_escaped}`\n\n"
                f"❌ **This number has incomplete data in our records.**\n\n"
                f"🚨 **WARNING:** Don't search this number again, otherwise you will be charged!\n\n"
                f"💰 **Your balance is safe** - This search was blocked automatically. 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']} 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💡 **Please search a different number** ⚡",
                parse_mode="Markdown"
            )
            return
        
        query_id = randint(0, 9999999)
        report = generate_report(query, query_id)

        user_bot.delete_message(message.chat.id, process_msg.message_id)

        if report is None or not isinstance(report, list) or len(report) == 0:
            # Return JSON format for error
            no_result_json = [{
                "status": "error",
                "message": "Unable to retrieve data at this moment. Please try again later.",
                "number": query,
                "owned_and_developed_by": "@hackingteamx"
            }]
            json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
            json_result = f"```json\n{json_str}\n```"

            user_bot.send_message(
                message.chat.id,
                json_result,
                parse_mode="Markdown"
            )
            return

        # Check if valid data found - ONLY deduct balance if "no_results_found" is NOT in the response
        has_valid_data = False
        for r in report:
            # Check if 'no_results_found' is NOT in the JSON string (means valid data was found and HiTeckGroop header was present)
            if "no_results_found" not in str(r):
                has_valid_data = True
                break

        if not has_valid_data:
            # Check if this is truly incomplete (only has "Request" field)
            is_truly_incomplete = False
            try:
                # Parse the JSON from the report
                json_text = report[0]
                if json_text.startswith("```json\n"):
                    json_content = json_text[8:-4]
                else:
                    json_content = json_text
                
                parsed_data = json.loads(json_content)
                # Check if it only contains "Request" field
                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    if isinstance(parsed_data[0], list) and len(parsed_data[0]) > 0:
                        first_entry = parsed_data[0][0]
                        if isinstance(first_entry, dict) and "Request" in first_entry and len(first_entry) == 1:
                            is_truly_incomplete = True
            except:
                pass
            
            if is_truly_incomplete:
                # Save this number to prevent future searches
                add_to_incomplete_numbers(query)
                print(f"📝 Saved incomplete number: {query}")
            
            # Send the JSON result without deducting balance with typing effect
            send_with_typing_effect(message.chat.id, report[0])

            # Send message that full data not available, so no charge
            if is_truly_incomplete:
                user_bot.send_message(
                    message.chat.id,
                    f"ℹ️ **Incomplete Data Found** 📋\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ **Full data not available in records**\n\n"
                    f"🚨 **WARNING:** Don't search this number again, otherwise you will be charged!\n\n"
                    f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                    f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
            else:
                user_bot.send_message(
                    message.chat.id,
                    f"ℹ️ **Incomplete Data Found** 📋\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ **Full data not available in records**\n\n"
                    f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                    f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
            return

        # Only deduct balance if "The name of the father" field is found
        deduct_balance(user_id, price)

        markup = create_inline_keyboard(query_id, 0, len(report))

        # Send JSON formatted result with typing effect
        send_with_typing_effect(message.chat.id, report[0], reply_markup=markup)

        user_bot.send_message(
            message.chat.id,
            f"✅ **Search Completed Successfully!** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💸 **Deducted:** ₹{price}\n"
            f"💰 **Remaining Balance:** ₹{get_user(user_id)['balance']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )

    elif search_type == "username" or search_type == "user_id":
        # Prepare pyrogram query
        if search_type == "username":
            pyrogram_query = query  # Already without @
        else:  # user_id
            # Add /tg prefix for User ID searches
            pyrogram_query = f"/tg{query}"
            print(f"🔄 User ID search - Added prefix: {pyrogram_query}")

        user_bot.delete_message(message.chat.id, process_msg.message_id)

        # Automated username/user ID search
        loading_msg = user_bot.send_message(
            message.chat.id,
            f"🔍 **Automated Search Started** 🤖\n\n"
            f"{search_icon} **{display_label}:** {display_query_escaped}\n\n"
            f"⏳ **Fetching data from Telegram...**\n"
            f"🔄 **Processing... Please wait** ⚡",
            parse_mode="Markdown"
        )

        # Track request count
        global ACTIVE_USERNAME_PYROGRAM_INDEX, USERNAME_PYROGRAM_REQUEST_COUNTS
        
        # Generate report using automated Pyrogram with correct query format
        # Wrap in try/finally to ensure counter increments even on exceptions
        query_id = randint(0, 9999999)
        report = None
        
        try:
            report = generate_report(pyrogram_query, query_id, is_username_search=True)
        finally:
            # Increment request count ALWAYS (even on exceptions/failures)
            if ACTIVE_USERNAME_PYROGRAM_INDEX not in USERNAME_PYROGRAM_REQUEST_COUNTS:
                USERNAME_PYROGRAM_REQUEST_COUNTS[ACTIVE_USERNAME_PYROGRAM_INDEX] = 0
            
            USERNAME_PYROGRAM_REQUEST_COUNTS[ACTIVE_USERNAME_PYROGRAM_INDEX] += 1
            current_count = USERNAME_PYROGRAM_REQUEST_COUNTS[ACTIVE_USERNAME_PYROGRAM_INDEX]
            
            print(f"📊 Account #{ACTIVE_USERNAME_PYROGRAM_INDEX + 1}: Request {current_count} completed")
            
            # Check if limit reached for current account (rotate AFTER completing the request)
            should_rotate = False
            if ACTIVE_USERNAME_PYROGRAM_INDEX in USERNAME_PYROGRAM_LIMITS:
                limit = USERNAME_PYROGRAM_LIMITS[ACTIVE_USERNAME_PYROGRAM_INDEX]
                
                if current_count >= limit:
                    should_rotate = True
                    # Find next available account
                    configured_accounts = [i for i, config in enumerate(USERNAME_SEARCH_PYROGRAMS) if config["api_id"] != 0 and config["api_hash"]]
                    current_idx_in_list = configured_accounts.index(ACTIVE_USERNAME_PYROGRAM_INDEX)
                    
                    # Rotate to next account
                    if current_idx_in_list + 1 < len(configured_accounts):
                        ACTIVE_USERNAME_PYROGRAM_INDEX = configured_accounts[current_idx_in_list + 1]
                    else:
                        # Wrap around to first account
                        ACTIVE_USERNAME_PYROGRAM_INDEX = configured_accounts[0]
                    
                    # Reset count for new account if not exists
                    if ACTIVE_USERNAME_PYROGRAM_INDEX not in USERNAME_PYROGRAM_REQUEST_COUNTS:
                        USERNAME_PYROGRAM_REQUEST_COUNTS[ACTIVE_USERNAME_PYROGRAM_INDEX] = 0
                    
                    print(f"✅ Auto-rotated to Account #{ACTIVE_USERNAME_PYROGRAM_INDEX + 1} (limit of {limit} reached)")
            
            # ALWAYS save updated config (whether rotated or not) to persist counter
            save_active_pyrogram_index()

        user_bot.delete_message(message.chat.id, loading_msg.message_id)

        # Check if report has data
        if report is None or not isinstance(report, list) or len(report) == 0:
            # Add to searched no data list - SAVE IN FILE
            print(f"📝 Saving no-data entry (empty report): {search_type}_{original_query}")
            add_to_searched_no_data(original_query, search_type)

            # Create JSON format for no results found
            if search_type == "username":
                no_result_json = [
                    [
                        {
                            "Username": f"@{original_query}"
                        },
                        {
                            "Status": "No Results Found"
                        },
                        {
                            "Message": "No data available for this username"
                        }
                    ]
                ]
            else:  # user_id
                no_result_json = [
                    [
                        {
                            "User ID": original_query
                        },
                        {
                            "Status": "No Results Found"
                        },
                        {
                            "Message": "No data available for this user ID"
                        }
                    ]
                ]
            
            json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
            json_result = f"```json\n{json_str}\n```"

            # Send JSON result with typing effect
            send_with_typing_effect(message.chat.id, json_result)

            # Send balance safe confirmation with new format
            user_bot.send_message(
                message.chat.id,
                f"ℹ️ **NO Data Found** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Full data not available in records**\n\n"
                f"🚨 **WARNING:** Don't search this {display_label.lower()} again, otherwise you will be charged!\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return

        # Check if valid data found
        # report already contains the extracted phone number from generate_report
        has_valid_data = False
        telegram_number = None

        for r in report:
            if isinstance(r, str) and "no_results_found" not in r.lower():
                # Report already has extracted phone number, just validate it
                if r and (r.startswith('+') or r.isdigit()):
                    telegram_number = r
                    has_valid_data = True
                    break

        if not has_valid_data or not telegram_number:
            # SAVE TO NO-DATA FILE - Use normalized query (without @, lowercase)
            save_query = original_query  # Already normalized (without @)
            print(f"📝 Saving no-data entry: {search_type}_{save_query}")
            add_to_searched_no_data(save_query, search_type)

            # Create JSON format for no results found
            if search_type == "username":
                no_result_json = [
                    [
                        {
                            "Username": f"@{original_query}"
                        },
                        {
                            "Status": "No Results Found"
                        },
                        {
                            "Message": "No data available for this username"
                        }
                    ]
                ]
            else:  # user_id
                no_result_json = [
                    [
                        {
                            "User ID": original_query
                        },
                        {
                            "Status": "No Results Found"
                        },
                        {
                            "Message": "No data available for this user ID"
                        }
                    ]
                ]
            
            json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
            json_result = f"```json\n{json_str}\n```"

            # Send JSON result with typing effect
            send_with_typing_effect(message.chat.id, json_result)

            # Send balance safe confirmation with new format
            user_bot.send_message(
                message.chat.id,
                f"ℹ️ **NO Data Found** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Full data not available in records**\n\n"
                f"🚨 **WARNING:** Don't search this {display_label.lower()} again, otherwise you will be charged!\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )

            return

        # Valid result found - deduct balance and show formatted result
        deduct_balance(user_id, USERNAME_SEARCH_PRICE)

        # Create JSON format for username/user_id search result
        if search_type == "username":
            result_json = [
                [
                    {
                        "Username": f"@{original_query}"
                    },
                    {
                        "Telephone": telegram_number.replace('+', '')
                    }
                ]
            ]
        else:  # user_id
            result_json = [
                [
                    {
                        "User ID": original_query
                    },
                    {
                        "Telephone": telegram_number.replace('+', '')
                    }
                ]
            ]
        
        json_str = json.dumps(result_json, indent=2, ensure_ascii=False)
        json_result = f"```json\n{json_str}\n```"

        # Show result with button to get number details
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔍 Get Number Details", callback_data=f"search_number_{telegram_number}"))

        # Send JSON result with typing effect
        send_with_typing_effect(message.chat.id, json_result, reply_markup=markup)

        # Send deduction confirmation message with two buttons
        result_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("🆔 LOOKUP BY USER ID")
        btn2 = types.KeyboardButton("🏠 Main Menu")
        result_markup.add(types.KeyboardButton("🆔 LOOKUP BY USER ID"), types.KeyboardButton("🏠 Main Menu"))
        
        user_bot.send_message(
            message.chat.id,
            f"✅ <b>Search Completed Successfully!</b> 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💸 <b>Deducted:</b> {get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH'])}\n"
            f"💰 <b>Remaining Balance:</b> ₹{get_user(user_id)['balance']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="HTML",
            reply_markup=result_markup
        )

        return
    
    elif search_type == "profile_lookup":
        """Handle profile lookup search (username or user ID)"""
        # Determine query for profile lookup
        if is_username(original_query):
            lookup_query = original_query
        else:
            lookup_query = original_query
        
        # Check if profile/username is in blocked list
        if is_lookup_blocked(lookup_query, 'profile'):
            user_bot.delete_message(message.chat.id, process_msg.message_id)
            user_bot.send_message(
                message.chat.id,
                f"🚫 **Profile Lookup Blocked** 🔒\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⛔ **This profile cannot be looked up.**\n\n"
                f"📋 **Query:** {display_query}\n\n"
                f"💡 **Please search for another profile.**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            # Keep user in profile_search_mode for next search
            return
        
        user_bot.delete_message(message.chat.id, process_msg.message_id)
        
        # Send loading message
        loading_msg = user_bot.send_message(
            message.chat.id,
            f"🔍 **Profile Lookup Started** 🤖\n\n"
            f"👤 **Query:** {display_query_escaped}\n\n"
            f"⏳ **Fetching complete profile data...**\n"
            f"🔄 **Processing... Please wait** ⚡",
            parse_mode="Markdown"
        )
        
        try:
            # Call async profile lookup coroutine
            future = asyncio.run_coroutine_threadsafe(
                profile_userid_search_coroutine(lookup_query),
                loop
            )
            result = future.result(timeout=60)  # Wait up to 60 seconds
            
            user_bot.delete_message(message.chat.id, loading_msg.message_id)
            
            if result is None:
                # No data found
                user_bot.send_message(
                    message.chat.id,
                    f"ℹ️ **Profile Not Found** 😔\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **Query:** {display_query_escaped}\n\n"
                    f"⚠️ **No profile data available in records**\n\n"
                    f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                    f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
                # Keep user in profile_search_mode for next search
                return
            
            # Result found - check if it has groups data
            has_groups_data = False
            if isinstance(result, dict):
                has_groups_data = result.get('has_groups_data', False)
                profile_data = result.get('profile_text', '')
                groups_data = result.get('groups_formatted', '')
                html_file = result.get('html_file', None)
                
                # Only deduct balance if groups data was retrieved
                if has_groups_data:
                    deduct_balance(user_id, price)
                    charge_applied = True
                else:
                    charge_applied = False
                
                # Send profile data
                if profile_data:
                    send_with_typing_effect(message.chat.id, profile_data)
                
                # Send groups data
                if groups_data:
                    send_with_typing_effect(message.chat.id, groups_data)
                
                # Send HTML file if available
                if html_file:
                    try:
                        with open(html_file, 'rb') as file:
                            user_bot.send_document(
                                message.chat.id,
                                file,
                                caption="📄 **Profile HTML Export** 💾"
                            )
                    except:
                        pass
                
                # Send completion message
                if charge_applied:
                    user_bot.send_message(
                        message.chat.id,
                        f"✅ **Profile Lookup Completed!** 🎉\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💸 **Deducted:** ₹{price}\n"
                        f"💰 **Remaining Balance:** ₹{get_user(user_id)['balance']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        parse_mode="Markdown"
                    )
                else:
                    user_bot.send_message(
                        message.chat.id,
                        f"✅ **Profile Data Retrieved!** 📊\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 **Groups data not available in this profile**\n\n"
                        f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                        f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        parse_mode="Markdown"
                    )
        
        except asyncio.TimeoutError:
            user_bot.delete_message(message.chat.id, loading_msg.message_id)
            user_bot.send_message(
                message.chat.id,
                f"⏱️ **Search Timeout** ⌛\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ **Profile lookup took too long**\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        except Exception as e:
            user_bot.delete_message(message.chat.id, loading_msg.message_id)
            print(f"Error in profile lookup: {e}")
            user_bot.send_message(
                message.chat.id,
                f"❌ **Profile Lookup Error** 🚫\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"An error occurred during profile lookup\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        
        # **IMPORTANT: Keep user in profile_search_mode for next search**
        # Do NOT clear the mode - user should stay in profile lookup
        return

def show_profile(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    loading_msg = user_bot.send_message(message.chat.id, "🔄 **Loading profile...** 📊\n\n▰▰▰▰▰▱▱▱▱▱ 50%")
    time.sleep(0.5)
    user_bot.edit_message_text("✅ **Profile Loaded!** ✨\n\n▰▰▰▰▰▰▰▰▰▰ 100%", message.chat.id, loading_msg.message_id)
    time.sleep(0.5)
    user_bot.delete_message(message.chat.id, loading_msg.message_id)

    response = f"👤 **Your Profile** 💎\n\n"
    response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    response += f"🆔 **User ID:** `{user_id}`\n"
    response += f"👤 **Name:** {message.from_user.first_name}\n"
    response += f"💰 **Balance:** ₹{user['balance']} 💵\n"
    response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━"

    user_bot.send_message(message.chat.id, response, parse_mode="Markdown")

def show_balance(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    balance_msg = user_bot.send_message(message.chat.id, "🔄 **Fetching balance...** 💰\n\n▰▰▰▰▰▱▱▱▱▱ 50%")
    time.sleep(0.5)
    user_bot.edit_message_text("✅ **Balance Retrieved!** ✨\n\n▰▰▰▰▰▰▰▰▰▰ 100%", message.chat.id, balance_msg.message_id)
    time.sleep(0.5)
    user_bot.delete_message(message.chat.id, balance_msg.message_id)

    user_bot.send_message(
        message.chat.id,
        f"💰 **Your Balance** 💎\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"👤 **Name:** {message.from_user.first_name}\n"
        f"💵 **Available Balance:** ₹{user['balance']} 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )



@admin_bot.message_handler(func=lambda message: message.text == "🎟️ CREATE PROMO CODE")
def create_promo_code(message):
    msg = admin_bot.send_message(message.chat.id, "🎟️ **Enter promo code name** (e.g., WELCOME100):")
    admin_bot.register_next_step_handler(msg, process_promo_name)

def process_promo_name(message):
    promo_name = message.text.strip().upper()

    with promo_codes_lock:
        promo_codes = load_promo_codes()
        if promo_name in promo_codes:
            admin_bot.send_message(message.chat.id, "❌ **This promo code already exists!**")
            return

    msg = admin_bot.send_message(message.chat.id, f"💰 **Enter amount for promo code '{promo_name}':**")
    admin_bot.register_next_step_handler(msg, process_promo_amount, promo_name)

def process_promo_amount(message, promo_name):
    try:
        amount = float(message.text.strip())
        msg = admin_bot.send_message(message.chat.id, f"👥 **Enter maximum number of users who can claim '{promo_name}':**")
        admin_bot.register_next_step_handler(msg, process_promo_max_uses, promo_name, amount)
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid amount!** Please try again.")

def process_promo_max_uses(message, promo_name, amount):
    try:
        max_uses = int(message.text.strip())

        # Save promo code
        with promo_codes_lock:
            promo_codes = load_promo_codes()
            promo_codes[promo_name] = {
                "amount": amount,
                "max_uses": max_uses,
                "used_count": 0,
                "used_by": []
            }
            save_promo_codes(promo_codes)

        admin_bot.send_message(
            message.chat.id,
            f"✅ **Promo Code Created!** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎟️ **Code:** `{promo_name}`\n"
            f"💰 **Amount:** ₹{amount}\n"
            f"👥 **Max Uses:** {max_uses}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 **Share this code with users!**",
            parse_mode="Markdown"
        )
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid number!** Please try again.")


def process_recharge_amount(message):
    try:
        # Clean the input and convert to float
        amount_text = message.text.strip()
        amount = float(amount_text)

        if amount < MINIMUM_RECHARGE:
            user_bot.send_message(
                message.chat.id,
                f"❌ **Invalid Amount** 💰\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Minimum recharge:** ₹{MINIMUM_RECHARGE}\n\n"
                f"🔄 **Please try again with valid amount** ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return

        user_states[message.from_user.id] = {"amount": amount}

        process_msg = user_bot.send_message(message.chat.id, "🔄 **Generating payment QR...** 💳\n\n▰▰▰▰▰▱▱▱▱▱ 50%")
        time.sleep(0.8)
        user_bot.edit_message_text("✅ **QR Generated!** ✨\n\n▰▰▰▰▰▰▰▰▰▰ 100%", message.chat.id, process_msg.message_id)
        time.sleep(0.5)
        user_bot.delete_message(message.chat.id, process_msg.message_id)

        markup_qr = types.InlineKeyboardMarkup()
        
        # Add two buttons vertically: Redirect to Payment App and Payment Done
        markup_qr.add(types.InlineKeyboardButton("💳 Redirect to Payment App", url=f"https://searchanything11bot.vercel.app/?am={int(amount)}"))
        markup_qr.add(types.InlineKeyboardButton("✅ Payment Done", callback_data=f"enter_utr_{amount}"))

        # Send QR photo from file
        try:
            user_bot.send_photo(
                message.chat.id,
                open('attached_assets/IMG_20250904_120641_1761313497327.jpg', 'rb'),
                caption=f"💳 **Payment Instructions** 🚀\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💵 **Amount to Pay:** ₹{amount} 💎\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📱 **How to Pay:**\n\n"
                        f"**Option 1: Scan QR Code** 📸\n"
                        f"• Open your UPI app (Google Pay, PhonePe, etc.)\n"
                        f"• Scan the QR code above\n"
                        f"• Pay exactly ₹{amount}\n"
                        f"• Copy your **12-digit UTR number**\n\n"
                        f"**Option 2: Use Payment App** 💳\n"
                        f"• Click **Redirect to Payment App** button below\n"
                        f"• Complete payment directly in app\n"
                        f"• Copy your **12-digit UTR number**\n\n"
                        f"**After Payment:**\n"
                        f"• Click **Payment Done** button below\n"
                        f"• Send your 12-digit UTR",
                reply_markup=markup_qr,
                parse_mode="Markdown"
            )
            user_states[message.from_user.id]["waiting_utr"] = True
        except Exception as e:
            print(f"❌ Custom QR error: {e}")
            # Fallback to text message
            user_bot.send_message(
                message.chat.id,
                f"💳 **Payment Instructions** 🚀\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💵 **Amount to Pay:** ₹{amount} 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📱 **How to Pay:**\n\n"
                f"**Option 1: Scan QR Code** 📸\n"
                f"• Open your UPI app (Google Pay, PhonePe, etc.)\n"
                f"• Scan the QR code above\n"
                f"• Pay exactly ₹{amount}\n"
                f"• Copy your **12-digit UTR number**\n\n"
                f"**Option 2: Use Payment App** 💳\n"
                f"• Click **Redirect to Payment App** button below\n"
                f"• Complete payment directly in app\n"
                f"• Copy your **12-digit UTR number**\n\n"
                f"**After Payment:**\n"
                f"• Click **Payment Done** button below\n"
                f"• Send your 12-digit UTR",
                reply_markup=markup_qr,
                parse_mode="Markdown"
            )
            user_states[message.from_user.id]["waiting_utr"] = True

    except ValueError:
        user_bot.send_message(
            message.chat.id,
            "❌ **Invalid Amount!** 💰\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ Please enter a valid **numeric** value.\n\n"
            "📝 **Example:** 50 or 100\n\n"
            "🔄 **Try again** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error in recharge: {e}")
        user_bot.send_message(
            message.chat.id,
            "❌ **Something went wrong!**\n\n"
            "Please try again or contact support. 🛠️",
            parse_mode="Markdown"
        )

def process_utr_input(message):
    user_id = message.from_user.id
    utr = message.text.strip()

    if user_id not in user_states or not user_states[user_id].get("waiting_utr"):
        return

    if not utr.isdigit() or len(utr) != 12:
        user_bot.send_message(
            message.chat.id,
            "❌ **Invalid UTR Number** 🔢\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ UTR must be exactly **12 digits**.\n\n"
            "📝 **Please send valid 12-digit UTR** ⚡\n\n"
            "💡 You can continue using other features! 🚀\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return

    amount = user_states[user_id]["amount"]
    
    # Increment attempt counter
    user_states[user_id]["utr_attempts"] = user_states[user_id].get("utr_attempts", 0) + 1
    attempt = user_states[user_id]["utr_attempts"]

    verify_msg = user_bot.send_message(
        message.chat.id,
        "🔄 **Verifying payment...** 💳\n\n▱▱▱▱▱▱▱▱▱▱ 0%"
    )

    stages = [
        ("▰▰▰▱▱▱▱▱▱▱", "30%"),
        ("▰▰▰▰▰▰▱▱▱▱", "60%"),
        ("▰▰▰▰▰▰▰▰▱▱", "90%"),
        ("▰▰▰▰▰▰▰▰▰▰", "100%")
    ]

    for bar, percent in stages:
        try:
            user_bot.edit_message_text(
                f"🔄 **Verifying payment...** 💳\n\n{bar} {percent}",
                message.chat.id,
                verify_msg.message_id
            )
            time.sleep(0.5)
        except:
            pass

    user_bot.delete_message(message.chat.id, verify_msg.message_id)

    # Send UTR to admin for approval
    review_msg = user_bot.send_message(
        message.chat.id,
        "⏳ **Payment Under Review** 🔍\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Your payment is being **verified** by our team.\n\n"
        "💰 **Payment will be added in maximum 20 minutes** ⏱️\n"
        "❌ **If not received, contact owner:** @hackingteamx\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    
    # Save review message ID to persistent file (will survive user_states deletion)
    payment_reviews = load_payment_reviews()
    payment_reviews[str(user_id)] = {
        "message_id": review_msg.message_id,
        "chat_id": message.chat.id,
        "amount": amount
    }
    save_payment_reviews(payment_reviews)
    print(f"💾 Saved review message ID {review_msg.message_id} for user {user_id}")

    # Get user info
    user = get_user(user_id)
    username = user.get('username', 'Not Set')
    first_name = user.get('first_name', 'Not Set')

    # Create admin approval markup
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.row(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_utr_{user_id}_{amount}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_utr_{user_id}_{amount}")
    )

    # Send to admin with retry logic (3 attempts max)
    notification_sent = False
    for retry in range(3):
        try:
            admin_bot.send_message(
                ADMIN_CHAT_ID,
                f"💳 **New Payment Request** 🔔\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"👤 **Username:** @{username}\n"
                f"📝 **Name:** {first_name}\n"
                f"💰 **Amount:** ₹{amount}\n"
                f"🔢 **UTR Number:** `{utr}`\n"
                f"👥 **Submission Attempt:** {attempt}/3\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚡ **Action Required:** Approve or Reject payment 👇",
                reply_markup=markup_admin,
                parse_mode="Markdown"
            )
            print(f"✅ Payment request sent to admin for user {user_id}, amount ₹{amount}, UTR: {utr}, Attempt: {attempt}/3")
            notification_sent = True
            break
        except Exception as e:
            print(f"⚠️ Admin notification error (Attempt {retry+1}/3): {e}")
            if retry < 2:
                time.sleep(1)  # Wait before retry

    if notification_sent:
        # Clear only if notification was successful
        del user_states[user_id]
    else:
        # Keep state for retry if notification failed after 3 attempts
        user_bot.send_message(
            message.chat.id,
            " **Balance will be added soon** 🔔\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Admin will process it soon .\n\n"
            "📤 BE PATIENT.\n\n"
            f"📊 **Attempt:** {attempt}/3\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        if attempt >= 3:
            del user_states[user_id]
            user_bot.send_message(
                message.chat.id,
                "❌ **Max Attempts Reached**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Please contact support.\n\n"
                "👨‍💻 Click 'Support' button to reach us!",
                parse_mode="Markdown"
            )

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("search_number_"))
def handle_number_details_search(call):
    number = call.data.replace("search_number_", "")
    user_id = call.from_user.id

    # Check balance
    user = get_user(user_id)
    if user['balance'] < NUMBER_SEARCH_PRICE:
        user_bot.answer_callback_query(
            call.id,
            f"❌ Insufficient balance! Need ₹{NUMBER_SEARCH_PRICE}. Current: ₹{user['balance']}",
            show_alert=True
        )
        return

    user_bot.answer_callback_query(call.id, "🔍 Searching number details...")

    # Show processing message
    process_msg = user_bot.send_message(
        call.message.chat.id,
        f"🔄 **Processing Number Search** 🚀\n\n"
        f"📞 **Number:** `{number}`\n\n"
        f"▱▱▱▱▱▱▱▱▱▱ 0%",
        parse_mode="Markdown"
    )

    stages = [
        ("▰▰▱▱▱▱▱▱▱▱", "20%", "Validating query... 🔍"),
        ("▰▰▰▰▱▱▱▱▱▱", "40%", "Connecting to database... 🌐"),
        ("▰▰▰▰▰▰▱▱▱▱", "60%", "Searching records... 📊"),
        ("▰▰▰▰▰▰▰▰▱▱", "80%", "Compiling results... 📋"),
        ("▰▰▰▰▰▰▰▰▰▰", "100%", "Finalizing... ✨")
    ]

    for bar, percent, status in stages:
        try:
            user_bot.edit_message_text(
                f"🔄 **Processing Number Search** 🚀\n\n"
                f"📞 **Number:** `{number}`\n"
                f"📊 **Status:** {status}\n\n"
                f"{bar} {percent}",
                call.message.chat.id,
                process_msg.message_id,
                parse_mode="Markdown"
            )
            time.sleep(0.4)
        except:
            pass

    # Generate report from Pyrogram
    query_id = randint(0, 9999999)
    report = generate_report(number, query_id)

    user_bot.delete_message(call.message.chat.id, process_msg.message_id)

    if report is None or not isinstance(report, list) or len(report) == 0:
        # Return JSON format for error
        no_result_json = [{
            "status": "error",
            "message": "Unable to retrieve data at this moment. Please try again later.",
            "number": number,
            "owned_and_developed_by": "@hackingteamx"
        }]
        json_str = json.dumps(no_result_json, indent=2, ensure_ascii=False)
        json_result = f"```json\n{json_str}\n```"

        user_bot.send_message(
            call.message.chat.id,
            json_result,
            parse_mode="Markdown"
        )
        return

    # Check if valid data found - ONLY deduct balance if "The name of the father" field exists
    has_valid_data = False
    for r in report:
        # Check if 'The name of the father' exists and 'no_results_found' is NOT in the JSON string
        if ("The name of the father" in str(r) or "father" in str(r).lower()) and "no_results_found" not in str(r):
            has_valid_data = True
            break

    if not has_valid_data:
        # Check if this is truly incomplete (only has "Request" field)
        is_truly_incomplete = False
        try:
            # Parse the JSON from the report
            json_text = report[0]
            if json_text.startswith("```json\n"):
                json_content = json_text[8:-4]
            else:
                json_content = json_text
            
            parsed_data = json.loads(json_content)
            # Check if it only contains "Request" field
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                if isinstance(parsed_data[0], list) and len(parsed_data[0]) > 0:
                    first_entry = parsed_data[0][0]
                    if isinstance(first_entry, dict) and "Request" in first_entry and len(first_entry) == 1:
                        is_truly_incomplete = True
        except:
            pass
        
        if is_truly_incomplete:
            # Save this number to prevent future searches
            add_to_incomplete_numbers(number)
            print(f"📝 Saved incomplete number: {number}")
        
        # Send the JSON result without deducting balance with typing effect
        send_with_typing_effect(call.message.chat.id, report[0])

        # Send message that full data not available, so no charge
        if is_truly_incomplete:
            user_bot.send_message(
                call.message.chat.id,
                f"ℹ️ **Incomplete Data Found** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Full data not available in records**\n\n"
                f"🚨 **WARNING:** Don't search this number again, otherwise you will be charged!\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        else:
            user_bot.send_message(
                call.message.chat.id,
                f"ℹ️ **Incomplete Data Found** 📋\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Full data not available in records**\n\n"
                f"💰 **No charge applied** - Your balance is safe! 🔒\n"
                f"💵 **Current Balance:** ₹{get_user(user_id)['balance']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        return

    # Only deduct balance if "The name of the father" field is found
    deduct_balance(user_id, NUMBER_SEARCH_PRICE)

    markup = create_inline_keyboard(query_id, 0, len(report))

    # Send JSON formatted result with typing effect
    send_with_typing_effect(call.message.chat.id, report[0], reply_markup=markup)

    user_bot.send_message(
        call.message.chat.id,
        f"✅ <b>Search Completed Successfully!</b> 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 <b>Deducted:</b> {get_price_display(NUMBER_SEARCH_PRICE, ORIGINAL_PRICES['NUMBER_SEARCH'])}\n"
        f"💰 <b>Remaining Balance:</b> ₹{get_user(user_id)['balance']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )

@user_bot.callback_query_handler(func=lambda call: call.data == "view_top_referrers")
def show_top_referrers_to_user(call):
    user_bot.answer_callback_query(call.id, "📊 Loading top referrers...")
    
    top_referrers = get_top_referrers(10)
    
    response = "╔═══════════════════════════════╗\n"
    response += "║   *🏆 TOP REFERRERS 🏆*   ║\n"
    response += "╚═══════════════════════════════╝\n\n"
    
    if not top_referrers:
        response += "_No referrals recorded yet._\n\n"
        response += "🚀 *Be the first to start referring!*"
    else:
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        with users_lock:
            users = load_users()
            for idx, referrer in enumerate(top_referrers, 1):
                user_id = referrer['user_id']
                user_info = users.get(user_id, {})
                first_name = user_info.get('first_name', 'Anonymous')
                earnings = referrer['total_earnings']
                count = referrer['total_referrals']
                
                # Medal emojis for top 3
                if idx == 1:
                    medal = "🥇"
                elif idx == 2:
                    medal = "🥈"
                elif idx == 3:
                    medal = "🥉"
                else:
                    medal = f"*{idx}.*"
                
                response += f"{medal} *{first_name}*\n"
                response += f"   ├─ Referrals: *{count}* 👥\n"
                response += f"   └─ Earnings: *₹{earnings}* 💰\n\n"
        
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        response += "💡 *Keep referring to reach the top!*\n"
        response += f"🎁 *Winner gets ₹150 bonus every Sunday!*"
    
    user_bot.send_message(
        call.message.chat.id,
        response,
        parse_mode="Markdown"
    )

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("/page "))
def handle_pagination(call):
    query_id, page_id = call.data.split(" ")[1:]
    if query_id not in cash_reports:
        user_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ **The results have been deleted** 🗑️"
        )
    else:
        report = cash_reports[query_id]
        # Ensure page_id is an integer and within valid range
        try:
            page_id_int = int(page_id)
            count_page = len(report)

            # Adjust page_id if it's out of bounds
            if page_id_int < 0:
                page_id_int = count_page - 1
            elif page_id_int >= count_page:
                page_id_int = 0 # Wrap around

            markup = create_inline_keyboard(query_id, page_id_int, count_page)
            user_bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=report[page_id_int],
                parse_mode="Markdown", # Assuming results are Markdown-compatible JSON
                reply_markup=markup
            )
        except (ValueError, IndexError):
            user_bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ **Invalid page number.** Please try again."
            )

# ============= ADMIN BOT =============

@admin_bot.message_handler(commands=['start'])
def admin_start(message):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👥 ALL USERS")
    btn2 = types.KeyboardButton("💵 ADD BALANCE")
    btn3 = types.KeyboardButton("💸 DEDUCT BALANCE")
    btn4 = types.KeyboardButton("🎟️ CREATE PROMO CODE")
    btn5 = types.KeyboardButton("📢 BROADCAST MESSAGE")
    btn6 = types.KeyboardButton("🔄 SHIFT PYROGRAM ACCOUNT")
    btn7 = types.KeyboardButton("📊 PYROGRAM STATUS")
    btn8 = types.KeyboardButton("⚙️ SET PYROGRAM LIMITS")
    btn9 = types.KeyboardButton("🔒 MANAGE CHANNEL MEMBERSHIP")
    btn10 = types.KeyboardButton("📊 REFERRAL STATS")
    btn11 = types.KeyboardButton("🔄 RESET USED COUNTS")
    btn12 = types.KeyboardButton("🚫 NO SEARCH RESULTS")
    btn13 = types.KeyboardButton("🤖 CHANGE NUMBER BOT")
    btn14 = types.KeyboardButton("👤 MANAGE USERNAME SEARCH")
    btn15 = types.KeyboardButton("🔄 RESET REFERRALS")
    btn16 = types.KeyboardButton("🔒 LOOKUP BLOCK")
    btn17 = types.KeyboardButton("💰 SET PRICE")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn14, btn10, btn11, btn12, btn13, btn15, btn16, btn17)

    admin_bot.send_message(
        message.chat.id,
        "🔐 **Welcome to Admin Dashboard!** 🚀\n\nSelect an option:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.message_handler(func=lambda message: message.text == "🎟️ CREATE PROMO CODE")
def create_promo_code(message):
    msg = admin_bot.send_message(message.chat.id, "🎟️ **Enter promo code name** (e.g., WELCOME100):")
    admin_bot.register_next_step_handler(msg, process_promo_name)

def process_promo_name(message):
    promo_name = message.text.strip().upper()

    with promo_codes_lock:
        promo_codes = load_promo_codes()
        if promo_name in promo_codes:
            admin_bot.send_message(message.chat.id, "❌ **This promo code already exists!**")
            return

    msg = admin_bot.send_message(message.chat.id, f"💰 **Enter amount for promo code '{promo_name}':**")
    admin_bot.register_next_step_handler(msg, process_promo_amount, promo_name)

def process_promo_amount(message, promo_name):
    try:
        amount = float(message.text.strip())
        msg = admin_bot.send_message(message.chat.id, f"👥 **Enter maximum number of users who can claim '{promo_name}':**")
        admin_bot.register_next_step_handler(msg, process_promo_max_uses, promo_name, amount)
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid amount!** Please try again.")

def process_promo_max_uses(message, promo_name, amount):
    try:
        max_uses = int(message.text.strip())

        # Save promo code
        with promo_codes_lock:
            promo_codes = load_promo_codes()
            promo_codes[promo_name] = {
                "amount": amount,
                "max_uses": max_uses,
                "used_count": 0,
                "used_by": []
            }
            save_promo_codes(promo_codes)

        admin_bot.send_message(
            message.chat.id,
            f"✅ **Promo Code Created!** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎟️ **Code:** `{promo_name}`\n"
            f"💰 **Amount:** ₹{amount}\n"
            f"👥 **Max Uses:** {max_uses}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 **Share this code with users!**",
            parse_mode="Markdown"
        )
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid number!** Please try again.")


@admin_bot.message_handler(func=lambda message: message.text == "💸 DEDUCT BALANCE")
def deduct_balance_admin(message):
    msg = admin_bot.send_message(message.chat.id, "🆔 **Enter the User ID:**")
    admin_bot.register_next_step_handler(msg, process_deduct_user_id)

def process_deduct_user_id(message):
    user_id = message.text.strip()
    msg = admin_bot.send_message(
        message.chat.id,
        f"💸 **Enter balance to deduct from User ID** `{user_id}`:",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_deduct_amount, user_id)

def process_deduct_amount(message, user_id):
    try:
        amount = float(message.text.strip())
        user = get_user(user_id)

        if user['balance'] < amount:
            admin_bot.send_message(
                message.chat.id,
                f"❌ **Insufficient balance!**\n\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"💰 **Current Balance:** ₹{user['balance']}\n"
                f"💸 **Requested Deduct:** ₹{amount}\n"
                f"❌ **Deficit:** ₹{amount - user['balance']}",
                parse_mode="Markdown"
            )
            return

        new_balance = user['balance'] - amount
        update_user_balance(user_id, new_balance)

        admin_bot.send_message(
            message.chat.id,
            f"✅ **Balance deducted successfully!**\n\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"💸 **Amount Deducted:** ₹{amount}\n"
            f"💵 **New Balance:** ₹{new_balance}",
            parse_mode="Markdown"
        )
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid amount!** Please try again.")

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("approve_utr_"))
def handle_approve_utr(call):
    try:
        parts = call.data.replace("approve_utr_", "").split("_")
        user_id = int(parts[0])
        amount = float(parts[1])

        # Update user balance
        user = get_user(user_id)
        new_balance = user['balance'] + amount
        update_user_balance(user_id, new_balance)
        
        # Process referral bonus (if this is first recharge)
        referrer_id = process_referral_bonus(user_id)
        referral_message = ""
        
        if referrer_id:
            try:
                # Get referrer info
                referrer_user = get_user(int(referrer_id))
                referrer_balance = referrer_user.get('balance', 0)
                
                # Notify referrer
                user_bot.send_message(
                    int(referrer_id),
                    f"🎉 **Referral Bonus Earned!** 💰\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **Your referral completed their first recharge!**\n\n"
                    f"💰 **Bonus Received:** ₹{REFERRAL_BONUS} 🎁\n"
                    f"💵 **New Balance:** ₹{referrer_balance} 🚀\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"✨ **Keep sharing to earn more!** 📤",
                    parse_mode="Markdown"
                )
                referral_message = f"\n🎁 **Referral bonus ₹{REFERRAL_BONUS} given to referrer!**"
            except Exception as e:
                print(f"Error notifying referrer: {e}")

        # Notify admin
        admin_bot.edit_message_text(
            f"✅ **Payment Approved!** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"💰 **Amount Added:** ₹{amount}\n"
            f"💵 **New Balance:** ₹{new_balance}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ **Balance added successfully!**{referral_message}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

        # Delete "Payment Under Review" message and send approval
        try:
            # Load payment reviews from file
            payment_reviews = load_payment_reviews()
            if str(user_id) in payment_reviews:
                review_data = payment_reviews[str(user_id)]
                try:
                    print(f"🔪 Deleting review message {review_data['message_id']} for user {user_id}")
                    user_bot.delete_message(review_data['chat_id'], review_data['message_id'])
                except Exception as e:
                    print(f"⚠️ Could not delete review message: {e}")
                
                # Remove from payment reviews
                del payment_reviews[str(user_id)]
                save_payment_reviews(payment_reviews)
                print(f"✅ Cleaned up payment review record for user {user_id}")
        except Exception as e:
            print(f"Error deleting review message: {e}")
        
        # Notify user with approval message
        try:
            user_bot.send_message(
                user_id,
                f"✅ **Payment Approved!** 🎉\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 **Amount Added:** ₹{amount} 💎\n"
                f"💵 **New Balance:** ₹{new_balance} 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎉 **Thank you for your payment!** ⚡",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error notifying user: {e}")

        admin_bot.answer_callback_query(call.id, "✅ Balance added successfully!", show_alert=True)

    except Exception as e:
        admin_bot.answer_callback_query(call.id, f"❌ Error: {str(e)}", show_alert=True)

@admin_bot.message_handler(func=lambda message: message.text == "💰 SET PRICE")
def set_price_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"📞 Number Search ({NUMBER_SEARCH_PRICE}₹)", callback_data="set_price_number"),
        types.InlineKeyboardButton(f"👤 Username Search ({USERNAME_SEARCH_PRICE}₹)", callback_data="set_price_username"),
        types.InlineKeyboardButton(f"👤 Profile Lookup ({PROFILE_SEARCH_PRICE}₹)", callback_data="set_price_profile")
    )
    admin_bot.send_message(message.chat.id, "💰 **Select Search Type to update price:**", reply_markup=markup, parse_mode="Markdown")

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("set_price_"))
def handle_set_price_callback(call):
    search_type = call.data.replace("set_price_", "")
    msg = admin_bot.send_message(call.message.chat.id, f"📝 **Enter new price for {search_type.replace('_', ' ').title()}:**")
    admin_bot.register_next_step_handler(msg, process_new_price, search_type)
    admin_bot.answer_callback_query(call.id)

def process_new_price(message, search_type):
    global NUMBER_SEARCH_PRICE, USERNAME_SEARCH_PRICE, PROFILE_SEARCH_PRICE
    try:
        new_price = float(message.text.strip())
        with prices_lock:
            if search_type == "number":
                NUMBER_SEARCH_PRICE = new_price
            elif search_type == "username":
                USERNAME_SEARCH_PRICE = new_price
            elif search_type == "profile":
                PROFILE_SEARCH_PRICE = new_price
            save_prices()
        
        admin_bot.send_message(message.chat.id, f"✅ **Price updated successfully!**\n\n💰 New {search_type.title()} Search Price: ₹{new_price}")
    except ValueError:
        admin_bot.send_message(message.chat.id, "❌ **Invalid price!** Please enter a number.")
    try:
        parts = call.data.replace("reject_utr_", "").split("_")
        user_id = int(parts[0])
        amount = float(parts[1])

        # Notify admin
        admin_bot.edit_message_text(
            f"❌ **Payment Rejected** 🚫\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"💰 **Amount:** ₹{amount}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ **Payment not approved**",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

        # Notify user
        try:
            user_bot.send_message(
                user_id,
                f"❌ **Payment Not Received** 🚫\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 **Amount:** ₹{amount}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ **Your payment could not be verified.**\n\n"
                f"💡 **Please contact support:** @hackingteamx\n"
                f"🔄 **Or try again with correct UTR** ⚡",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error notifying user: {e}")

        admin_bot.answer_callback_query(call.id, "❌ Payment rejected!", show_alert=True)

    except Exception as e:
        admin_bot.answer_callback_query(call.id, f"❌ Error: {str(e)}", show_alert=True)

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("provide_"))
def handle_provide_data_callback(call):
    username = call.data.replace("provide_", "")

    if username not in pending_username_searches:
        admin_bot.answer_callback_query(call.id, "❌ Request expired or already processed.", show_alert=True)
        return

    admin_bot.answer_callback_query(call.id, "✅ Processing request...")

    original_username = pending_username_searches[username].get('original_username', username)

    # Escape special characters
    def escape_markdown_v2(text):
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    escaped_username = escape_markdown_v2(original_username)

    msg = admin_bot.send_message(
        call.message.chat.id,
        f"📞 *Enter phone number for @{escaped_username}:*\n\n"
        f"*Format:* \\+91XXXXXXXXXX",
        parse_mode="MarkdownV2"
    )
    admin_bot.register_next_step_handler(msg, process_admin_number_only, username)

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("no_data_"))
def handle_no_data_callback(call):
    username = call.data.replace("no_data_", "")

    if username not in pending_username_searches:
        admin_bot.answer_callback_query(call.id, "❌ Request expired or already processed.", show_alert=True)
        return

    search_info = pending_username_searches[username]
    user_id = search_info['user_id']
    chat_id = search_info['chat_id']
    original_username = search_info.get('original_username', username)

    # Notify user - NO balance deduction
    try:
        user_bot.send_message(
            chat_id,
            f"❌ **Data Not Available** 😔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Username:** @{original_username}\n\n"
            f"⚠️ **Sorry, no data found in our database for this username.**\n\n"
            f"💰 **Your balance is safe** - No charges applied! 🔒\n"
            f"💵 **Current Balance:** ₹{get_user(user_id)['balance']} 💎\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 **Try another username** ⚡",
            parse_mode="Markdown"
        )
        print(f"✅ No data message sent to user {user_id} for @{original_username}")
    except Exception as e:
        print(f"❌ Error sending no data message: {e}")

    # Confirm to admin
    admin_bot.edit_message_text(
        f"❌ **Data Not Available** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Username:** @{original_username}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ **User notified - No balance deducted**",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    admin_bot.answer_callback_query(call.id, "✅ User notified - No charges applied!", show_alert=True)

    del pending_username_searches[username]

def process_admin_number_only(message, username):
    number = message.text.strip()

    if username not in pending_username_searches:
        admin_bot.send_message(message.chat.id, "❌ **Request expired.**", parse_mode="Markdown")
        return

    search_info = pending_username_searches[username]
    user_id = search_info['user_id']
    chat_id = search_info['chat_id']
    original_username = search_info.get('original_username', username)

    # Deduct balance for username search
    deduct_balance(user_id, USERNAME_SEARCH_PRICE)

    # Send number to user with button to get details
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔍 Get Number Details", callback_data=f"search_number_{number}"))

        user_bot.send_message(
            chat_id,
            f"✅ **Username Search Results** 🎉\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Username:** @{original_username}\n"
            f"📞 **Phone Number:** `{number}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💸 **Deducted:** {get_price_display(USERNAME_SEARCH_PRICE, ORIGINAL_PRICES['USERNAME_SEARCH'])}\n"
            f"💰 **Remaining Balance:** ₹{get_user(user_id)['balance']} 💎\n\n"
            f"🔍 **Click below to get detailed information** (₹4 will be deducted) ⚡",
            reply_markup=markup,
            parse_mode="Markdown"
        )

        print(f"✅ Number sent to user {user_id} for username @{original_username}")
    except Exception as e:
        print(f"❌ Error sending number to user: {e}")
        import traceback
        traceback.print_exc()

    # Confirm to admin
    try:
        admin_bot.send_message(
            message.chat.id,
            f"✅ **Number provided successfully!** 🎉\n\n"
            f"👤 **Username:** @{original_username}\n"
            f"📞 **Number:** {number}\n"
            f"🆔 **User ID:** {user_id}\n\n"
            f"✨ **Number sent to user with option to get details!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error confirming to admin: {e}")

    del pending_username_searches[username]

@admin_bot.message_handler(func=lambda message: message.text == "👥 ALL USERS")
def show_all_users(message):
    with users_lock:
        users = load_users()

    if not users:
        admin_bot.send_message(message.chat.id, "❌ **No users found.**")
        return

    # Send the users.json file directly
    try:
        with open(USERS_FILE, 'rb') as users_file:
            admin_bot.send_document(
                message.chat.id,
                users_file,
                caption=f"👥 **All Users Database** 💎\n\n"
                        f"📊 **Total Users:** {len(users)} 🚀\n"
                        f"📁 **File:** users.json (Real-time data)",
                parse_mode="Markdown"
            )
    except Exception as e:
        admin_bot.send_message(
            message.chat.id,
            f"❌ **Error sending file:** {str(e)}\n\n"
            f"Please check the file permissions.",
            parse_mode="Markdown"
        )

@admin_bot.message_handler(func=lambda message: message.text == "💵 ADD BALANCE")
def add_balance_admin(message):
    msg = admin_bot.send_message(message.chat.id, "🆔 **Enter the User ID:**")
    admin_bot.register_next_step_handler(msg, process_admin_user_id)

def process_admin_user_id(message):
    user_id = message.text.strip()
    msg = admin_bot.send_message(
        message.chat.id,
        f"💰 **Enter balance to add for User ID** `{user_id}`:",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_admin_balance, user_id)

def process_admin_balance(message, user_id):
    try:
        amount = float(message.text.strip())
        user = get_user(user_id)
        new_balance = user['balance'] + amount
        update_user_balance(user_id, new_balance)

        admin_bot.send_message(
            message.chat.id,
            f"✅ **Balance added successfully!** 🎉\n\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"💰 **Amount added:** ₹{amount}\n"
            f"💵 **New Balance:** ₹{new_balance}",
            parse_mode="Markdown"
        )
    except:
        admin_bot.send_message(message.chat.id, "❌ **Invalid amount!** Please try again.")

@admin_bot.message_handler(func=lambda message: message.text == "📊 PYROGRAM STATUS")
def show_pyrogram_status(message):
    response = "📊 Pyrogram Configuration Status 🤖\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Number Search Pyrogram
    response += "📞 Number Search Pyrogram:\n"
    if number_search_client:
        response += "   ✅ Configured & Active\n"
        response += f"   📱 Phone: {NUMBER_SEARCH_PYROGRAM['phone']}\n"
        response += f"   🆔 API ID: {NUMBER_SEARCH_PYROGRAM['api_id']}\n"
    else:
        response += "   ❌ Not configured\n"

    response += "\n👤 Username Search Pyrograms:\n"
    configured_count = sum(1 for config in USERNAME_SEARCH_PYROGRAMS if config["api_id"] != 0 and config["api_hash"])

    if configured_count > 0:
        response += f"   ✅ Total Configured: {configured_count}/{len(USERNAME_SEARCH_PYROGRAMS)}\n"
        response += f"   🎯 Active Account: #{ACTIVE_USERNAME_PYROGRAM_INDEX + 1}\n\n"
        for idx, config in enumerate(USERNAME_SEARCH_PYROGRAMS):
            if config["api_id"] != 0 and config["api_hash"]:
                status = "🟢 ACTIVE" if idx == ACTIVE_USERNAME_PYROGRAM_INDEX else "⚪ Inactive"
                limit = USERNAME_PYROGRAM_LIMITS.get(idx, "∞ (No Limit)")
                count = USERNAME_PYROGRAM_REQUEST_COUNTS.get(idx, 0)
                response += f"   Account #{idx + 1} {status}\n"
                response += f"   📱 Phone: {config.get('phone', 'Not set')}\n"
                response += f"   🤖 Target Bot: {config.get('target_bot', 'Not set')}\n"
                response += f"   📊 Limit: {limit} | Used: {count}\n\n"
    else:
        response += "   ❌ No accounts configured\n"
        response += "   💡 Configure in main.py USERNAME_SEARCH_PYROGRAMS\n"

    response += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
    admin_bot.send_message(message.chat.id, response)

@admin_bot.message_handler(func=lambda message: message.text == "⚙️ SET PYROGRAM LIMITS")
def set_pyrogram_limits_menu(message):
    configured_accounts = [i for i, config in enumerate(USERNAME_SEARCH_PYROGRAMS) if config["api_id"] != 0 and config["api_hash"]]

    if not configured_accounts:
        admin_bot.send_message(
            message.chat.id,
            "❌ No Username Pyrogram accounts configured!\n\n"
            "💡 Configure accounts in main.py USERNAME_SEARCH_PYROGRAMS",
            parse_mode="Markdown"
        )
        return

    response = "⚙️ **Set Pyrogram Account Limits** 📊\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    response += "**Current Limits:**\n\n"

    for idx in configured_accounts:
        config = USERNAME_SEARCH_PYROGRAMS[idx]
        limit = USERNAME_PYROGRAM_LIMITS.get(idx, "∞ (No Limit)")
        count = USERNAME_PYROGRAM_REQUEST_COUNTS.get(idx, 0)
        status = "🟢 ACTIVE" if idx == ACTIVE_USERNAME_PYROGRAM_INDEX else "⚪"
        
        response += f"{status} **Account #{idx + 1}**\n"
        response += f"   Phone: {config.get('phone', 'N/A')}\n"
        response += f"   Limit: {limit} | Used: {count}\n\n"

    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    response += "👇 **Select account to set limit:**"

    markup = types.InlineKeyboardMarkup()
    for idx in configured_accounts:
        config = USERNAME_SEARCH_PYROGRAMS[idx]
        limit = USERNAME_PYROGRAM_LIMITS.get(idx, "No Limit")
        btn_text = f"Account #{idx + 1} ({config.get('phone', 'N/A')}) - Limit: {limit}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"set_limit_{idx}"))

    admin_bot.send_message(
        message.chat.id,
        response,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("set_limit_"))
def handle_set_limit(call):
    account_idx = int(call.data.replace("set_limit_", ""))
    
    admin_bot.answer_callback_query(call.id, "Enter limit for this account")
    
    msg = admin_bot.send_message(
        call.message.chat.id,
        f"⚙️ **Set Limit for Account #{account_idx + 1}**\n\n"
        f"Enter the maximum number of requests allowed before auto-rotation:\n\n"
        f"💡 Enter a number (e.g., 4, 10, 50) or type 'unlimited' for no limit",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_limit_input, account_idx)

def process_limit_input(message, account_idx):
    global USERNAME_PYROGRAM_LIMITS
    
    limit_input = message.text.strip().lower()
    
    if limit_input == 'unlimited':
        # Remove limit
        if account_idx in USERNAME_PYROGRAM_LIMITS:
            del USERNAME_PYROGRAM_LIMITS[account_idx]
        limit_text = "∞ (No Limit)"
    else:
        try:
            limit_value = int(limit_input)
            if limit_value <= 0:
                admin_bot.send_message(
                    message.chat.id,
                    "❌ **Invalid limit!** Please enter a positive number or 'unlimited'",
                    parse_mode="Markdown"
                )
                return
            USERNAME_PYROGRAM_LIMITS[account_idx] = limit_value
            limit_text = str(limit_value)
        except ValueError:
            admin_bot.send_message(
                message.chat.id,
                "❌ **Invalid input!** Please enter a number or 'unlimited'",
                parse_mode="Markdown"
            )
            return
    
    # Save configuration
    save_active_pyrogram_index()
    
    config = USERNAME_SEARCH_PYROGRAMS[account_idx]
    admin_bot.send_message(
        message.chat.id,
        f"✅ **Limit Set Successfully!** 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Account #{account_idx + 1}**\n"
        f"📱 Phone: {config.get('phone', 'N/A')}\n"
        f"📊 New Limit: {limit_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ Auto-rotation will occur when this limit is reached!",
        parse_mode="Markdown"
    )



@admin_bot.message_handler(func=lambda message: message.text == "🔄 SHIFT PYROGRAM ACCOUNT")
def shift_pyrogram_account(message):
    # Filter only configured accounts
    configured_accounts = [i for i, config in enumerate(USERNAME_SEARCH_PYROGRAMS) if config["api_id"] != 0 and config["api_hash"]]

    if not configured_accounts:
        admin_bot.send_message(
            message.chat.id,
            "❌ No Username Pyrogram accounts configured!\n\n"
            "💡 Configure accounts in main.py USERNAME_SEARCH_PYROGRAMS",
            parse_mode="Markdown"
        )
        return

    response = "🔄 **Select Active Pyrogram Account** 🎯\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    markup = types.InlineKeyboardMarkup()
    for idx in configured_accounts:
        config = USERNAME_SEARCH_PYROGRAMS[idx]
        status = "🟢 ACTIVE" if idx == ACTIVE_USERNAME_PYROGRAM_INDEX else "⚪"
        btn_text = f"{status} Account #{idx + 1} - {config.get('phone', 'N/A')}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"shift_pyrogram_{idx}"))

    response += f"**Current Active:** Account #{ACTIVE_USERNAME_PYROGRAM_INDEX + 1}\n\n"
    response += "👇 Click to activate different account:"

    admin_bot.send_message(
        message.chat.id,
        response,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("shift_pyrogram_"))
def handle_shift_pyrogram(call):
    global ACTIVE_USERNAME_PYROGRAM_INDEX
    new_index = int(call.data.replace("shift_pyrogram_", ""))

    if new_index >= len(USERNAME_SEARCH_PYROGRAMS):
        admin_bot.answer_callback_query(call.id, "❌ Invalid account!", show_alert=True)
        return

    config = USERNAME_SEARCH_PYROGRAMS[new_index]
    if config["api_id"] == 0 or not config["api_hash"]:
        admin_bot.answer_callback_query(call.id, "❌ Account not configured!", show_alert=True)
        return

    ACTIVE_USERNAME_PYROGRAM_INDEX = new_index
    save_active_pyrogram_index()

    admin_bot.edit_message_text(
        f"✅ Pyrogram Account Shifted! 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Now Active: Account #{new_index + 1}\n"
        f"📱 Phone: {config.get('phone', 'N/A')}\n"
        f"🤖 Target Bot: {config.get('target_bot', 'N/A')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ All username searches will now use this account!",
        call.message.chat.id,
        call.message.message_id
    )

    admin_bot.answer_callback_query(call.id, f"✅ Shifted to Account #{new_index + 1}!", show_alert=True)

@admin_bot.message_handler(func=lambda message: message.text == "🔒 MANAGE CHANNEL MEMBERSHIP")
def manage_channel_membership(message):
    global CHANNEL_MEMBERSHIP_REQUIRED

    status = "🟢 ON" if CHANNEL_MEMBERSHIP_REQUIRED else "🔴 OFF"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Turn ON", callback_data="channel_membership_on"),
        types.InlineKeyboardButton("❌ Turn OFF", callback_data="channel_membership_off")
    )

    admin_bot.send_message(
        message.chat.id,
        f"🔒 **Channel Membership Management** 📢\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Current Status:** {status}\n\n"
        f"**What this controls:**\n"
        f"• **ON**: Users must join channels to use the bot\n"
        f"• **OFF**: Users can use bot without joining channels\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Choose an option below:**",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "channel_membership_on")
def turn_channel_membership_on(call):
    global CHANNEL_MEMBERSHIP_REQUIRED
    CHANNEL_MEMBERSHIP_REQUIRED = True

    admin_bot.edit_message_text(
        f"✅ **Channel Membership: ENABLED** 🟢\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Users now **MUST** join channels to use the bot.\n"
        f"Existing users who haven't joined will be prompted.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    admin_bot.answer_callback_query(call.id, "✅ Channel membership requirement ENABLED!")

@admin_bot.callback_query_handler(func=lambda call: call.data == "channel_membership_off")
def turn_channel_membership_off(call):
    global CHANNEL_MEMBERSHIP_REQUIRED
    CHANNEL_MEMBERSHIP_REQUIRED = False

    admin_bot.edit_message_text(
        f"❌ **Channel Membership: DISABLED** 🔴\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Users can now use the bot **WITHOUT** joining channels.\n"
        f"All features accessible immediately.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    admin_bot.answer_callback_query(call.id, "❌ Channel membership requirement DISABLED!")

@admin_bot.message_handler(func=lambda message: message.text == "👤 MANAGE USERNAME SEARCH")
def manage_username_search(message):
    global USERNAME_SEARCH_ENABLED

    status = "🟢 ON" if USERNAME_SEARCH_ENABLED else "🔴 OFF"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Turn ON", callback_data="username_search_on"),
        types.InlineKeyboardButton("❌ Turn OFF", callback_data="username_search_off")
    )

    admin_bot.send_message(
        message.chat.id,
        f"👤 **Username Search Management** 🔍\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Current Status:** {status}\n\n"
        f"**What this controls:**\n"
        f"• **ON**: Users can search usernames and user IDs\n"
        f"• **OFF**: Username/User ID search disabled for all users\n"
        f"• Phone number search remains **ALWAYS AVAILABLE**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Choose an option below:**",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "username_search_on")
def turn_username_search_on(call):
    global USERNAME_SEARCH_ENABLED
    USERNAME_SEARCH_ENABLED = True

    admin_bot.edit_message_text(
        f"✅ **Username Search: ENABLED** 🟢\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Users can now search **usernames and user IDs**.\n"
        f"All username search features are active.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    admin_bot.answer_callback_query(call.id, "✅ Username search ENABLED!")

@admin_bot.callback_query_handler(func=lambda call: call.data == "username_search_off")
def turn_username_search_off(call):
    global USERNAME_SEARCH_ENABLED
    USERNAME_SEARCH_ENABLED = False

    admin_bot.edit_message_text(
        f"❌ **Username Search: DISABLED** 🔴\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Username/User ID search is now **DISABLED** for all users.\n"
        f"📞 **Phone number search remains available**.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    admin_bot.answer_callback_query(call.id, "❌ Username search DISABLED!")

@admin_bot.message_handler(func=lambda message: message.text == "🔄 RESET USED COUNTS")
def reset_pyrogram_used_counts(message):
    global USERNAME_PYROGRAM_REQUEST_COUNTS
    
    # Reset all request counts to zero
    USERNAME_PYROGRAM_REQUEST_COUNTS = {}
    save_active_pyrogram_index()
    
    admin_bot.send_message(
        message.chat.id,
        "✅ **All Pyrogram Used Counts Reset!** 🔄\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "All account usage counts have been set to **0**\n\n"
        "📊 **Status:**\n"
        "• All accounts are now at 0 used requests\n"
        "• Limits remain unchanged\n"
        "• Ready for fresh rotation cycle\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

@admin_bot.message_handler(func=lambda message: message.text and message.text.strip() == "📊 REFERRAL STATS")
def show_referral_statistics(message):
    try:
        # Get overall stats
        overall_stats = get_total_referral_stats()
        top_referrers = get_top_referrers(10)
        
        # Format top referrers list
        top_list = ""
        if top_referrers:
            with users_lock:
                users = load_users()
                for idx, referrer in enumerate(top_referrers, 1):
                    user_id = referrer['user_id']
                    user_info = users.get(user_id, {})
                    username = user_info.get('username', 'N/A')
                    first_name = user_info.get('first_name', 'Anonymous')
                    earnings = referrer['total_earnings']
                    count = referrer['total_referrals']
                    
                    # Use first_name instead of username for better display
                    # Escape markdown special characters to prevent parsing errors
                    display_name = f"@{username}" if username != 'N/A' else first_name
                    # Escape special markdown characters: * _ [ ] ( ) ~ ` > # + - = | { } . !
                    display_name = display_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                    top_list += f"{idx}. {display_name} (ID: {user_id})\n"
                    top_list += f"   └─ Referrals: {count} | Earnings: ₹{earnings}\n\n"
        else:
            top_list = "_No referrals yet._\n"
        
        admin_bot.send_message(
            message.chat.id,
            "╔═══════════════════════════════╗\n"
            "║   *REFERRAL STATISTICS* 📊   ║\n"
            "╚═══════════════════════════════╝\n\n"
            "*📈 Overall Statistics:*\n\n"
            f"├─ 💰 Total Bonuses Given: *₹{overall_stats['total_bonuses']}*\n"
            f"├─ 👥 Total Referrals: *{overall_stats['total_referrals']}*\n"
            f"└─ 📊 Conversion Rate: *{overall_stats['conversion_rate']}%*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "*🏆 Top 10 Referrers:*\n\n"
            f"{top_list}"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*💡 Bonus per referral: ₹{REFERRAL_BONUS}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        admin_bot.send_message(
            message.chat.id,
            f"❌ **Error loading referral stats:**\n\n`{str(e)}`",
            parse_mode="Markdown"
        )
        print(f"Error in referral stats: {e}")
        import traceback
        traceback.print_exc()

@admin_bot.message_handler(func=lambda message: message.text == "🔄 RESET REFERRALS")
def reset_referrals_menu(message):
    with referrals_lock:
        referrals = load_referrals()
        total_users_with_referrals = sum(1 for user_data in referrals.values() if len(user_data.get("referrals", [])) > 0)
        total_referral_count = sum(len(user_data.get("referrals", [])) for user_data in referrals.values())
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ YES, Reset All", callback_data="reset_referrals_confirm"),
        types.InlineKeyboardButton("❌ NO, Cancel", callback_data="reset_referrals_cancel")
    )
    
    admin_bot.send_message(
        message.chat.id,
        "🔄 **RESET ALL REFERRAL COUNTS** ⚠️\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**⚠️ WARNING: This action will:**\n\n"
        "• Reset ALL users' referral counts to 0\n"
        "• Clear all referral history\n"
        "• Reset total earnings from referrals\n\n"
        "**📊 Current Stats:**\n"
        f"• Users with referrals: {total_users_with_referrals}\n"
        f"• Total referral count: {total_referral_count}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**🔒 This action CANNOT be undone!**\n\n"
        "Are you sure you want to reset all referral counts?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "reset_referrals_confirm")
def confirm_reset_referrals(call):
    try:
        with referrals_lock:
            referrals = load_referrals()
            
            reset_count = 0
            for user_id in referrals:
                if len(referrals[user_id].get("referrals", [])) > 0 or referrals[user_id].get("total_earnings", 0) > 0:
                    reset_count += 1
                referrals[user_id]["referrals"] = []
                referrals[user_id]["total_earnings"] = 0
            
            save_referrals(referrals)
        
        admin_bot.edit_message_text(
            "✅ **REFERRAL COUNTS RESET SUCCESSFULLY!** 🎉\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **Reset Summary:**\n\n"
            f"• Users affected: {reset_count}\n"
            "• All referral counts: 0\n"
            "• All referral earnings: ₹0\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🆕 Users can now start fresh referrals for the new week!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        admin_bot.answer_callback_query(call.id, "✅ All referral counts have been reset!")
        
    except Exception as e:
        admin_bot.edit_message_text(
            f"❌ **Error resetting referrals:**\n\n`{str(e)}`",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        admin_bot.answer_callback_query(call.id, "❌ Error occurred!")
        print(f"Error resetting referrals: {e}")
        import traceback
        traceback.print_exc()

@admin_bot.callback_query_handler(func=lambda call: call.data == "reset_referrals_cancel")
def cancel_reset_referrals(call):
    admin_bot.edit_message_text(
        "❌ **Reset Cancelled** 🛑\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "No changes were made.\n"
        "All referral data remains intact.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    admin_bot.answer_callback_query(call.id, "❌ Reset cancelled!")

@admin_bot.message_handler(func=lambda message: message.text == "🚫 NO SEARCH RESULTS")
def no_search_results_menu(message):
    with searched_no_data_lock:
        data = load_searched_no_data()
        total_count = len(data)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 View All", callback_data="nsr_view_all"),
        types.InlineKeyboardButton("➕ Add Username", callback_data="nsr_add")
    )
    markup.add(
        types.InlineKeyboardButton("🗑️ Delete Username", callback_data="nsr_delete")
    )
    
    admin_bot.send_message(
        message.chat.id,
        f"🚫 **No Search Results Manager** 📊\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Total Entries:** {total_count}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**What would you like to do?**\n\n"
        f"📋 **View All:** See all usernames with no data\n"
        f"➕ **Add Username:** Block a username from searches\n"
        f"🗑️ **Delete Username:** Allow a username to be searched again",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "nsr_view_all")
def nsr_view_all(call):
    with searched_no_data_lock:
        data = load_searched_no_data()
    
    if not data:
        admin_bot.answer_callback_query(call.id, "No entries found!")
        admin_bot.edit_message_text(
            "📋 **No Search Results List** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ **List is empty!**\n\n"
            "No usernames are currently blocked.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        return
    
    username_entries = []
    for key, entry in data.items():
        if entry.get('search_type') == 'username':
            query = entry.get('query', 'Unknown')
            # Escape ALL Markdown special characters to prevent parsing errors
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            escaped_query = query
            for char in special_chars:
                escaped_query = escaped_query.replace(char, f'\\{char}')
            username_entries.append(f"@{escaped_query}")
    
    if not username_entries:
        admin_bot.answer_callback_query(call.id, "No username entries found!")
        admin_bot.edit_message_text(
            "📋 **No Search Results List** 🚫\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ **No username entries found!**\n\n"
            "Only user_id entries exist (if any).",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        return
    
    entries_text = "\n".join(username_entries[:50])
    if len(username_entries) > 50:
        entries_text += f"\n\n... and {len(username_entries) - 50} more"
    
    admin_bot.answer_callback_query(call.id, "✅ Loaded!")
    admin_bot.edit_message_text(
        f"📋 **No Search Results List** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Total Usernames:** {len(username_entries)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{entries_text}",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "nsr_add")
def nsr_add(call):
    admin_bot.answer_callback_query(call.id, "✅ Please send the username")
    msg = admin_bot.send_message(
        call.message.chat.id,
        "➕ **Add Username to Block List** 🚫\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Please send the username to block:\n\n"
        "📝 **Format:** username or @username\n"
        "⚠️ **Note:** This username will NOT be searchable by users\n\n"
        "❌ Send /cancel to cancel",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_nsr_add)

def process_nsr_add(message):
    if message.text and message.text.strip().lower() == '/cancel':
        admin_bot.send_message(message.chat.id, "❌ **Cancelled!**", parse_mode="Markdown")
        return
    
    # Normalize username: remove @, convert to lowercase (same as automatic searches)
    username = message.text.strip().lstrip('@').lower()
    
    if not username or len(username) < 1:
        admin_bot.send_message(
            message.chat.id,
            "❌ **Invalid username!** Please enter a valid username.",
            parse_mode="Markdown"
        )
        return
    
    with searched_no_data_lock:
        data = load_searched_no_data()
        # Use the same normalization format as automatic searches
        key = f"username_{username}"
        
        if key in data:
            admin_bot.send_message(
                message.chat.id,
                f"⚠️ **Username already exists!**\n\n"
                f"@{username} is already in the blocked list.",
                parse_mode="Markdown"
            )
            return
        
        # Store with normalized username (without @, lowercase)
        data[key] = {
            "query": username,
            "search_type": "username",
            "timestamp": time.time(),
            "added_by_admin": True
        }
        save_searched_no_data(data)
    
    admin_bot.send_message(
        message.chat.id,
        f"✅ **Username Added!** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Username:** @{username}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"This username is now **BLOCKED** from searches.\n"
        f"Users will see 'No data found' message.",
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "nsr_delete")
def nsr_delete(call):
    admin_bot.answer_callback_query(call.id, "✅ Please send the username")
    msg = admin_bot.send_message(
        call.message.chat.id,
        "🗑️ **Delete Username from Block List** ✅\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Please send the username to remove:\n\n"
        "📝 **Format:** username or @username\n"
        "⚠️ **Note:** This username will become searchable again\n\n"
        "❌ Send /cancel to cancel",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_nsr_delete)

def process_nsr_delete(message):
    if message.text and message.text.strip().lower() == '/cancel':
        admin_bot.send_message(message.chat.id, "❌ **Cancelled!**", parse_mode="Markdown")
        return
    
    # Normalize username: remove @, convert to lowercase (same as automatic searches)
    username = message.text.strip().lstrip('@').lower()
    
    if not username or len(username) < 1:
        admin_bot.send_message(
            message.chat.id,
            "❌ **Invalid username!** Please enter a valid username.",
            parse_mode="Markdown"
        )
        return
    
    with searched_no_data_lock:
        data = load_searched_no_data()
        # Use the same normalization format as automatic searches
        key = f"username_{username}"
        
        if key not in data:
            admin_bot.send_message(
                message.chat.id,
                f"⚠️ **Username not found!**\n\n"
                f"@{username} is not in the blocked list.\n\n"
                f"💡 **Tip:** Make sure the username is spelled correctly.",
                parse_mode="Markdown"
            )
            return
        
        # Delete the entry
        del data[key]
        save_searched_no_data(data)
    
    admin_bot.send_message(
        message.chat.id,
        f"✅ **Username Deleted!** ♻️\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Username:** @{username}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"This username is now **SEARCHABLE** again.\n"
        f"Users can search for this username.",
        parse_mode="Markdown"
    )

@admin_bot.message_handler(func=lambda message: message.text == "🤖 CHANGE NUMBER BOT")
def change_number_bot_username(message):
    global NUMBER_SEARCH_BOT_USERNAME
    
    current_bot = NUMBER_SEARCH_BOT_USERNAME
    
    # Escape underscores in bot username for Markdown
    escaped_current_bot = current_bot.replace('_', '\\_')
    
    # Status indicators for both bots
    status_zaverin = "🟢 ACTIVE" if current_bot == "@ZaverinBot" else "⚪"
    status_osneh = "🟢 ACTIVE" if current_bot == "@numbersearahsv_bot" else "⚪"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{status_zaverin} @ZaverinBot", callback_data="set_bot_zaverin"))
    markup.add(types.InlineKeyboardButton(f"{status_osneh} @numbersearahsv_bot", callback_data="set_bot_osneh"))
    
    admin_bot.send_message(
        message.chat.id,
        f"🤖 **Number Search Bot Configuration** 🔧\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 **Current Bot:** {escaped_current_bot}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💡 **Select bot to use for number searches:**",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "set_bot_zaverin")
def set_bot_zaverin(call):
    global NUMBER_SEARCH_BOT_USERNAME
    
    old_bot = NUMBER_SEARCH_BOT_USERNAME
    NUMBER_SEARCH_BOT_USERNAME = "@ZaverinBot"
    
    # Escape underscores in bot usernames
    escaped_old_bot = old_bot.replace('_', '\\_')
    
    admin_bot.edit_message_text(
        f"✅ **Bot Changed Successfully!** 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 **Old Bot:** {escaped_old_bot}\n"
        f"🆕 **New Bot:** @ZaverinBot\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ All number searches will now use **@ZaverinBot**!",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    
    admin_bot.answer_callback_query(call.id, "✅ Switched to @ZaverinBot!", show_alert=True)

@admin_bot.callback_query_handler(func=lambda call: call.data == "set_bot_osneh")
def set_bot_osneh(call):
    global NUMBER_SEARCH_BOT_USERNAME
    
    old_bot = NUMBER_SEARCH_BOT_USERNAME
    NUMBER_SEARCH_BOT_USERNAME = "@numbersearahsv_bot"
    
    # Escape underscores in bot usernames
    escaped_old_bot = old_bot.replace('_', '\\_')
    
    admin_bot.edit_message_text(
        f"✅ **Bot Changed Successfully!** 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 **Old Bot:** {escaped_old_bot}\n"
        f"🆕 **New Bot:** @osnehfwj\\_bot\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ All number searches will now use **@osnehfwj\\_bot**!",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    
    admin_bot.answer_callback_query(call.id, "✅ Switched to @numbersearahsv_bot!", show_alert=True)

@admin_bot.message_handler(func=lambda message: message.text == "🔒 LOOKUP BLOCK")
def lookup_block_menu(message):
    with lookupblocked_lock:
        data = load_lookupblocked()
        total_count = len(data)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Add Username/UserID", callback_data="lb_add"),
        types.InlineKeyboardButton("📋 View All", callback_data="lb_view_all")
    )
    markup.add(
        types.InlineKeyboardButton("🗑️ Delete", callback_data="lb_delete")
    )
    
    admin_bot.send_message(
        message.chat.id,
        f"🔒 **LOOKUP BLOCK MANAGER** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Total Blocked:** {total_count}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Prevent users from looking up specific profiles:**\n\n"
        f"➕ **Add:** Block a username or User ID\n"
        f"📋 **View:** See all blocked profiles\n"
        f"🗑️ **Delete:** Unblock a profile",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "lb_add")
def lb_add(call):
    admin_bot.answer_callback_query(call.id, "✅ Send username or User ID")
    msg = admin_bot.send_message(
        call.message.chat.id,
        "➕ **Add to Block List** 🚫\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send a username or User ID:\n\n"
        "📝 **Format:** @username or 123456789\n\n"
        "❌ Send /cancel to cancel",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_lb_add)

def process_lb_add(message):
    if message.text and message.text.strip().lower() == '/cancel':
        admin_bot.send_message(message.chat.id, "❌ **Cancelled!**", parse_mode="Markdown")
        return
    
    query = message.text.strip()
    if query.startswith("@"):
        lookup_type = "username"
        query_normalized = query.lstrip('@')
    elif query.isdigit():
        lookup_type = "user_id"
        query_normalized = query
    else:
        admin_bot.send_message(message.chat.id, "❌ Invalid format! Use @username or user_id", parse_mode="Markdown")
        return
    
    add_to_lookupblocked(query_normalized, lookup_type)
    admin_bot.send_message(
        message.chat.id,
        f"✅ **Added to Block List!** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Query:** {query}\n"
        f"🔒 **Type:** {lookup_type}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Users cannot lookup this profile anymore.",
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "lb_view_all")
def lb_view_all(call):
    with lookupblocked_lock:
        data = load_lookupblocked()
    
    if not data:
        admin_bot.answer_callback_query(call.id, "No blocked profiles!")
        admin_bot.edit_message_text(
            "📋 **Block List** 📋\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ **Empty!** No profiles blocked.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        return
    
    entries = []
    for key, entry in data.items():
        query = entry.get('query', 'Unknown')
        lookup_type = entry.get('lookup_type', 'unknown')
        if lookup_type == "username":
            entries.append(f"👤 @{query}")
        else:
            entries.append(f"🆔 {query}")
    
    entries_text = "\n".join(entries[:50])
    if len(entries) > 50:
        entries_text += f"\n\n... and {len(entries) - 50} more"
    
    admin_bot.answer_callback_query(call.id, "✅ Loaded!")
    admin_bot.edit_message_text(
        f"📋 **Blocked Profiles** 🚫\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Total:** {len(entries)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{entries_text}",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

@admin_bot.callback_query_handler(func=lambda call: call.data == "lb_delete")
def lb_delete(call):
    admin_bot.answer_callback_query(call.id, "✅ Send username or User ID")
    msg = admin_bot.send_message(
        call.message.chat.id,
        "🗑️ **Remove from Block List** ✅\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send a username or User ID to unblock:\n\n"
        "📝 **Format:** @username or 123456789\n\n"
        "❌ Send /cancel to cancel",
        parse_mode="Markdown"
    )
    admin_bot.register_next_step_handler(msg, process_lb_delete)

def process_lb_delete(message):
    if message.text and message.text.strip().lower() == '/cancel':
        admin_bot.send_message(message.chat.id, "❌ **Cancelled!**", parse_mode="Markdown")
        return
    
    query = message.text.strip()
    if query.startswith("@"):
        lookup_type = "username"
        query_normalized = query.lstrip('@')
    elif query.isdigit():
        lookup_type = "user_id"
        query_normalized = query
    else:
        admin_bot.send_message(message.chat.id, "❌ Invalid format!", parse_mode="Markdown")
        return
    
    if remove_from_lookupblocked(query_normalized, lookup_type):
        admin_bot.send_message(
            message.chat.id,
            f"✅ **Removed from Block List!** ♻️\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Query:** {query}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Users can now lookup this profile.",
            parse_mode="Markdown"
        )
    else:
        admin_bot.send_message(message.chat.id, f"❌ **Not found** in block list!", parse_mode="Markdown")

@admin_bot.message_handler(func=lambda message: message.text == "📢 BROADCAST MESSAGE")
def broadcast_message(message):
    msg = admin_bot.send_message(
        message.chat.id,
        "📢 **Enter broadcast message for all users:**"
    )
    admin_bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    broadcast_text = message.text.strip()
    with users_lock:
        users = load_users()

    if not users:
        admin_bot.send_message(message.chat.id, "❌ **No users found.**")
        return

    success_count = 0
    fail_count = 0

    admin_bot.send_message(message.chat.id, f"📤 **Broadcasting to {len(users)} users...**")

    for user_id in users.keys():
        try:
            user_bot.send_message(int(user_id), broadcast_text)
            success_count += 1
            time.sleep(0.05)
        except:
            fail_count += 1

    admin_bot.send_message(
        message.chat.id,
        f"✅ **Broadcast completed!** 🎉\n\n"
        f"📊 **Statistics:**\n"
        f"✅ **Sent:** {success_count}\n"
        f"❌ **Failed:** {fail_count}",
        parse_mode="Markdown"
    )

# Asyncio event loop setup
async def run_user_bot_async():
    """Run user bot with asyncio"""
    global main_event_loop
    print("👥 User Bot: Starting...\n")

    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()
    main_event_loop = loop

    try:
        await loop.run_in_executor(
            executor,
            lambda: user_bot.infinity_polling(
                timeout=20,
                long_polling_timeout=20
            )
        )
    except Exception as e:
        print(f"👥 User Bot Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

async def run_admin_bot_async():
    """Run admin bot with asyncio"""
    print("🔐 Admin Bot: Starting...\n")

    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()

    try:
        await loop.run_in_executor(
            executor,
            lambda: admin_bot.infinity_polling(
                timeout=20,
                long_polling_timeout=20
            )
        )
    except Exception as e:
        print(f"🔐 Admin Bot Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

def cleanup_corrupted_sessions():
    """Remove corrupted or empty Pyrogram session files"""
    import os
    import glob

    print("🔍 Checking for corrupted session files...")
    session_files = glob.glob("*.session")
    cleaned_count = 0

    for session_file in session_files:
        try:
            # Check if file is empty or too small (corrupted)
            file_size = os.path.getsize(session_file)
            if file_size == 0:
                print(f"🗑️  Removing empty session file: {session_file}")
                os.remove(session_file)
                cleaned_count += 1
            elif file_size < 1024:  # Less than 1KB is likely corrupted
                print(f"⚠️  Warning: {session_file} is unusually small ({file_size} bytes)")
                print(f"🗑️  Removing potentially corrupted file: {session_file}")
                os.remove(session_file)
                cleaned_count += 1
        except Exception as e:
            print(f"⚠️  Could not check session file {session_file}: {e}")

    if cleaned_count > 0:
        print(f"✅ Cleaned up {cleaned_count} corrupted session file(s)")
    else:
        print(f"✅ No corrupted session files found")
    print()

# Flag to track if Pyrogram sessions are already initialized
_pyrogram_sessions_initialized = False

def ensure_pyrogram_session():
    """Ensure Pyrogram accounts are authenticated"""
    global _pyrogram_sessions_initialized

    # Skip if already initialized
    if _pyrogram_sessions_initialized:
        print("\n✅ Pyrogram sessions already authenticated (skipping re-initialization)")
        return True

    import logging
    import sys
    import os
    import io
    import threading

    # Clean up any corrupted session files first
    cleanup_corrupted_sessions()

    # Background error suppression using thread-local stderr capture
    class SuppressStderr:
        def __enter__(self):
            self.old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            return self

        def __exit__(self, *args):
            sys.stderr = self.old_stderr

    try:
        print("\n" + "="*60)
        print("🔐 PYROGRAM AUTHENTICATION")
        print("="*60)

        # Suppress ALL Pyrogram logging
        logging.getLogger("pyrogram").setLevel(logging.CRITICAL)
        logging.getLogger("pyrogram.session.session").setLevel(logging.CRITICAL)
        logging.getLogger("pyrogram.session.internals").setLevel(logging.CRITICAL)

        loop = get_pyrogram_loop()
        success = False

        # Authenticate number search client
        if number_search_client:
            try:
                print(f"\n📞 Authenticating Number Search Pyrogram...")
                print(f"📱 Phone: {NUMBER_SEARCH_PYROGRAM['phone']}")
                print(f"🆔 API ID: {NUMBER_SEARCH_PYROGRAM['api_id']}")
                print("\n⏳ Starting Pyrogram client...")
                print("📝 If asked for OTP, enter ONLY digits (no spaces/extra chars)")
                print("="*60 + "\n")
                sys.stdout.flush()

                with SuppressStderr():
                    future = asyncio.run_coroutine_threadsafe(number_search_client.start(), loop)
                    future.result()

                print("\n" + "="*60)
                print("✅ Number Search Pyrogram connected successfully!")
                print("="*60 + "\n")
                success = True
            except Exception as e:
                error_msg = str(e)
                print("\n" + "="*60)

                # Auto-fix AUTH_KEY_DUPLICATED error
                if "AUTH_KEY_DUPLICATED" in error_msg or "406" in error_msg:
                    session_file = f"{NUMBER_SEARCH_PYROGRAM.get('session_name', 'number_search_account')}.session"
                    print(f"🔧 AUTO-FIX: Detected duplicate session key for Number Search")
                    print(f"🗑️  Deleting corrupted session file: {session_file}")
                    try:
                        if os.path.exists(session_file):
                            os.remove(session_file)
                            print(f"✅ Session file deleted successfully!")
                            print(f"📝 Next run will ask for fresh OTP")
                        else:
                            print(f"⚠️  Session file not found (already deleted)")
                    except Exception as del_error:
                        print(f"⚠️  Could not delete session file: {del_error}")

                    print(f"\n💡 TIP: Make sure phone {NUMBER_SEARCH_PYROGRAM['phone']} is NOT logged in elsewhere")
                    print(f"   (Check Telegram app -> Settings -> Devices)")
                else:
                    print(f"❌ Number Search Pyrogram failed: {error_msg}")

                print("="*60 + "\n")

        # Authenticate username search clients (if configured)
        for idx, client in enumerate(username_search_clients):
            config = USERNAME_SEARCH_PYROGRAMS[idx]

            # Skip unconfigured accounts
            if config.get('api_id', 0) == 0 or not config.get('api_hash'):
                print(f"\n⚪ Skipping Account #{idx + 1} - Not configured")
                continue

            try:
                print(f"\n👤 Authenticating Username Search Pyrogram #{idx + 1}...")
                print(f"📱 Phone: {config.get('phone', 'Not set')}")
                print(f"🆔 API ID: {config.get('api_id', 'Not set')}")
                print("\n⚠️  IMPORTANT - OTP Entry:")
                print("   • Enter ONLY the OTP digits when prompted")
                print("   • Do NOT add spaces or extra characters")
                print("   • Press Enter after typing the code")
                print("="*60 + "\n")
                sys.stdout.flush()

                with SuppressStderr():
                    future = asyncio.run_coroutine_threadsafe(client.start(), loop)
                    future.result()

                print("\n" + "="*60)
                print(f"✅ Username Search Pyrogram #{idx + 1} connected successfully!")
                print("="*60 + "\n")
                success = True
            except Exception as e:
                error_msg = str(e)
                print("\n" + "="*60)

                # Auto-fix AUTH_KEY_DUPLICATED error
                if "AUTH_KEY_DUPLICATED" in error_msg or "406" in error_msg:
                    session_file = f"{config.get('session_name', f'username_search_account_{idx + 1}')}.session"
                    print(f"🔧 AUTO-FIX: Detected duplicate session key for Account #{idx + 1}")
                    print(f"🗑️  Deleting corrupted session file: {session_file}")
                    try:
                        if os.path.exists(session_file):
                            os.remove(session_file)
                            print(f"✅ Session file deleted successfully!")
                            print(f"📝 Next run will ask for fresh OTP for this account")
                        else:
                            print(f"⚠️  Session file not found (already deleted)")
                    except Exception as del_error:
                        print(f"⚠️  Could not delete session file: {del_error}")

                    print(f"\n💡 TIP: Make sure this phone number is NOT logged in elsewhere")
                    print(f"   (Check Telegram app -> Settings -> Devices)")
                else:
                    print(f"❌ Account #{idx + 1} failed: {error_msg}")

                print(f"⚠️  Continuing with other accounts...")
                print("="*60 + "\n")
                continue

        # Authenticate profile search client (if configured)
        if profile_search_client:
            try:
                print(f"\n📊 Authenticating Profile Search Pyrogram...")
                print(f"📱 Phone: {PROFILE_SEARCH_PYROGRAM['phone']}")
                print(f"🆔 API ID: {PROFILE_SEARCH_PYROGRAM['api_id']}")
                print("\n⚠️  IMPORTANT - OTP Entry:")
                print("   • Enter ONLY the OTP digits when prompted")
                print("   • Do NOT add spaces or extra characters")
                print("   • Press Enter after typing the code")
                print("="*60 + "\n")
                sys.stdout.flush()

                with SuppressStderr():
                    profile_loop = get_profile_search_loop()
                    future = asyncio.run_coroutine_threadsafe(profile_search_client.start(), profile_loop)
                    future.result()

                print("\n" + "="*60)
                print("✅ Profile Search Pyrogram connected successfully!")
                print("="*60 + "\n")
                success = True
            except Exception as e:
                error_msg = str(e)
                print("\n" + "="*60)

                # Auto-fix AUTH_KEY_DUPLICATED error
                if "AUTH_KEY_DUPLICATED" in error_msg or "406" in error_msg:
                    session_file = f"{PROFILE_SEARCH_PYROGRAM.get('session_name', 'profile_search_account')}.session"
                    print(f"🔧 AUTO-FIX: Detected duplicate session key for Profile Search")
                    print(f"🗑️  Deleting corrupted session file: {session_file}")
                    try:
                        if os.path.exists(session_file):
                            os.remove(session_file)
                            print(f"✅ Session file deleted successfully!")
                            print(f"📝 Next run will ask for fresh OTP")
                        else:
                            print(f"⚠️  Session file not found (already deleted)")
                    except Exception as del_error:
                        print(f"⚠️  Could not delete session file: {del_error}")

                    print(f"\n💡 TIP: Make sure phone {PROFILE_SEARCH_PYROGRAM['phone']} is NOT logged in elsewhere")
                    print(f"   (Check Telegram app -> Settings -> Devices)")
                else:
                    print(f"❌ Profile Search Pyrogram failed: {error_msg}")

                print("="*60 + "\n")

        # Restore logging level
        logging.getLogger("pyrogram").setLevel(logging.WARNING)

        if not success:
            print("⚠️ No Pyrogram accounts configured!")
            return False

        # Mark sessions as initialized
        _pyrogram_sessions_initialized = True
        print("\n✅ All Pyrogram sessions authenticated and saved!")
        return True
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ Pyrogram connection error: {e}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        return False

async def main_async():
    """Main async function to run both bots"""
    init_files()
    print("✅ Files initialized\n")

    # Ensure Pyrogram is authenticated BEFORE starting bots
    if not ensure_pyrogram_session():
        print("⚠️ Warning: Pyrogram not connected. Some features may not work.")

    print("🤖 Starting both bots...\n")

    # Run both bots concurrently
    await asyncio.gather(
        run_user_bot_async(),
        run_admin_bot_async()
    )

def main():
    """Entry point"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⚠️ Bots stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()