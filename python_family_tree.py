#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse
import gzip

####################################################
class Util:

    @staticmethod
    def getAbbreviatedLocation(location):
        abbrs = [
        ('Germany', 'Ger'),
        ('Deutschland', 'Ger'),
        ('Saxony', 'Ger'),
        ('Heiliges R', 'Ger'),
        ('Pennsylvania', 'PA'),
        ('North Carolina', 'NC'),
        ('Alaska', 'AK'),
        ('California', 'CA'),
        ('Iowa', 'IA'),
        ('France', 'France'),
        ('Illinois', 'IL'),
        ('Virginia', 'VA'),
        (' Pa.', 'PA'),
        ('Luxembourg', 'Luxembourg'),
        ('Switzerland', 'Switzerland'),
        ('United Kingdom','UK'),
        (', MD', 'MD'),
        ('Ohio', 'OH'),
        ('Maryland', 'MD'),
        (', Pa', 'PA'),
        (', PA', 'PA'),
        (',PA', 'PA'),
        (', MA', 'MA'),
        (', KY', 'KY'),
        (', CA', 'CA'),
        (', GER', 'Ger'),
        (', Ill', 'IL'),
        ('West Prussia', 'Prussia'),
        ('Rhineland', 'Rhineland'),
        ('Prussia', 'Prussia'),
        ('Denmark', 'Denmark'),
        ('South Africa','South Africa'),
        ('Worcester, Cape Colony', 'South Africa'),
        ('Czechoslovakia','Czech'),
        ('Czech','Czech'),
        ('Ungarn','Hungary'),
        ('Kloppenheim', 'Ger'),
        ('Württemberg','Ger'),
        ('Alsace', 'Alsace'),
        ('Nederland', 'Neth'),
        ('Indiana', 'IN'),
        ('Ontario', 'Canada'),
        ('Kentucky', 'KY'),
        ('Alabama', 'AL'),
        ('Arkansas', 'AR'),
        ('Tennessee', 'TN'),
        ('Texas', 'TX'),
        ('Kansas', 'KS'),
        ('Louisiana', 'LA'),
        ('Mississippi', 'MS'),
        ('Wisconsin', 'WI'),
        ('England', 'England'),
        ('North Dakota', 'ND'),
        ('Nebraska', 'NE'),
        ('Georgia', 'GA'),
        ('Oklahoma', 'OK'),
        ('Canada', 'Canada'),
        ('Russia', 'Russia'),
        ('Colorado', 'CO'),
        ('Delaware', 'DE'),
        ('Austria', 'Austria'),
        ('Vermont', 'VT'),
        ('Missouri', 'MO'),
        ('New Jersey', 'NJ'),
        ('South Carolina', 'SC'),
        ('Minnesota', 'Minnesota'),
        ('Montana', 'Montana'),
        ('Michigan', 'Michigan'),
        ('Romania', 'Romania'),
        ('Iowa', 'Iowa'),
        ('California', 'California'),
        ('Arizona', 'Arizona'),
        ('Hungary', 'Hungary'),
        ('Czechoslovakia', 'Czechoslovakia'),
        ('NY', 'NY'),
        ('New York', 'NY'),
        ]
        for abbr in abbrs:
            (partial, label) = abbr
            if partial in location:
                return label
        return location

    @staticmethod
    def getWikiId(wl):
        fp = wl.split("|")[0]
        lp = fp.split("[")[2]
        return lp.strip()

    @staticmethod
    def after(txt, afterThis):
        tokens = txt.split(afterThis,1)
        if len(tokens)>1:
            return tokens[1]
        else:
            return ""

    @staticmethod
    def getLabel(text):
        return text.split("-")[-1].strip()

    @staticmethod
    def getWebPage(url):
        import urllib.request
        try:
            contents = urllib.request.urlopen(url).read().decode("utf8")
            return contents
        except:
            Util.log("Failed to read web page: "+url)
            return ''

    @staticmethod
    def getBetween(text, start, end):
        try:
            return text.split(start)[1].split(end)[0]
        except:
            return ''

    @staticmethod
    def commonSubstring(names):

        substring_counts = {}

        if len(names) == 1:
            return names[0]

        n = 0
        for i in range(0, len(names)):
            for j in range(i + 1, len(names)):
                n = n + 1
                string1 = names[i]
                string2 = names[j]

                partial_matches = []

                for start in range(0, len(string1)):
                    for end in range(start+1, len(string1)+1):
                        partial = string1[start:end]
                        if partial in string2:
                            if partial not in partial_matches:
                                partial_matches.append(partial)

                for matching_substring in partial_matches:
                    if matching_substring not in substring_counts:
                        substring_counts[matching_substring] = 1
                    else:
                        substring_counts[matching_substring] += 1

        best_partial = ""
        best_cnt = 0

        for partial, cnt in substring_counts.items():
            if cnt > best_cnt or ( cnt >= best_cnt and len(partial) > len(best_partial) ):
                best_partial = partial
                best_cnt = cnt

        if best_cnt == n:
            return best_partial
        else:
            return ""

    @staticmethod
    def openGz(path):
        Util.log('Reading ' + path)
        return gzip.open(path, 'rb')

    @staticmethod
    def log(msg):
        sys.stderr.write('{m}\n'.format(m=msg))

    @staticmethod
    def logr(msg):
        sys.stderr.write('{m}                 \r'.format(m=msg))

import sqlite3

class Person:
  #  os.remove("/tmp/person.db")
    connection = sqlite3.connect("/tmp/person.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS person(id TEXT PRIMARY KEY, name TEXT, fatherId TEXT, motherId TEXT)")

    def putPerson(person):
        Person.cursor.execute("INSERT OR REPLACE INTO person VALUES (?,?,?,?)", (person.id, person.name, person.fatherId, person.motherId))

    def getPersonById(id):
        rows = Person.cursor.execute("SELECT id, name, fatherId, motherId FROM person WHERE id=?",(id,)).fetchall()
        if len(rows) > 0:
            return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3])

    def getPersonByName(name):
        rows = Person.cursor.execute("SELECT id, name, fatherId, motherId FROM person WHERE name=?",(name,)).fetchall()
        if len(rows) > 0:
            return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3])

    def getPersonsByParent(parentId):
        rows = Person.cursor.execute("SELECT id, name, fatherId, motherId FROM person WHERE fatherId=? or motherId=?",(parentId,parentId)).fetchall()
        persons = []
        for row in rows:
            persons.append(Person(row[0],row[1],row[2],row[3]))
        return persons

    def __init__(self, id, name, fatherId=None, motherId=None):
        self.id = id
        self.name = name
        self.fatherId = fatherId
        self.motherId = motherId

    def __repr__(self):

        num_children = str(len(Person.getPersonsByParent(self.id)))

        return "{ id:" + str(self.id) + ", name:" + self.name + ", fatherId:" + str(self.fatherId) + ", motherId:" + self.motherId + ", num_children:"+num_children+" }"



def readProfiles():

    i=0
    gzpath = "data_2023_06_18/dump_people_users.csv.gz"

    for line in Util.openGz(gzpath):
        line2 = line.decode('utf8')
        i = i + 1
        if i % 100000 == 0:
            Util.logr(str(i) + "  " + str(int(100 * i / 30300000)) + "%")
            Person.connection.commit()

        #for testing
        if os.getenv("DEBUG")!=None and i > 20000:
            break

        tokens = line2.strip().split('\t')
        if i == 1:
            fields = tokens
        else:
            row = dict(zip(fields, tokens))

            name = row['WikiTree ID']
            id = row['User ID']
            father = row['Father']
            mother = row['Mother']
            person = Person(id, name, father, mother)
            Person.putPerson(person)

    Person.connection.commit()

readProfiles()

print("")
print(Person.getPersonByName("Howes-13"))
print(Person.getPersonByName("Waggoner-1922"))


