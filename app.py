import os
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

MAX_VOICE_DURATION = 5

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
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
        return "Webhook setup succeeded", 200
    return "Webhook setup failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
