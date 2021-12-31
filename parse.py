import requests, re, os, json
import urllib
from bs4 import BeautifulSoup

URL = 'http://new.vtk-portal.ru/studentam/raspisanie-zanyatiy.php'  #Ссылка на сайт колледжа с расписанием
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}

responce = requests.get(URL, allow_redirects=True)
soup = BeautifulSoup(responce.content, 'html.parser')
#Отделение ссылок от остального
block = soup.find('div', class_ = 'content')
all_link = block.find_all('a')

for link in all_link:
    if type(link) != type(None):
        if link.get('href') != None:  #Запись ссылок если они есть
            links = link.get('href')
            print(links)
print(all_link)
