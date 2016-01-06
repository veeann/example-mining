import urllib2
import re
from urllib2 import urlopen, URLError
from urlparse import urljoin, urlparse
from argparse import ArgumentParser
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag
from lxml import etree

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

def extract(link):
	try:
		resp = urlopen(link)
	except URLError as e:
		return

	soup = BeautifulSoup(resp.read(), "lxml")
	count =0
	for possible_code in soup.findAll('pre'):
		print count
		print possible_code.text
		count += 1


extract('https://github.com/cglib/cglib/wiki/Tutorial')