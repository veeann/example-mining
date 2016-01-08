'''
debug text are commented with #
'''
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse, urldefrag
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import language_check
import re

base_url = ""
visited_pages = []
nl_tool = language_check.LanguageTool('en-US')
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '/']
ERROR_RATIO_THRESHOLD = 0.43
PUNCTUATION_RATIO_THRESHOLD = 0.2

def parse_arguments():
	parser = ArgumentParser(description='Accept Keywords from Users')
	parser.add_argument('-u', '--url', help='URL of webpage to scrape from', required=True)
	args = parser.parse_args()
	global base_url
	global domain
	url_parts = urlparse(args.url)
	url_path = url_parts.path
	base_url = url_parts.scheme + '://' + url_parts.netloc + url_path
	if url_path.rfind('/') < url_path.rfind('.'):
		base_url = base_url[:base_url.rfind('/')]
	get_links(args.url)

def get_links(url):
	visited_pages.append(url)

	if url.startswith(base_url) == False:
		return

	try:
		resp = urlopen(url)
	except URLError as e:
		return

	page = resp.read()
	soup = BeautifulSoup(page, "lxml")
	#print "visiting: " + url

	'''
	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = urljoin(url,link['href'])
			next_link = urldefrag(next_link)[0]
			if next_link not in visited_pages:
				get_links(next_link)
	'''

	extract(soup)

'''
consider adding results of island parser to see if that will improve results since focus is only on Java
also add splitting for introductory sentences using : delimiter
'''
def extract(page):
	for possible_code in page.findAll():
		if possible_code.name=='p' or possible_code.name=='pre':
			'''
			maybe there is a better way to do this
			maybe this is not the right way
			'''
			words = possible_code.text.split()
			word_count = len(words)
			for word in words:
				if re.search('[a-zA-Z]', word) < 0:
					word_count -= 1
			error_ratio = get_error_ratio(possible_code.text, word_count)
			punctuation_ratio = get_punctuation_ratio(possible_code.text, word_count)
			print possible_code.text
			print word_count
			if error_ratio >= ERROR_RATIO_THRESHOLD and punctuation_ratio >= PUNCTUATION_RATIO_THRESHOLD:
				print "SOURCE CODE \(*O*)/"
			elif error_ratio < ERROR_RATIO_THRESHOLD and punctuation_ratio < PUNCTUATION_RATIO_THRESHOLD:
				print "NATURAL LANGUAGE (.__.)"
			else:
				print "CONFUSED m(T__T)m"
			print ""

def get_error_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	errors = nl_tool.check(text)
	error_count = len(errors)
	error_ratio = float(error_count) / float(word_count)
	print "error count: " + str(error_count) + " error ratio: " + str(error_ratio)
	return error_ratio

'''
find a more efficient way to do this
'''
def get_punctuation_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	punctuation_count = 0
	for punctuation in PUNCTUATION_LIST:
		punctuation_count += text.count(punctuation)
	punctuation_ratio = float(punctuation_count) / float(word_count)
	print "punctuation count: " + str(punctuation_count) + " punctuation ratio: " + str(punctuation_ratio)
	return punctuation_ratio

parse_arguments()