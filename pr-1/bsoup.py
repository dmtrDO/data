
# 4. Використати BeautifulSoup для парсингу
#  сторінки зі списком елементів, витягнути 
#  текст, почистити від зайвих пробілів та 
#  HTML-символів і порахувати топ-20 найчастіших слів.

from bs4 import BeautifulSoup
import requests
import re
from collections import Counter


class Crawler():
	def __init__(self, urls, headers):
		self.__urls = urls
		self.__headers = headers
		self.__sites = {}

	def request_handler(self):
		for url in self.__urls:
			request = requests.get(url, headers=self.__headers)

			if request.url in self.__sites or request.status_code != 200:
				print(f"{request.status_code}: {request.url}")
				continue

			html_page = BeautifulSoup(request.text, "lxml")
			filtered_words = Crawler.__filter_page(html_page)

			counter = Counter(filtered_words)
			self.__sites[request.url] = {
										"title": html_page.find("title").text, #type:ignore
										"words": []
									}
			for word, _ in counter.most_common(20):
				self.__sites[request.url]["words"].append(word)

		return self.__sites

	@classmethod
	def __filter_page(cls, html_page):
		text = html_page.get_text(" ")
		text = re.sub(r"\s+", " ", text.lower())
		words = re.findall(r"\b[а-яa-zіїє]+\b", text)
		words_to_delete = {
    		"з", "не", "для", "у", "в", "й", "а", "як", "або", "є",
    		"і", "та", "на", "так", "що", "об", "до", "за", "при", "від",
    		"in", "at", "on", "of", "to", "for", "and", "but", "or", 
    		"because", "if", "a", "an", "the", "do", 
    		"does", "did", "have", "has", "will", "not"
		}
		filtered_words = []
		for word in words:
			if word not in words_to_delete:
				filtered_words.append(word)
		return filtered_words


urls = [
    "https://www.wikipedia.org",
    "https://www.bbc.com",
    "https://www.cnn.com",
    "https://stackoverflow.com",
    "https://github.com",
    "https://reddit.com",
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}

crawler = Crawler(urls, headers)
sites = crawler.request_handler()
for url, data in sites.items():
	print(url)
	print(data['title'])
	print(data['words'])
	print("-"*40)


