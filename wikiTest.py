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


def lookup(d, key):
    found = False
    for child in d.iter():
        if not found:
            try:
                if child.tag == 'a' and (key in child.text):
#                    print(child.text)   
                    found = True
            except: continue
        else: 
            if child.tag == 'a':
#                print(child.text, child.attrib)
                found = False
                return child

oldurl = 'example old url'
cur.execute('''INSERT OR IGNORE INTO Links (link) 
        VALUES ( ? )''', ( oldurl, ) )
cur.execute('SELECT id FROM Links WHERE link = ? ', (oldurl, ))
parenturl_id = cur.fetchone()[0]
print(parenturl_id )

url = 'https://en.wikipedia.org/wiki/Local_field'

startpage = 40
testpages = 10

for i in range(testpages):
    cur.execute('SELECT link FROM Links WHERE id = ? ', (startpage + i, ))
    url = 'https://en.wikipedia.org' + cur.fetchone()[0]
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        t1 = lookup(tree, 'Categories')
        newtree = tree
        categories = ['first']
        
        while t1.text != None and 'categor' not in categories[-1] and categories[-1] not in categories[:-2]:
            t1 = lookup(newtree, 'Categories')
            categories.append(t1.text)    
            newurl = 'https://en.wikipedia.org' + t1.get('href')
        #    print(t1.text)
            newpage = requests.get(newurl)
            newtree = html.fromstring(newpage.content)
        print(categories)
        
        if len(categories) >= 2:
            cur.execute('''INSERT OR IGNORE INTO Category (topic) 
                    VALUES ( ? )''', ( categories[-2], ) )
            cur.execute('SELECT id FROM Category WHERE topic = ? ', (categories[-2], ))
            category_id = cur.fetchone()[0]
        else:
            category_id = 'Null'
        cur.execute('''UPDATE Links SET topic = ?
                 WHERE id = ?''', (category_id, startpage + i) )
    except: continue
conn.commit()