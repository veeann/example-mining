import urllib2
import re
from urllib2 import urlopen, URLError
from urlparse import urlparse
from argparse import ArgumentParser
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag
from lxml import etree

base_url = ""
domain = ""
pages = []

def parse_arguments():
	parser = ArgumentParser(description='Accept Keywords from Users')
	parser.add_argument('-u', '--url', help='URL of webpage to scrape from', required=True)
	args = parser.parse_args()
	global base_url
	global domain
	base_url = args.url
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(base_url))
	domain = domain[:-1]

	get_links(base_url)

def get_links(url):
	try:
		if url.index(base_url) != 0:
			return
	except ValueError as e:
		return

	try:
		resp = urlopen(url)
	except URLError as e:
		return

	print "checked " + url 

	pages.append(url)
	soup = BeautifulSoup(resp.read(), "lxml")
	for link in soup.findAll('a'):
		if link.has_attr('href'):
			next_link = link['href']
			if next_link.startswith('/'):
				next_link = domain + next_link
			if next_link not in pages:
				get_links(next_link)

def get_next (current):
	try:
		for child in current.children:
			return child
	except AttributeError:
		if current.nextSibling!=None:
			return current.nextSibling
		if current.parent!=None:
			if current.parent.nextSibling!=None:
				return current.parent.nextSibling
	return None

def main():
	parse_arguments()

	for link in pages:
		print link

	#2. Represent page as navigable structure
	#toParse = open("page.html", "r")
	#soup = BeautifulSoup(toParse,"lxml")


main()