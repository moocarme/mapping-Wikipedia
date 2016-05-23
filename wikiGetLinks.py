# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:40:36 2016

@author: matt-666
"""

import sqlite3
from lxml import html
import requests

conn = sqlite3.connect('wikiLinks.sqlite')
cur = conn.cursor()

cur.executescript('''
/*
DROP TABLE IF EXISTS Links;
DROP TABLE IF EXISTS Category;

CREATE TABLE Links (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    link    TEXT UNIQUE,
    parent INTEGER,
    topic INTEGER
);

CREATE TABLE Category (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    topic TEXT UNIQUE

)
*/
''')

def get_urls(url_tree, parent_id):
    for child in url_tree.iter():
        try:
            if child.tag == 'a':
#               print(child.get('href'))
               cur.execute('''INSERT OR IGNORE INTO Links (link, parent) 
                   VALUES ( ?, ? )''', ( child.get('href'), parent_id) )
        except: continue
    return None

#oldurl = 'example old url'
#cur.execute('''INSERT OR IGNORE INTO Links (link) 
#        VALUES ( ? )''', ( oldurl, ) )
#cur.execute('SELECT id FROM Links WHERE link = ? ', (oldurl, ))
#parenturl_id = cur.fetchone()[0]
#print(parenturl_id )

init_url = 'https://en.wikipedia.org/wiki/Main_Page'

pages = 20
init = 344

#print(init_url)

for i in range(pages):
#cur.execute('''INSERT OR IGNORE INTO Links (link) 
#        VALUES ( ? )''', ( init_url, ) )

    cur.execute('SELECT link FROM Links WHERE id = ? ', (init + i, ))
    try:    
        url = cur.fetchone()[0]
    except: 
        url = None
    
    if url:
        cur.execute('SELECT id FROM Links WHERE link = ? ', (init_url, ))
        parenturl_id = cur.fetchone()[0]
        try:
            page = requests.get('https://en.wikipedia.org' + url)
            tree = html.fromstring(page.content)
            tree_body = tree.find_class('mw-content-ltr')
            tree_body=tree_body[0]
            t1 = get_urls(tree_body, parenturl_id)
        except: continue
conn.commit()
#print t1.get('href')
#newtree = tree
#categories = []
#
#while t1.text != None:
#    t1 = lookup(newtree, 'Categories')
#    categories.append(t1.text)    
#    newurl = 'https://en.wikipedia.org' + t1.get('href')
##    print(t1.text)
#    newpage = requests.get(newurl)
#    newtree = html.fromstring(newpage.content)
#print(categories)
#
#cur.execute('''INSERT OR IGNORE INTO Category (topic) 
#        VALUES ( ? )''', ( categories[-2], ) )
#cur.execute('SELECT id FROM Category WHERE topic = ? ', (categories[-2], ))
#category_id = cur.fetchone()[0]
#
#cur.execute('''INSERT OR IGNORE INTO Links (link, parent, topic) 
#        VALUES ( ?, ?, ? )''', ( url, parenturl_id, category_id) )
#conn.commit()