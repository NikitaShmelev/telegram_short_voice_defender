import os
import logging
from flask import Flask, request, jsonify
import telebot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
telebot.logger.setLevel(logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

MAX_VOICE_DURATION = 5

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    logger.info("Received voice message")
    if message.voice.duration <= MAX_VOICE_DURATION:
        bot.reply_to(message, "Please write text, such short voice messages are inconvenient to listen to.")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    status = bot.set_webhook(url=f"{WEBHOOK_HOST}/webhook")
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
        "has_custom_certificate": webhook_info.has_custom_certificate,
        "pending_update_count": webhook_info.pending_update_count,
        "ip_address": webhook_info.ip_address,
        "last_error_date": webhook_info.last_error_date,
        "last_error_message": webhook_info.last_error_message,
        "max_connections": webhook_info.max_connections,
        "allowed_updates": webhook_info.allowed_updates
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
