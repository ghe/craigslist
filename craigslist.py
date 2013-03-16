#!/usr/bin/python
import sys
import time
import datetime
import re
import urllib2
import xml.etree.ElementTree as ET
import signal

import mail

def clean_tag(node):
    tag = node.tag
    i = tag.find('}')
    if i > -1 and i < len(tag):
        tag = tag[i+1:]
    return tag

def get_year(text):
    m = re.search("((19|20)[0-9]{2}[^0-9])", text)
    return m.group(1)[:4] if m else None

def get_mileage(text):
    m = re.search("(?<!\$)(?!83)([0-9]{5,6}|[0-9]{2,3}[kK]|[0-9]{2,3},[0-9]{3})", text)
    return m.group(1) if m else None

def get_location(text):
    m = re.search("\((.*)\)", text)
    return m.group(1) if m else None

def get_price(text):
    m = re.search("\$([0-9,]*)", text)
    if m:
        pricestr = m.group(1)
        return re.sub(r'[^\d.]+', '', pricestr)
    return None

def get_query(text):
    m = re.search("query=(.*)&", text)
    return m.group(1) if m else None

def parse_response(response):
    entries = {}
    root = ET.fromstring(response)
    query = None
    for item in root:
        tag = clean_tag(item)
        if tag == "channel":
            for field in item:
                tag = clean_tag(field)
                if tag == "link":
                    query = get_query(field.text)
        elif tag == "item":
            price = None
            location = None
            mileage = None
            year = None
            date = None
            link = None
            for field in item:
                tag = clean_tag(field)
                if tag in ["title", "description"]:
                    if tag == "title":
                        if location is None:
                            location = get_location(field.text)
                    if year is None:
                        year = get_year(field.text)
                    if mileage is None:
                        mileage = get_mileage(field.text)
                    if price is None:
                        price = get_price(field.text)
                elif tag == "date":
                    d = field.text[:field.text.find('T')]
                    date = datetime.datetime.strptime(d, "%Y-%m-%d")
                elif tag == "link":
                    link = field.text
                #else: print "tag: %s" % (tag,)
            try:
                y = int(year)
                if y >= 1996:
                    if date > datetime.datetime.now() - datetime.timedelta(days=7):
                        d = date.strftime("%a %b %d")
                        if float(price) < 15000:
                            entries[link] = "%s: %s, year %s, mileage %s, price %s, location %s (%s)" % (
                               query, d, y, mileage, price, location, link)
            except:
                pass
    return entries

def ctrl_c(signal, frame):
    print "exiting..."
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, ctrl_c)
    already_sent = {}

    if len(sys.argv) > 4:
        queries = open(sys.argv[1]).read().splitlines()
        emails = open(sys.argv[2]).read().splitlines()
        account = sys.argv[3]
        password = sys.argv[4]

        while(True):
            print "checking craigslist..."
            entries = {}

            try:
                for q in queries:
                    d = parse_response(urllib2.urlopen(q).read())
                    entries.update(d)
            except Exception as e:
                print "URL parsing error({0}): {1}".format(e.errno, e.strerror)

            msg = ""
            for key, value in entries.items():
                if key not in already_sent:
                    msg += "%s\n" % (value,)
                    already_sent[key] = value
            if len(msg) > 0:
                print msg
                try:
                    mail.send_gmail(account, password, emails, "craigslist scrub", msg)
                    pass
                except Exception as e:
                    print "mail sending error({0}): {1}".format(e.errno, e.strerror)

            for i in range(10):
                print "sleeping for %d more minutes" % (10 - i,)
                time.sleep(60)
    else:
        print "usage: %s <queryfile> <emailfile> <gmail account> <password>"
