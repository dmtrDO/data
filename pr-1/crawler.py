
# 4. Використати BeautifulSoup для парсингу
#  сторінки зі списком елементів, витягнути 
#  текст, почистити від зайвих пробілів та 
#  HTML-символів і порахувати топ-20 найчастіших слів.

from bs4 import BeautifulSoup
import asyncio, aiohttp, re, random
from mysql.connector.aio import connect
from collections import Counter


class Crawler():
	def __init__(self, seed_urls, headers, async_workers, max_pages, add_link):
		self.__seed_urls = seed_urls
		self.__headers = headers
		self.__crawl_frontier = asyncio.Queue()
		self.__db_queue = asyncio.Queue()
		self.__visited_sites = set()

		self.__query = "INSERT INTO pages (url, common_words) VALUES (%s, %s)"
		self.__async_workers = async_workers
		self.__max_pages = max_pages
		self.__add_link = add_link

	async def __connect_db(self):
		try:
			self.__cnx = await connect(
					host = '127.0.0.1',
					port = 3306,
					user = 'root',
					password = 'strongpassword123',
					database = 'pages'
				)
		except Exception as e:
			print(e)
			await self.__cnx.close()
			exit(1)

	async def crawl(self):
		await self.__connect_db()

		for url in self.__seed_urls:
			await self.__crawl_frontier.put(url)

		async with aiohttp.ClientSession() as session:
			workers = []
			for _ in range(self.__async_workers):
				workers.append(asyncio.create_task(self.__worker(session)))

			db_worker = asyncio.create_task(self.__db_worker())
			workers.append(db_worker)

			await self.__crawl_frontier.join()

			for worker in workers:
				worker.cancel()

	async def __worker(self, session):
		counter = 0
		while True:
			counter += 1
			url = await self.__crawl_frontier.get()
			try:
				if len(self.__visited_sites) >= self.__max_pages:
					continue

				if url in self.__visited_sites:
					continue

				self.__visited_sites.add(url)

				async with session.get(url, headers=self.__headers, timeout=10) as response:
					html_page = await response.text()

					soup = BeautifulSoup(html_page, "lxml")

					await self.__update_links(soup)

					filtered_words = Crawler.__filter_page(soup)
					words = Counter(filtered_words)
					common_words = words.most_common(20)
					if len(common_words) < 20:
						continue
					common_words_str = ""
					for common in common_words:
						common_words_str += str(common[0]) + " "

					if counter % 10 == 0:
						print(url)
					await self.__db_queue.put((url, common_words_str.strip()))
			except Exception as e:
				print(e)
			finally:
				self.__crawl_frontier.task_done()

	async def __db_worker(self):
		batch = []
		while True:
			url, common_words = await self.__db_queue.get()
			if len(url) >= 500:
				self.__db_queue.task_done()
				continue
			batch.append((url, common_words))

			if len(batch) >= self.__async_workers or self.__db_queue.empty():
				try:
					cur = await self.__cnx.cursor()
					await cur.executemany(self.__query, batch)
					await self.__cnx.commit()
					await cur.close()
					batch = []
				except Exception as e:
					print(e)

			self.__db_queue.task_done()

	async def __update_links(self, b_soup):
		if len(self.__visited_sites) >= self.__max_pages:
			return

		links = b_soup.find_all("a", href=True)
		http_links = []
		for link in links:
			if str(link.get('href')).startswith("http"):
				http_links.append(link.get('href'))

		random.shuffle(http_links)

		for _ in range(self.__add_link):
			if len(http_links) > 0:
				url = http_links.pop()
				if url not in self.__visited_sites:
					await self.__crawl_frontier.put(url)
			else:
				break

	@classmethod
	def __filter_page(cls, b_soup):
		text = b_soup.get_text(" ")
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


seed_urls = [
    "https://www.wikipedia.org",
    "https://www.bbc.com",
    "https://www.cnn.com",
    "https://stackoverflow.com",
    "https://github.com",
    "https://reddit.com",
    "https://www.bbc.com/ukrainian",
    "https://news.ycombinator.com/",
    "https://www.pravda.com.ua/",
    "https://pypi.org/",
    "https://www.nytimes.com",
    "https://www.theguardian.com",
    "https://medium.com",
    "https://news.ycombinator.com"
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}

try:
	crawler = Crawler(seed_urls, headers, 50, 1e6, 4)
	asyncio.run(crawler.crawl())
except Exception as e:
	print(e)


