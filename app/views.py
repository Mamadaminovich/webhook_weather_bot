from django.shortcuts import render, HttpResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import path
import telebot
import requests

def home(context):
    return HttpResponse('Salom Dunyo!!!')

from googletrans import Translator

BOT_TOKEN = '7004165241:AAEINcsXbHR67RNYPuygPkfm2JAfRErl3Es'
API_KEY = 'eaa7ae462493aaf974882e3683aaa449'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

@csrf_exempt
@require_POST
def webhook(request):
    json_str = request.body.decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return HttpResponse(status=200)

def get_weather_icon(weather_id):
    if weather_id < 300:
        return '⛈️'
    elif weather_id < 600:
        return '🌧️'
    elif weather_id < 700:
        return '🌨️'
    elif weather_id == 800:
        return '☀️'
    else:
        return '☁️'

def get_weather_info(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        city_name = city.capitalize()
        weather_desc = data['weather'][0]['description']
        weather_id = data['weather'][0]['id']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        icon_code = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        weather_icon = get_weather_icon(weather_id)
        dc = translator.translate(weather_desc.capitalize(), dest='uz')
        weather_info = (
            f"Shahar: {city_name}\n"
            f"Ob-Havo: {dc.text} {weather_icon}\n"
            f"Harorat: {temperature}°C\n"
            f"his qilish: {feels_like}°C"
        )
    else:
        weather_info = 'Hatolik yuz berdi. Iltimos qayta urinib ko\'ring'

    return weather_info

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Assalomu Aleykum ob-havo ☀️ botiga hush kelibsiz!\n\nQaysi shahar ob-havosini bilmoqchisiz?")

@bot.message_handler(func=lambda message: True)
def handle_city(message):
    city = message.text
    weather_info = get_weather_info(city)
    bot.reply_to(message, weather_info)


WEBHOOK_URL = 'https://4335-213-230-76-133.ngrok-free.app'
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)
