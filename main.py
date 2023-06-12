import logging
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, ContextTypes, MessageHandler, filters
import json
import uuid

# Replace your_bot_token with the actual bot token from BotFather
TOKEN = "5526713521:AAEljrEWYhpZsx2x2NF-3yI-X4VuKNBkjws"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

# Stages
NAME, LOCATION, TITLE, DESCRIPTION, MONEY, WALLET = range(6)

# Command handlers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(chat_id='@bigcryptoaids', user_id=user_id)
    except:
        await update.message.reply_text("You must join @bigcryptoaids channel first!")
        return ConversationHandler.END

    await update.message.reply_text("Welcome to CryptoAid! Please enter your name.")
    return NAME

# Define a dictionary to store the last post timestamp for each user
user_last_post = {}

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Thank you. Please enter your location.")
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text("Great! Now, please enter the title of your request.")
    return TITLE


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Now, please provide a description of your request.")
    return DESCRIPTION


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text("Can you tell me how much money you need?")
    return MONEY


async def money(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['money'] = update.message.text
    await update.message.reply_text("Lastly, please provide your wallet address.")
    return WALLET


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['wallet'] = update.message.text
    await update.message.reply_text("Thank you. Your request has been recorded.")

    user_id = update.effective_user.id

    # Check if the user has made a post within the past 24 hours
    if user_id in user_last_post and time.time() - user_last_post[user_id] < 24 * 60 * 60:
        await update.message.reply_text("You can only make one post per day. Please try again tomorrow.")
        return ConversationHandler.END
    
    # Update the last post timestamp for the user
    user_last_post[user_id] = time.time()
    

    # Format the information into a post template
    post = f"🔔 New Request 🔔\n\n👤 Name: {context.user_data['name']}\n📍 Location: {context.user_data['location']}\n📜 Title: {context.user_data['title']}\n💬 Description: {context.user_data['description']}\n💰 Money Needed: {context.user_data['money']}\n🔗 Wallet: {context.user_data['wallet']}"

    # Replace 'yourchannel' with the actual username of your channel
    await context.bot.send_message(chat_id='@bigcryptoaids', text=post)

    # Save the request in the database or file-based storage
    save_request(context.user_data)

    return ConversationHandler.END



def save_request(request_data):
    # Load existing requests from storage
    stored_requests = load_requests()

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Add the new request to the dictionary
    stored_requests[request_id] = request_data

    # Save the updated requests dictionary to storage
    save_requests(stored_requests)

def load_requests():
    # Implement the code to load existing requests from storage
    # Read the requests from a file
    try:
        with open('requests.json', 'r') as f:
            stored_requests = json.load(f)
            return stored_requests
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty dictionary
        return {}

def save_requests(stored_requests):
    # Implement the code to save the updated requests to storage
    # Write the requests to a file
    with open('requests.json', 'w') as f:
        json.dump(stored_requests, f)


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            MONEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, money)],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
