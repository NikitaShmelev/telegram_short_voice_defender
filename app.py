import os
import logging
from flask import Flask, request, jsonify
import telebot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

MAX_VOICE_DURATION = 5

@bot.business_message_handler(func=lambda message: message.content_type == 'voice')
def handle_business_voice(message):
    logger.info("Received business voice message")
    if message.voice.duration <= MAX_VOICE_DURATION:
        bot.send_message(
            chat_id=message.chat.id,
            text="Please write text, such short voice messages are inconvenient to listen to.",
            reply_to_message_id=message.message_id,
            business_connection_id=message.business_connection_id
        )
        logger.info("Successfully replied to business voice message")

@bot.message_handler(func=lambda message: message.content_type == 'voice')
def handle_regular_voice(message):
    logger.info("Received regular voice message")
    if message.voice.duration <= MAX_VOICE_DURATION:
        bot.send_message(
            chat_id=message.chat.id,
            text="Please write text, such short voice messages are inconvenient to listen to.",
            reply_to_message_id=message.message_id
        )
        logger.info("Successfully replied to regular voice message")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        logger.info(f"Raw update received: {json_string}") 
        
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    status = bot.set_webhook(
        url=f"{WEBHOOK_HOST}/webhook",
        allowed_updates=["message", "business_message"]
    )
    if status:
        logger.info("Webhook setup succeeded")
        return "Webhook setup succeeded", 200
    logger.error("Webhook setup failed")
    return "Webhook setup failed", 500

@app.route('/check_webhook', methods=['GET'])
def check_webhook():
    webhook_info = bot.get_webhook_info()
    return jsonify({
        "url": webhook_info.url,
        "pending_update_count": webhook_info.pending_update_count,
        "last_error_message": webhook_info.last_error_message,
        "allowed_updates": webhook_info.allowed_updates
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)