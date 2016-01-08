'''
debug text are commented with #
'''
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse, urldefrag
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import language_check

base_url = ""
visited_pages = []
nl_tool = language_check.LanguageTool('en-US')
ERROR_RATIO_THRESHOLD = 0.5
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
	print "visiting: " + url

	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = urljoin(url,link['href'])
			next_link = urldefrag(next_link)[0]
			if next_link not in visited_pages:
				get_links(next_link)
	extract(soup)

'''
consider adding results of island parser to see if that will improve results since focus is only on Java
also add splitting for introductory sentences using : delimiter
'''
def extract(page):
	for possible_code in page.findAll():
		if possible_code.name=='p' or possible_code.name=='pre':
			error_ratio = get_error_ratio(possible_code.text)
			punctuation_ratio = get_punctuation_ratio(possible_code.text)
			if error_ratio >= ERROR_RATIO_THRESHOLD and punctuation_ratio >= PUNCTUATION_RATIO_THRESHOLD:
				# print "SOURCE CODE \(*O*)/"
				print possible_code.text
			# elif error_ratio < ERROR_RATIO_THRESHOLD and punctuation_ratio < PUNCTUATION_RATIO_THRESHOLD:
			# 	print "NATURAL LANGUAGE (.__.)"
			# else:
			# 	print "CONFUSED m(T__T)m"

def get_error_ratio (text):
	word_count = len(text.split())
	if word_count <= 0:
		return 0.0
	errors = nl_tool.check(text)
	error_count = len(errors)
	error_ratio = float(error_count) / float(word_count)
	#print "error count: " + str(error_count) + " error ratio: " + str(error_ratio)
	return error_ratio

'''
find a more efficient way to do this
'''
def get_punctuation_ratio (text):
	word_count = len(text.split())
	if word_count <= 0:
		return 0.0
	punctuation_count = text.count(';') + text.count('(') + text.count(')') + text.count('=')
	punctuation_ratio = float(punctuation_count) / float(word_count)
	#print "punctuation count: " + str(punctuation_count) + " punctuation ratio: " + str(punctuation_ratio)
	return punctuation_ratio

parse_arguments()