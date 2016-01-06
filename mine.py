import urllib2
import re
from urllib2 import urlopen, URLError
from urlparse import urlparse
from argparse import ArgumentParser
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag
from lxml import etree

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