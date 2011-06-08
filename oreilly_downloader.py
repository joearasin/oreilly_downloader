#!/usr/bin/env python

import httplib
import ConfigParser, os, sys, getpass
import cookielib, urllib, urllib2
import argparse
import pprint
from BeautifulSoup import BeautifulSoup

class OReillyBooks():
    def __init__(self, email, password):
        """ Initializes the class, getting cookies in order to download things"""
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.login(email, password)
        self._load_book_info()
  
    def login(self, email, password):
        """ Logs into the O'Reilly members website, using the specified e-mail address and password, in order to set cookies in the opener"""
        r = self.opener.open("https://members.oreilly.com/account/login")
        soup = BeautifulSoup(r.read())
        auth_token = soup.find("input",{ "id" : "_authentication_token"})['value']
        params = urllib.urlencode({'email': email, 'password': password, '_authentication_token': auth_token})
        r = self.opener.open("https://members.oreilly.com/account/login", params)
  
    def _load_book_info(self):
        r = self.opener.open("https://members.oreilly.com/account/emedia")
        book_html = BeautifulSoup(r.read())
        parsed_books = [self._parse_book(book) for book in book_html.find(id="ebooks").findAll("li","product-block")]
        self.books = dict([(book['title'],book) for book in parsed_books])
  
    def download_all_books(self, formats):
        """Downloads all books in specified formats"""
        [self.download_book(book,formats) for book in self.books.keys()]
  
    def download_books(self, titles, formats):
        [self.download_book(book,formats) for book in titles]
  
    def download_book(self, title, formats = []):
        """Downloads a specified book in specified formats"""
        if isinstance(formats, basestring):
            formats = [formats]
    
        for format in formats:
            try:
                book = self.opener.open(self.books[title]['download_links'][format.lower()])
                output = open(title+'.'+format, 'wb')
                output.write(book.read())
                output.close
            except:
                print 'Unable to download %(book)s in %(format)s' % {"book": title, "format": format}
  
    def _parse_book(self, info):
        book_info = {}
        book_info['title'] = info.h4.a.string if info.h4.a else info.h4.string
        book_info['author'] = info.p.string[3:] if info.p else ""
        book_info['download_links'] = dict([(link.string.lower(),link['href']) 
            for link in info.find("ul","formats")('a')])
        return book_info

def get_login():
    # Attempts to read login from configuration file. If does not exist, prompts for one
    config = ConfigParser.ConfigParser()
    email = None
    password = None
    try:
        config.read(os.path.expanduser("~/.scriptconfig"))
        email = config.get('oreilly', 'email')
        password = config.get('oreilly', 'password')
    except:
        if email is None:
            email = raw_input("Email Address: ")
        if password is None:
            password = getpass.getpass()
    return email, password
    
def list(books, args):
    title_width = len(max(books.books.keys(), key=len))
    author_width = max(len(book['author']) for book in books.books.values())
    print "\033[1m%s\t%s\t%s\033[0m" % ("Title".ljust(title_width),"Author".ljust(author_width),"Formats")
    for title, book in sorted(books.books.items()):
        print "%s\t%s\t%s" % (title.ljust(title_width),book['author'].ljust(author_width),",".join(book['download_links'].keys()))
    
def download(books, args):
    if args.all:
        books.download_all_books(args.format)
    if args.title:
        books.download_books(args.title,args.format)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Download e-books from O\'Reilly')
    subparsers = parser.add_subparsers()

    # Create parser for list
    list_parser = subparsers.add_parser('list', help='list available e-books')
    list_parser.set_defaults(func=list)

    # Create parser for download
    download_parser = subparsers.add_parser('download', help='download e-books')
    group1 = download_parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--title','-t', action='append', help='titles to download')
    group1.add_argument('--all', action='store_true', help='download all available books')
    download_parser.set_defaults(func=download)

    download_parser.add_argument('format', help='format to download', action='append')
    args = parser.parse_args()
  
    # Initialize the connection
    email, password = get_login()
    books = OReillyBooks(email,password)
    
    args.func(books, args)
    
if __name__ == "__main__":
    sys.exit(main())