'''
This program reads a file, checks the contents per block element, and outputs them if they are source code.

WARNING:
This is an experimental version where different methods are being tried.
The current method it is implementing is noted above.
It is full of debug text; variable names may not always be descriptive
'''
from collections import deque
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse, urldefrag
from argparse import ArgumentParser
from bs4 import BeautifulSoup, NavigableString
from lxml.html.clean import Cleaner
import lxml
import language_check
import re

base_url = ""
visited_pages = []
pages_to_visit = deque([])
count = 0
#nl_tool = language_check.LanguageTool('en-US')
BLOCK_ELEMENTS = ['article', 'aside', 'blockquote', 'div', 'main', 'p', 'pre', 'section']
ELEMENTS_TO_IGNORE = ['address', 'canvas', 'dd', 'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'li', 'nav', 'noscript', 'ol', 'output', 'table', 'tfoot', 'ul', 'video']
CAMEL_CASE_PATTERN = re.compile('[A-Z]*[a-z]+[A-Z]+')
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '[', ']']

ERROR_WEIGHT = 0.2
CODE_WEIGHT = 1.0
SCORE_TOTAL = ERROR_WEIGHT + CODE_WEIGHT

PUNCTUATION_WEIGHT = 0.9
PARENTHESIS_WEIGHT = 1.0
NEGATION_WEIGHT = 0.8
COMMENT_WEIGHT = 0.7
METHOD_WEIGHT = 0.5
IMPORT_WEIGHT = 0.8
CAMEL_WEIGHT = 0.7
CODE_TOTAL = PUNCTUATION_WEIGHT + PARENTHESIS_WEIGHT + NEGATION_WEIGHT + COMMENT_WEIGHT + METHOD_WEIGHT + IMPORT_WEIGHT + CAMEL_WEIGHT

SCORE_THRESHOLD = 0.1

def parse_arguments():
	parser = ArgumentParser(description='Accept Keywords from Users')
	# parser.add_argument('-u', '--url', help='URL of webpage to scrape from', required=True)
	parser.add_argument('-f', '--filename', help='Name of the file containing a list of webpages to scrape from', required=True)
	args = parser.parse_args()
	# global base_url
	# url_parts = urlparse(args.url)
	# url_path = url_parts.path
	# base_url = url_parts.scheme + '://' + url_parts.netloc + url_path
	# if url_path.rfind('/') < url_path.rfind('.'):
	# 	base_url = base_url[:base_url.rfind('/')]
	# visited_pages.append(args.url)
	# pages_to_visit.append(args.url)
	file_with_urls = open(args.filename, 'r')
	for line in file_with_urls.readlines():
		if line.strip()=="":
			break
		pages_to_visit.append(line)
	while len(pages_to_visit)>0:
		visit(pages_to_visit.popleft())

def visit(url):
	if url.startswith(base_url) == False:
		return

	try:
		resp = urlopen(url)
	except URLError as e:
		return

	page = resp.read()
	cleaner = Cleaner()
	cleaner.javasript = True
	cleaner.style = True
	cleaner.kill_tags = ELEMENTS_TO_IGNORE

	# soup = BeautifulSoup(page, "lxml")
	# for link in soup.findAll('a'):
	# 	if link.has_attr('href'):
	# 		if link.has_attr('class') and 'history' in link['class']:
	# 			continue
	# 		next_link = urljoin(url,link['href'])
	# 		next_link = urldefrag(next_link)[0]
	# 		if next_link not in visited_pages:
	# 			visited_pages.append(next_link)
	# 			pages_to_visit.append(next_link)
	f = open("testing.txt", 'w')
	f.write(page)

	clean_page = cleaner.clean_html(page)
	f.write("\n\n\nVS\n\n\n")
	f.write(clean_page)
	f.close()
	soup = BeautifulSoup(clean_page, "lxml")
	return
	extract(soup, url)

def extract(page, url):
	global count
	results_file = open("experiment-"+str(count)+".txt", 'w')
	count += 1
	results_file.write("visiting: " + url + "\n\n")
	for block in page.findAll(BLOCK_ELEMENTS):
		text = block.text
		if not block.find(BLOCK_ELEMENTS)==None:
			text = ""
			for next_text in block:
				if type(next_text)==NavigableString:
					text += next_text
		if not text.isspace():
			results_file.write(text.encode("utf-8")+"\n")
			if is_source_code(text):
				results_file.write("RESULT: SOURCE CODE!\n")
			else:
				results_file.write("RESULT: NATURAL LANGUAGE~\n")
			results_file.write("\n")
	results_file.close()
	print "Finished with: " + str(url) + " at file: experiment-" + str(count-1) + ".txt"

def is_source_code(text):
	return True
	text = clean(text)
	word_count = get_word_count(text)
	error_ratio = get_error_ratio(text, word_count) * ERROR_WEIGHT
	code_ratio = get_code_ratio(text, word_count) * CODE_WEIGHT
	score = error_ratio + code_ratio
	score = score / SCORE_TOTAL
	if score >= SCORE_THRESHOLD:
		return True
	return False

def clean (text):
	lines = text.replace('\r','\n').split("\n")
	new_text = ""
	for line in lines:
		if not line.strip()=="":
			new_text += line + "\n"
	return new_text

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
	camel_ratio = get_camel_case_occurrences(text) / float(word_count) * CAMEL_WEIGHT
	code_ratio = punctuation_ratio + parenthesis_ratio + negation_ratio + comment_ratio + method_ratio + import_ratio + camel_ratio
	code_ratio = code_ratio / CODE_TOTAL
	return code_ratio

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

def get_comment_occurrences (text):
	possible_comments = re.findall("//[ \t\r\f\v\S]+\n", text)
	comment_count = 0
	for result in possible_comments:
		if not is_source_code(result[2:].strip()):
			comment_count += 1
	return comment_count

def get_method_occurrences (text):
	method_count = len(re.findall("[a-zA-Z]+[a-zA-Z0-9_()\"]+\.[a-zA-Z]+", text))
	return method_count

def get_import_occurrences (text):
	import_count = len(re.findall("import [a-zA-Z0-9. ]+;", text))
	return import_count

def get_camel_case_occurrences (text):
	words = text.split()
	camel_count = 0
	for word in words:
		if CAMEL_CASE_PATTERN.match(word):
			camel_count += 1
	return camel_count

parse_arguments()