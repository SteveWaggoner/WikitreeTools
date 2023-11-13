#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse
import gzip
import re

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
    def xxafter(txt, afterThis1, afterThis2=None):
        tokens1 = txt.split(afterThis1,1)
        tokens2 = txt.split(afterThis,1)
        if len(tokens)>1:
            return tokens[1]
        else:
            return ""


    @staticmethod
    def after(txt, afterThis):
        tokens = re.split(afterThis, txt, maxsplit=1)
        if len(tokens)>1:
            return tokens[1]
        else:
            return ""


    @staticmethod
    def getLabel(text):
        return text.split("-")[-1].strip()

    @staticmethod
    def getWebPage(url,label=None):
        import urllib.request
        try:
            print("reading "+url)
            if label:
                cache_path = "cache/"+label+".webpage"
                if os.path.isfile(cache_path):
                    print("loading cache "+cache_path)
                    contents = open(cache_path, 'r').read()
                else:
                    contents = urllib.request.urlopen(url).read().decode("utf8")
                    print("writing cache "+cache_path)
                    with open(cache_path, "w") as cache_fp:
                        cache_fp.write(contents)

            else:
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




####################################################
import sqlite3
class Person:
    # os.remove("/tmp/person.db")
    connection = sqlite3.connect("/tmp/person.db")
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS person(id TEXT PRIMARY KEY, wtId TEXT, name TEXT, fatherId TEXT, motherId TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS marriage(id1 TEXT, id2 TEXT, year TEXT)")

    def createIndexes():
        Person.cursor.execute("CREATE INDEX IF NOT EXISTS wtId_idx ON person (wtId)")
        Person.cursor.execute("CREATE INDEX IF NOT EXISTS father_idx ON person (fatherId)")
        Person.cursor.execute("CREATE INDEX IF NOT EXISTS mother_idx ON person (motherId)")
        Person.cursor.execute("CREATE INDEX IF NOT EXISTS groom_idx ON marriage (id1)")
        Person.cursor.execute("CREATE INDEX IF NOT EXISTS bride_idx ON marriage (id2)")

    def putMarriage(id1,id2,marriageYear):
        Person.cursor.execute("INSERT OR REPLACE INTO marriage VALUES (?,?,?)", (id1, id2, marriageYear))

    def putPerson(person):
        Person.cursor.execute("INSERT OR REPLACE INTO person VALUES (?,?,?,?,?)", (person.id, person.wtId, person.name, person.fatherId, person.motherId))

    def getPersonById(id):
        if id and int(id) > 0:
            rows = Person.cursor.execute("SELECT id, wtId, name, fatherId, motherId FROM person WHERE id=? LIMIT 100",(id,)).fetchall()
            if len(rows) > 0:
                return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3],rows[0][4])

    def getPersonByWtId(wtId):
        rows = Person.cursor.execute("SELECT id, wtId, name, fatherId, motherId FROM person WHERE wtId=? LIMIT 100",(wtId,)).fetchall()
        if len(rows) > 0:
            return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3],rows[0][4])

    def getPersonsByName(name):
        rows = Person.cursor.execute("SELECT id, wtId, name, fatherId, motherId FROM person WHERE UPPER(name) LIKE ?",("%"+name.upper()+"% LIMIT 100",)).fetchall()
        persons = []
        for row in rows:
            persons.append(Person(row[0],row[1],row[2],row[3],row[4]))
        return persons

    def getPersonsByParent(parentId):
        persons = []
        if parentId and int(parentId)>0:
            rows = Person.cursor.execute("SELECT id, wtId, name, fatherId, motherId FROM person WHERE fatherId=? or motherId=? LIMIT 100",(parentId,parentId)).fetchall()
            for row in rows:
                persons.append(Person(row[0],row[1],row[2],row[3],row[4]))
        return persons

    def getSpouseIds(id):
        rows1 = Person.cursor.execute("SELECT id1 FROM marriage WHERE id2=?",(id,)).fetchall()
        rows2 = Person.cursor.execute("SELECT id2 FROM marriage WHERE id1=?",(id,)).fetchall()
        spouseIds = []
        for row in rows1 + rows2:
            spouseIds.append(row[0])
        return spouseIds


    def __init__(self, id, wtId, name, fatherId=None, motherId=None):
        self.id = id
        self.wtId = wtId
        self.name = name
        self.fatherId = fatherId
        self.motherId = motherId

    def birthYear(self):
        birthYearArr = self.name.rsplit('(', 2)
        if len(birthYearArr)==2:
            return birthYearArr[1][0:4]



    def __lt__(self, other):

        # primary sort by birth year
        birthYear = self.birthYear()
        otherBirthYear = other.birthYear()
        if birthYear and otherBirthYear:
            if birthYear != otherBirthYear:
                return birthYear < otherBirthYear

        # secondary sort by name
        return self.name < other.name

    def spouses(self):
        return Person.getSpouseIds(self.id)

    def children(self):
        return sorted(Person.getPersonsByParent(self.id))

    def siblings(self):
        # include half siblings
        fathersChildren = Person.getPersonsByParent(self.fatherId)
        mothersChildren = Person.getPersonsByParent(self.motherId)
        return sorted(list(set(fathersChildren + mothersChildren)))

    def _appendPersons(id, degree, maxDegree, persons):

        if degree <= maxDegree:

            person = Person.getPersonById(id)
            if person:

                existing = persons.get(person.id)
                if existing:
                    existingDegree,eo,ep = existing
                    if existingDegree < degree:
                        return

                persons[person.id] = (degree, len(persons), person)

                children = person.children()
                for p in children:
                    Person._appendPersons(p.id, degree + 1, maxDegree, persons)

                Person._appendPersons(person.fatherId, degree + 1, maxDegree, persons)
                Person._appendPersons(person.motherId, degree + 1, maxDegree, persons)

                siblings = person.siblings()
                for p in siblings:
                    Person._appendPersons(p.id, degree + 1, maxDegree, persons)

                spouses = person.spouses()
                for pid in spouses:
                    Person._appendPersons(pid, degree + 1, maxDegree, persons)


    def family(self, maxDegree):
        family = {}
        Person._appendPersons(self.id, 0, maxDegree, family)
        return sorted(family.values())

    def __repr__(self):

        num_children = str(len(Person.getPersonsByParent(self.id)))

        return "{ id:" + str(self.id) + ", wtId:"+ self.wtId + ", name:" + self.name + ", fatherId:" + str(self.fatherId) + ", motherId:" + self.motherId + ", num_children:"+num_children+" }"


    dataDir="data_2023_11_11"
    def readPersons():

        i=0
        gzpath = Person.dataDir + "/dump_people_users.csv.gz"

        for line in Util.openGz(gzpath):
            line2 = line.decode('utf8')
            i = i + 1
            if i % 100000 == 0:
                Util.logr(str(i) + "  " + str(int(100 * i / 30300000)) + "%")
                Person.connection.commit()

            tokens = line2.strip().split('\t')
            if i == 1:
                fields = tokens
            else:
                row = dict(zip(fields, tokens))

                id = row['User ID']
                wtId = row['WikiTree ID']

                firstName = row["First Name"]
                middleName = row["Middle Name"]
                lastName1 = row["Last Name at Birth"]
                lastName2 = row["Last Name Current"]
                born = row["Birth Date"][0:4]

                name = firstName
                if len(middleName)>0:
                    name = name +" "+middleName

                if lastName1 != lastName2:
                    name = name +" ("+lastName1+")"
                name = name + " " + lastName2

                if len(born)>0:
                    name = name + " ("+born+")"

                father = row['Father']
                mother = row['Mother']
                person = Person(id, wtId, name, father, mother)

                Person.putPerson(person)

        Person.connection.commit()

    def readMarriages():

        i=0
        gzpath = Person.dataDir + "/dump_people_marriages.csv.gz"

        for line in Util.openGz(gzpath):
            line2 = line.decode('utf8')
            i = i + 1
            if i % 100000 == 0:
                Util.logr(str(i) + "  " + str(int(100 * i / 10000000)) + "%")
                Person.connection.commit()

            tokens = line2.strip().split('\t')
            if i == 1:
                fields = tokens
            else:
                row = dict(zip(fields, tokens))
                userId1 = row['User ID1']
                userId2 = row['UserID2']
                marriageYear = row["Marriage Date"][0:4]
                Person.putMarriage(userId1,userId2,marriageYear)

        Person.connection.commit()


#Person.readPersons()
#Person.readMarriages()
#Person.createIndexes()


def getSections(profileText):

    titles = []
    curText = Util.after(profileText, r"<h[23]")
    while curText:
        title = Util.getBetween(curText[3:],">", "</span>")[:-6]
        titles.append(title.strip())
        curText = Util.after(curText,r"<h[2|3]")

    return titles

def getLinks(profileText):
    links = {}
    fag = Util.getBetween(profileText, "Find A Grave: <a", "</a>")
    fs  = Util.getBetween(profileText, "FamilySearch Person: <a", "</a>")

    if fag:
        links["FindAGrave"] = Util.after(fag,"#")

    if fs:
        links["FamilySearch"] = Util.getBetween(fs,"/person/","\"")

    return links


def getStats(person):
    stats = []
    if int(person.fatherId)>0:
        stats.append("father")
    if int(person.motherId)>0:
        stats.append("mother")
    if len(person.spouses())>0:
        stats.append("spouse")
    if len(person.children())>0:
        stats.append("children")
    if len(person.siblings())>0:
        stats.append("siblings")
    return stats

def getSize(profileText):
    content = Util.getBetween(profileText,"This page has been accessed","Sponsored Search")
    return int((len(content)-100)/500)


def getProfileQuality(person):

    profileText = Util.getWebPage("https://www.wikitree.com/wiki/"+person.wtId, person.wtId)

    points = 0
    probs = []

    sections = getSections(profileText)

    if "Biography" in sections:
        points = points + 1
    else:
        probs.append("No biography")

    if "Family" in sections:
        points = points + 2
    else:
        probs.append("No family")
    if "Census" in sections:
        points = points + 1
    else:
        probs.append("No census")
    if "Sources" in sections:
        points = points + 1
    else:
        probs.append("No sources")
    if "Research notes" in sections:
        points = points + 1
    else:
        probs.append("No research notes")

    links = getLinks(profileText)
    if "FindAGrave" in links:
        points = points + 1
    else:
        probs.append("No findagrave")

    if "FamilySearch" in links:
        points = points + 2
    else:
        probs.append("No familysearch")

    stats = getStats(person)
    for m in ["father","mother","siblings","spouse","children"]:
        if m in stats:
            points = points + 1
        else:
            probs.append("No "+m)

    size_pnts = getSize(profileText)
    probs.append("Size is "+str(size_pnts))
    if size_pnts > 8:
        size_pnts = 8
    points = points + size_pnts

    return (points, person.name, probs)



family = Person.getPersonByWtId("Waggoner-1945").family(5)

quality_family = []

for degrees, ord, fam_person in family:
    if fam_person.birthYear() and int(fam_person.birthYear()) < 1900:
        points, name, probs = getProfileQuality(fam_person)
        quality_family.append( (points + degrees, degrees, name, probs) )

for fam in sorted(quality_family):
    print(fam)

