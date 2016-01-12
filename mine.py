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
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '[', ']']

'''
highest ratio is equal to weight
'''
ERROR_WEIGHT = 0.4
CODE_WEIGHT = 1.0
SCORE_TOTAL = ERROR_WEIGHT + CODE_WEIGHT

'''
ratios range from 0-1 without weight, highest is weight with weight
get decimal percentage of total to limit to 1
'''
PUNCTUATION_WEIGHT = 0.7
PARENTHESIS_WEIGHT = 1.0
NEGATION_WEIGHT = 0.8
COMMENT_WEIGHT = 0.7
METHOD_WEIGHT = 0.5
IMPORT_WEIGHT = 0.8
CODE_TOTAL = PUNCTUATION_WEIGHT + PARENTHESIS_WEIGHT + NEGATION_WEIGHT + COMMENT_WEIGHT + METHOD_WEIGHT + IMPORT_WEIGHT

SCORE_THRESHOLD = 0.1

def parse_arguments():
	parser = ArgumentParser(description='Accept Keywords from Users')
	parser.add_argument('-u', '--url', help='URL of webpage to scrape from', required=True)
	args = parser.parse_args()
	global base_url
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
use UnicodeDammit so encoding isn't hardcoded
'''
def extract(page):
	for possible_code in page.findAll():
		if possible_code.name=='p' or possible_code.name=='pre':
			print "analyzing:"
			print possible_code.text.encode("utf-8")
			if is_source_code(possible_code.text):
				print "RESULT: SOURCE CODE \(*O*)/"
			else:
				print "RESULT: NATURAL LANGUAGE (.__.)"
			print ""

def is_source_code(text):
	word_count = get_word_count(text)
	error_ratio = get_error_ratio(text, word_count) * ERROR_WEIGHT
	code_ratio = get_code_ratio(text, word_count) * CODE_WEIGHT
	score = error_ratio + code_ratio
	score = score / SCORE_TOTAL
	print "score: " + str(score)
	if score >= SCORE_THRESHOLD:
		return True
	return False

'''
maybe there is a better way to do this
maybe this is not the right way
'''
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
	return error_ratio

def get_code_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	punctuation_ratio = get_punctuation_occurrences(text)  / float(word_count) * PUNCTUATION_WEIGHT
	parenthesis_ratio = get_parentheses_occurrences(text)  / float(word_count) * PARENTHESIS_WEIGHT
	negation_ratio = get_negation_occurrences(text)  / float(word_count) * NEGATION_WEIGHT
	comment_ratio = get_comment_occurrences(text)  / float(word_count) * COMMENT_WEIGHT
	method_ratio = get_method_occurrences(text)  / float(word_count) * METHOD_WEIGHT
	import_ratio = get_import_occurrences(text)  / float(word_count) * IMPORT_WEIGHT
	code_ratio = punctuation_ratio + parenthesis_ratio + negation_ratio + comment_ratio + method_ratio + import_ratio
	code_ratio = code_ratio / CODE_TOTAL
	return code_ratio

'''
find a more efficient way to do this if possible
'''
def get_punctuation_occurrences (text):
	punctuation_count = 0
	for punctuation in PUNCTUATION_LIST:
		punctuation_count += text.count(punctuation)
	return punctuation_count

def get_parentheses_occurrences (text):
	parenthesis_count = text.count("()")
	return parenthesis_count

def get_negation_occurrences (text):
	negation_count = len(re.findall("![a-zA-Z=]+", text))
	return negation_count

'''
possibly include asterisks for comments
'''
def get_comment_occurrences (text):
	possible_comments = re.findall("//[ \t\r\f\v\S]+", text)
	comment_count = 0
	for result in possible_comments:
		if not is_source_code(result[2:]):
			comment_count += 1
	return comment_count

def get_method_occurrences (text):
	method_count = len(re.findall("[a-zA-Z]+[a-zA-Z0-9_()\"]+\.[a-zA-Z]+", text))
	return method_count

def get_import_occurrences (text):
	import_count = len(re.findall("import [a-zA-Z0-9. ]+;", text))
	return import_count

parse_arguments()