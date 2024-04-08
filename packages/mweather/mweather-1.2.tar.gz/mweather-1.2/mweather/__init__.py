import os
import requests
import time

try:
	from bs4 import BeautifulSoup
except:
	os.system("pip install bs4")
	from bs4 import BeautifulSoup

def weather(city, output='string', lang='en'):
    if output != 'calendar':
        try:
            city = city.replace(' ', '+')
            if lang == 'en': lang = 'weather'; reqlan = 'en-US,en;q=0.8'
            elif lang =='ru': lang = 'погода'; reqlan = 'ru-RU,ru;q=0.9'
            headers = {
            'Accept-Language': reqlan
            }
            last_time = time.time()
            req = requests.get(f'https://google.com/search?q={city}+{lang}', headers=headers)
            now_time = time.time() - last_time
            now_time = round(now_time, 2)
            soup = BeautifulSoup(req.text, 'html.parser')
    
            info = soup.select('.BNeawe.tAd8D.AP7Wnd')[1].getText().strip().split('\n')
            weather = soup.select('.BNeawe.iBp4i.AP7Wnd')[1].getText().strip()
    
            if output == 'string':
                return f'{info[1]}, {weather}'
            elif output == 'json':
                return {"weather": info[1], "temp": weather, "response-time": now_time}
            elif output == 'temp':
                return weather
            elif output == 'weather':
                return info[1]
        except IndexError as ex:
            return f'Error: this city was not found./Этот город не найден.'
        except Exception as ex:
            return f'Error: {ex}'
    elif output == 'calendar':
        city = city.replace(' ', '%20')
        req = requests.get(f'https://wttr.in/{city}?lang={lang}')
        retrn = req.text
        retrn = retrn.replace('Все новые фичи публикуются здесь', '').replace('@igor_chubin', '')
        return retrn