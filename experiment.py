'''
trying out different methods
full of debug text
variable names may not always be descriptive
'''
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse, urldefrag
from argparse import ArgumentParser
from bs4 import BeautifulSoup, UnicodeDammit
import language_check
import re

nl_tool = language_check.LanguageTool('en-US')
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '/']
ERROR_RATIO_THRESHOLD = 0.43
PUNCTUATION_RATIO_THRESHOLD = 0.2

def parse_arguments():
	parser = ArgumentParser(description='Accept Keywords from Users')
	parser.add_argument('-u', '--url', help='URL of webpage to scrape from', required=True)
	args = parser.parse_args()
	get_links(args.url)

def get_links(url):
	try:
		resp = urlopen(url)
	except URLError as e:
		return

	page = resp.read()
	dammit = UnicodeDammit.detwingle(page)
	soup = BeautifulSoup(dammit.decode("utf8"), "lxml")
	extract(soup)

def extract(page):
	for line in page.html.text.splitlines():
		#print line.encode("utf-8")
		word_count = get_word_count(line)
		if get_punctuation_ratio(line, word_count) >= PUNCTUATION_RATIO_THRESHOLD:
			print line.encode("utf-8")

def get_word_count (text):
	words = text.split()
	word_count = len(words)
	for word in words:
		if re.search('[a-zA-Z]', word) < 0:
			word_count -= 1
	return word_count

def get_error_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	errors = nl_tool.check(text)
	error_count = len(errors)
	error_ratio = float(error_count) / float(word_count)
	#print "error count: " + str(error_count) + " error ratio: " + str(error_ratio)
	return error_ratio

def get_punctuation_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	punctuation_count = 0
	for punctuation in PUNCTUATION_LIST:
		punctuation_count += text.count(punctuation)
	punctuation_ratio = float(punctuation_count) / float(word_count)
	#print "punctuation count: " + str(punctuation_count) + " punctuation ratio: " + str(punctuation_ratio)
	return punctuation_ratio

parse_arguments()

'''
RULES to try:
import with ;
{ }
x.x
// comment
!x
()
'''