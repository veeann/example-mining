from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import language_check

base_url = ""
pages = []
nl_tool = language_check.LanguageTool('en-US')

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

	pages.append(url)
	soup = BeautifulSoup(resp.read(), "lxml")
	'''
	#currently checks only the given page
	#uncomment this part in order to crawl the website
	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = urljoin(base_url,link['href'])
			if next_link not in pages:
				get_links(next_link)
	'''
	extract(soup)

'''
finds code samples only based on NL errors
checking for punctuations to come soon
'''
def extract(page):
	for possible_code in page.findAll():
		if possible_code.name=='p' or possible_code.name=='pre':
			errors = nl_tool.check(possible_code.text)
			error_count = 0
			word_count = len(possible_code.text.split())
			for error in errors:
				error_count = error_count + 1
			error_ratio = float(error_count) / float(word_count)
			print possible_code.text
			print "errors: " + str(error_count) + " ratio: " + str(error_ratio)
			if error_ratio >= 0.5:
				print "SOURCE CODE \(*O*)/"
			else:
				print "NATURAL LANGUAGE (.____.)"
			print ""

parse_arguments()