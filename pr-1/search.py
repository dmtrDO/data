
import mysql.connector, webbrowser
from rapidfuzz import fuzz

class SearchEngine():
	def __init__(self):
		self.__query = "SELECT * FROM pages"

	def __connect_db(self):
		self.__cnx = mysql.connector.connect(
			host = '127.0.0.1',
			port = 3306,
			user = 'root',
			password = 'strongpassword123',
			database = 'pages'
		)

	def search(self, request):
		self.__connect_db()
		cur = self.__cnx.cursor()
		cur.execute(self.__query)
		all_pages = cur.fetchall()
		cur.close()
		self.__cnx.close()

		result = None
		best_score = 0
		print(len(all_pages))
		if len(all_pages) == 0:
			return result

		threshold = 50
		for idx, url, common_words in all_pages:
			curr_score = fuzz.token_set_ratio(request.lower(), str(common_words).lower())

			if curr_score > best_score:
				best_score = curr_score
				result = (idx, url, common_words, best_score)

		return result

search_engine = SearchEngine()

while True:
	try:
		request = input("\ninput search request: ")
		if request == "q":
			break
		result = search_engine.search(request)
		if result is None:
			print("No match results")
		else:
			print(result)
			webbrowser.open(str(result[1]))
			
	except Exception as e:
		print(e)

