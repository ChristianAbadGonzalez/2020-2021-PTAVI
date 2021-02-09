#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SmallSmilHandler(ContentHandler):

	def __init__(self):
		self.list = []
		self.attr = {"root-layout": ["width", "height", "background-color"],
				     "region": ["id", "top", "bottom", "left", "right"],
					 "img": ["src", "region", "begin", "dur"],
					 "audio": ["src", "begin", "dur"],
					 "textstream": ["src", "region"]}

	def startElement(self, name, attrs):

		if name in self.attr:
			dicc = {}
			for atributo in self.attr[name]:
				dicc[atributo] = attrs.get(atributo, "")

			self.list.append([name, dicc])

	def get_tags(self):
		return self.list


if __name__ == "__main__":

	parser = make_parser()
	cHandler = SmallSmilHandler()
	parser.setContentHandler(cHandler)
	parser.parse(open('karaoke.smil'))
	print(cHandler.get_tags())
