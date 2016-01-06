from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse
from argparse import ArgumentParser
from bs4 import BeautifulSoup

base_url = ""
pages = []

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
	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = urljoin(base_url,link['href'])
			if next_link not in pages:
				get_links(next_link)

	print "page: " + url
	extract(soup)

def extract(page):
	for possible_code in page.findAll('pre'):
		print possible_code.text

parse_arguments()