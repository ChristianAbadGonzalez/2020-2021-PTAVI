#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import urllib.request
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from smallsmilhandler import SmallSmilHandler


class KaraokeLocal:

    def __init__(self, filename):
        parser = make_parser()
        cHandler = SmallSmilHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(filename))
        self.list = cHandler.get_tags()

    def __str__(self):
        line = ""
        for tag in self.list:
            line += tag[0] + "\t"
            for att in tag[1]:
                line += att + "=\"" + tag[1][att] + "\"\t"
            line += "\n"
        return line

    def to_json(self, filename, filejson=""):
        if filejson == "":
            filejson = filename.replace("smil", "json")
        with open(filejson, "w") as jsonfile:
            json.dump(self.list, jsonfile, indent=2)

    def do_local(self):
        for tag in self.list:
            for att in tag[1]:
                if att == "src":
                    url = tag[1][att]
                    if len(url.split("http")) != 1:
                        filename = url.split("/")[-1]
                        urllib.request.urlretrieve(url, filename)
                        tag[1][att] = filename


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        karaoke = KaraokeLocal(filename)
        print(karaoke)
        karaoke.to_json(filename)
        karaoke.do_local()
        karaoke.to_json(filename, "local.json")
        print(karaoke)
    except IndexError:
        sys.exit("Usage Error: python3 karaoke.py file.smil")
    except FileNotFoundError:
        sys.exit("File " + filename + " not found")
