'''
debug text are commented with #
'''
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse
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
	base_url = args.url
	get_links(base_url)

def get_links(url):
	if url.startswith(base_url) == False:
		return

	try:
		resp = urlopen(url)
	except URLError as e:
		return

	visited_pages.append(url)
	page = resp.read()
	soup = BeautifulSoup(page, "lxml")

	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = urljoin(base_url,link['href'])
			'''
			the next three lines after this comment make sure that the same page isn't visited multiple times under "different" URLs
			checking is rather brute force and perhaps can still be improved
			'''
			end_index = next_link.rfind('/')+1
			if end_index<len(next_link) and next_link[end_index]=="#":
				next_link = next_link[:end_index]
			if next_link not in visited_pages:
				get_links(next_link)
	extract(soup)

'''
consider adding results of island parser to see if that will improve results since focus is only on Java
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
	errors = nl_tool.check(text)
	error_count = len(errors)
	word_count = len(text.split())
	error_ratio = float(error_count) / float(word_count)
	#print "error count: " + str(error_count) + " error ratio: " + str(error_ratio)
	return error_ratio

'''
find a more efficient way to do this
'''
def get_punctuation_ratio (text):
	word_count = len(text.split())
	punctuation_count = 0
	for index in range (len(text)):
		if text[index]==';' or text[index]=='(' or text[index]==')' or text[index]=='=':
			punctuation_count = punctuation_count + 1
	punctuation_ratio = float(punctuation_count) / float(word_count)
	#print "punctuation count: " + str(punctuation_count) + " punctuation ratio: " + str(punctuation_ratio)
	return punctuation_ratio

parse_arguments()