
# 4. Використати BeautifulSoup для парсингу
#  сторінки зі списком елементів, витягнути 
#  текст, почистити від зайвих пробілів та 
#  HTML-символів і порахувати топ-20 найчастіших слів.

from bs4 import BeautifulSoup
import requests
import re
from collections import Counter

url = 'https://uk.wikipedia.org/wiki/Python'

file_path = "index.html"
request = requests.get(url, headers={"User-Agent": ""})

if request.status_code != 200:
	print(f"{request.status_code}")
	print(f"{request.text}")
	exit(1)

with open(file_path, 'w') as f:
	f.write(request.text)

with open(file_path, 'r') as html_file:
	content = html_file.read()

doc = BeautifulSoup(content, "lxml")

text = doc.get_text(" ")

text = re.sub(r"\s+", " ", text)
text = text.lower()

words = re.findall(r"\b[а-яa-zіїє]+\b", text)
words_to_delete = {
    "з", "не", "для", "у", "в", "й", "а", "як", "або", "є",
    "і", "та", "на", "так", "що", "об", "до", "за", "при", "від"
}

filtered_words = []
for word in words:
	if word not in words_to_delete:
		filtered_words.append(word)

counter = Counter(filtered_words)

for word, count in counter.most_common(20):
	print(f"{count}: {word}")


