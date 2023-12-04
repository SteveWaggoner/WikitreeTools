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
        ('Australia','Australia'),
        ('Massachusetts','Massachusetts'),
        ('Palatinate', 'Ger'),
        ('Deutsches Reich', 'Ger'),
        ('Ireland','Ireland'),
        ('Idaho','Idaho'),
        ('Maine','Maine'),
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
    def getLatestDataDir():
        return sorted([d for d in os.listdir('.') if d.startswith('data_20')], reverse=True)[0]

    @staticmethod
    def getLatestDataDate():
        dataDir = Util.getLatestDataDir()
        return dataDir[5:].replace('_','-')

    @staticmethod
    def getLabel(text):
        return text.split("-")[-1].strip()

    @staticmethod
    def getWebPage(url,label=None):

        url = url.replace(" ","_")

        import urllib.request
        try:
            if label:
                label = label.replace(" ","_")

                cache_path = "cache/"+label+".webpage"
                if os.path.isfile(cache_path):
                    contents = open(cache_path, 'r').read()
                else:
                    print("reading "+url)
                    contents = urllib.request.urlopen(url).read().decode("utf8")
                    with open(cache_path, "w") as cache_fp:
                        cache_fp.write(contents)

            else:
                print("reading "+url)
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
class PersonDb:

    connection = None
    cursor = None

    def init(dataDir=Util.getLatestDataDir(),reload=False):
        if reload:
            os.remove("/tmp/person.db")

        PersonDb.connection = sqlite3.connect("/tmp/person.db")
        PersonDb.cursor = PersonDb.connection.cursor()


        if reload:
            PersonDb.createTables()
            PersonDb.readPersons(dataDir)
            PersonDb.readMarriages(dataDir)
            PersonDb.readCategories(dataDir)
            PersonDb.createIndexes()

    def createTables():
        PersonDb.cursor.execute("CREATE TABLE IF NOT EXISTS person (id TEXT PRIMARY KEY, wtId TEXT, name TEXT, fatherId TEXT, motherId TEXT, firstName TEXT, lastNameAtBirth TEXT, birthYear TEXT, deathYear TEXT, birthPlace TEXT, deathPlace TEXT, touched TEXT)")
        PersonDb.cursor.execute("CREATE TABLE IF NOT EXISTS marriage (id1 TEXT, id2 TEXT, year TEXT)")
        PersonDb.cursor.execute("CREATE TABLE IF NOT EXISTS category (id TEXT, category TEXT)")


    def createIndexes():
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS wtId_idx ON person (wtId)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS father_idx ON person (fatherId)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS mother_idx ON person (motherId)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS lnab_idx ON person (lastNameAtBirth)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS groom_idx ON marriage (id1)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS bride_idx ON marriage (id2)")
        PersonDb.cursor.execute("CREATE INDEX IF NOT EXISTS catid_idx ON category (id)")

    def putCategory(id,category):
        PersonDb.cursor.execute("INSERT OR REPLACE INTO category VALUES (?,?)", (id, category))

    def putMarriage(id1,id2,marriageYear):
        PersonDb.cursor.execute("INSERT OR REPLACE INTO marriage VALUES (?,?,?)", (id1, id2, marriageYear))

    def putPerson(person):
        PersonDb.cursor.execute("INSERT OR REPLACE INTO person VALUES (?,?, ?,?,?, ?,?, ?,?,?,?, ?)", (person.id, person.wtId, person.name, person.fatherId, person.motherId, person.firstName, person.lastNameAtBirth, person.birthYear, person.birthPlace, person.deathYear, person.deathPlace, person.touched))

    def getPersonById(id):
        if id and int(id) > 0:
            rows = PersonDb.cursor.execute("SELECT id, wtId, name, fatherId, motherId, firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched FROM person WHERE id=? LIMIT 100",(id,)).fetchall()
            if len(rows) > 0:
                return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3],rows[0][4],rows[0][5],rows[0][6],rows[0][7],rows[0][8],rows[0][9],rows[0][10],rows[0][11])

    def getPersonByWtId(wtId):
        rows = PersonDb.cursor.execute("SELECT id, wtId, name, fatherId, motherId, firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched FROM person WHERE wtId=? LIMIT 100",(wtId,)).fetchall()
        if len(rows) > 0:
            return Person(rows[0][0],rows[0][1],rows[0][2],rows[0][3],rows[0][4],rows[0][5],rows[0][6],rows[0][7],rows[0][8],rows[0][9],rows[0][10],rows[0][11])
        else:
            sys.stderr.write("Person not found. wtId="+wtId+"\n")

    def getPersonsByName(name):
        rows = PersonDb.cursor.execute("SELECT id, wtId, name, fatherId, motherId, firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched FROM person WHERE UPPER(name) LIKE ?",("%"+name.upper()+"% LIMIT 100",)).fetchall()
        persons = []
        for row in rows:
            persons.append(Person(row[0],row[1],row[2],row[3],row[4],row[5],rows[6],rows[7],rows[8],rows[9],rows[10],rows[11]))
        return persons

    def getPersonsByParent(parentId):
        persons = []
        if parentId and int(parentId)>0:
            rows = PersonDb.cursor.execute("SELECT id, wtId, name, fatherId, motherId, firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched FROM person WHERE fatherId=? or motherId=? LIMIT 100",(parentId,parentId)).fetchall()
            for row in rows:
                persons.append(Person(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
        return persons


    def getPersonsBySurnames(surnames):
        Util.logr("Loading ...")
        persons = {}
        for surname in surnames:
            Util.logr("Loading "+surname+"...")
            rows = PersonDb.cursor.execute("SELECT id, wtId, name, fatherId, motherId,  firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace,      touched FROM person WHERE lastNameAtBirth = ? LIMIT 200000",(surname,)).fetchall()
            for row in rows:
                persons[row[0]] = Person(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])

        Util.log("Done. loaded "+str(len(persons))+" persons")
        return persons


    def getSpouseIds(id):
        rows = PersonDb.cursor.execute("SELECT DISTINCT case when id2=? then id1 else id2 end spouseId FROM marriage WHERE id1=? or id2=?",(id,id,id)).fetchall()
        spouseIds = []
        for row in rows:
            spouseIds.append(row[0])

        return spouseIds

    def getPersonsByCategory(category):
        rows = PersonDb.cursor.execute("SELECT id FROM category WHERE category=?",(category,)).fetchall()

        persons = []
        for row in rows:
            person = PersonDb.getPersonById(row[0])
            if person is not None:
                persons.append(person)
            else:
                print("getPersonsByCategory "+category+": Cannot find userId: "+row[0])

        return persons



    def readPersons(dataDir):

        i=0
        gzpath = dataDir + "/dump_people_users.csv.gz"

        for line in Util.openGz(gzpath):
            line2 = line.decode('utf8')
            i = i + 1
            if i % 100000 == 0:
                Util.logr(str(i) + "  " + str(int(100 * i / 30300000)) + "%")
                PersonDb.connection.commit()

            tokens = line2.strip().split('\t')
            if i == 1:
                fields = tokens
            else:
                row = dict(zip(fields, tokens))

                id = row['User ID']
                wtId = row['WikiTree ID']

                firstName = row["First Name"]
                middleName = row["Middle Name"]
                lastNameAtBirth = row["Last Name at Birth"]
                lastNameCurrent = row["Last Name Current"]
                birthYear = row["Birth Date"][0:4]
                deathYear = row["Death Date"][0:4]
                birthPlace = Util.getAbbreviatedLocation(row["Birth Location"])
                deathPlace = Util.getAbbreviatedLocation(row["Death Location"])
                touched = row["Touched"]

                name = firstName
                if len(middleName)>0:
                    name = name +" "+middleName

                if lastNameAtBirth != lastNameCurrent:
                    name = name +" ("+lastNameAtBirth+")"
                name = name + " " + lastNameCurrent

                if len(birthYear)==0 or int(birthYear)<1:
                    birthYear = ""

                if len(deathYear)==0 or int(deathYear)<1:
                    deathYear = ""


                # make pretty label
                birthText = (birthYear + ' ' + birthPlace).strip()
                deathText = (deathYear + ' ' + deathPlace).strip()

                dates = ''
                if birthText != '' and deathText != '':
                    dates = '({birth} - {death})'.format(birth=birthText, death=deathText)
                else:
                    if birthText != '':
                        dates = '({birth})'.format(birth=birthText)
                    if deathText != '':
                        dates = '(died {death})'.format(death=deathText)

                name = (name + " "+dates).strip()
                #


                father = row['Father']
                mother = row['Mother']

                person = Person(id, wtId, name, father, mother, firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched)

                PersonDb.putPerson(person)

        PersonDb.connection.commit()


    def readMarriages(dataDir):

        i=0
        gzpath = dataDir + "/dump_people_marriages.csv.gz"

        for line in Util.openGz(gzpath):
            line2 = line.decode('utf8')
            i = i + 1
            if i % 100000 == 0:
                Util.logr(str(i) + "  " + str(int(100 * i / 10000000)) + "%")
                PersonDb.connection.commit()

            tokens = line2.strip().split('\t')
            if i == 1:
                fields = tokens
            else:
                row = dict(zip(fields, tokens))
                userId1 = row['User ID1']
                userId2 = row['UserID2']
                marriageYear = row["Marriage Date"][0:4]
                PersonDb.putMarriage(userId1,userId2,marriageYear)

        PersonDb.connection.commit()

    def readCategories(dataDir):

        i=0
        gzpath = dataDir + "/dump_categories.csv.gz"

        for line in Util.openGz(gzpath):
            line2 = line.decode('utf8')
            i = i + 1
            if i % 100000 == 0:
                Util.logr(str(i) + "  " + str(int(100 * i / 10000000)) + "%")
                PersonDb.connection.commit()

            tokens = line2.strip().split('\t')
            if i == 1:
                fields = tokens
            else:
                row = dict(zip(fields, tokens))
                userId = row['User ID']
                category = row['Category']
                PersonDb.putCategory(userId,category)

        PersonDb.connection.commit()



class Person:

    def __init__(self, id, wtId, name, fatherId, motherId,
            firstName, lastNameAtBirth, birthYear, birthPlace, deathYear, deathPlace, touched):
        self.id = id
        self.wtId = wtId
        self.name = name
        self.fatherId = fatherId
        self.motherId = motherId

        self.firstName = firstName
        self.lastNameAtBirth = lastNameAtBirth
        self.birthYear = birthYear
        self.birthPlace = birthPlace
        self.deathYear = deathYear
        self.deathPlace = deathPlace
        self.touched = touched

        self.prevPerson = None
        self.nextPerson = None


    def __lt__(self, other):

        # primary sort by birth year
        birthYear = self.birthYear
        otherBirthYear = other.birthYear
        if birthYear and otherBirthYear:
            if birthYear != otherBirthYear:
                return birthYear < otherBirthYear

        # secondary sort by name
        return self.name < other.name

    def complete(self):
        complete = 0
        if len(self.birthYear)>0:
            complete = complete + 1
        if len(self.deathYear)>0:
            complete = complete + 1
        if len(self.birthPlace)>0:
            complete = complete + 1
        if len(self.deathPlace)>0:
            complete = complete + 1
        return complete

    def spouses(self):
        return PersonDb.getSpouseIds(self.id)

    def children(self):
        return sorted(PersonDb.getPersonsByParent(self.id))

    def siblings(self):
        # include half siblings
        fathersChildren = PersonDb.getPersonsByParent(self.fatherId)
        mothersChildren = PersonDb.getPersonsByParent(self.motherId)
        return sorted(list(set(fathersChildren + mothersChildren)))

    def _appendPersons(id, prevPerson, prevReason, degree, maxDegree, persons, wantAnyConnection, isCommonAncester):

        if degree <= maxDegree:

            person = PersonDb.getPersonById(id)
            if person:

                existing = persons.get(person.id)
                if existing:
                    existingDegree, existingPerson = existing
                    if existingDegree < degree:
                        return

                person.prevPerson = prevPerson   # the person that caused this person to be added (e.g. the father, the mother, etc.)
                person.prevReason = prevReason
                persons[person.id] = (degree, person)

                children = person.children()
                for p in children:
                    Person._appendPersons(p.id, person, "child", degree + 1, maxDegree, persons, wantAnyConnection, isCommonAncester=False)

                if wantAnyConnection or isCommonAncester:
                    Person._appendPersons(person.fatherId, person, "father", degree + 1, maxDegree, persons, wantAnyConnection, isCommonAncester=True)
                    Person._appendPersons(person.motherId, person, "mother", degree + 1, maxDegree, persons, wantAnyConnection, isCommonAncester=True)

                    siblings = person.siblings()
                    for p in siblings:
                        Person._appendPersons(p.id, person, "sibling", degree + 1, maxDegree, persons, wantAnyConnection, isCommonAncester=False)

                if wantAnyConnection:
                    spouses = person.spouses()
                    for pid in spouses:
                        Person._appendPersons(pid, person, "spouse", degree + 1, maxDegree, persons, wantAnyConnection, isCommonAncester=False)


    def family(self, maxDegree, wantAnyConnection=False):
        family = {}
        Person._appendPersons(self.id, None, None, 0, maxDegree, family, wantAnyConnection, isCommonAncester=True)
        return sorted(family.values())


    def __repr__(self):
        if self.prevPerson is not None:
            return self.name + " <-- (" + self.prevPerson.name + " " + self.prevReason + ")"
        else:
            return self.name

    def deathInNewWorld(self):
        death_location = self.deathPlace
        return (len(death_location) == 2 and death_location.isupper()) or death_location in ['Canada','Australia','South America','United States']

    def isForeignBorn(self):
        return self.birthPlace in ['Ger','France','Russia','England','Prussia','Austria','Luxembourg','Holland','England','Czech','Austria-Hungray']

    def bornAfter(self, year):
        return len(self.birthYear)>0 and int(self.birthYear)>year

    def isRecentEmigrant(self):
        return self.isForeignBorn() and self.deathInNewWorld() and self.bornAfter(1800)


class Profile:

    def __init__(self, person):
        self.person = person
        self.profileText = Util.getWebPage("https://www.wikitree.com/wiki/"+person.wtId, person.wtId)


    def sections(self):

        titles = []
        curText = Util.after(self.profileText, r"<h[23]")
        while curText:
            title = Util.getBetween(curText[3:],">", "</span>")[:-6]
            titles.append(title.strip())
            curText = Util.after(curText,r"<h[2|3]")

        return titles

    def links(self):
        links = {}
        fag = Util.getBetween(self.profileText, "Find A Grave: <a", "</a>")
        fs  = Util.getBetween(self.profileText, "FamilySearch Person: <a", "</a>")

        if fag:
            links["FindAGrave"] = Util.after(fag,"#")

        if fs:
            links["FamilySearch"] = Util.getBetween(fs,"/person/","\"")

        return links


    def stats(self):
        stats = []
        if int(self.person.fatherId)>0:
            stats.append("father")
        if int(self.person.motherId)>0:
            stats.append("mother")
        if len(self.person.spouses())>0:
            stats.append("spouse")
        if len(self.person.children())>0:
            stats.append("children")
        if len(self.person.siblings())>0:
            stats.append("siblings")
        return stats

    def size(self):
        content = Util.getBetween(self.profileText,"This page has been accessed","Sponsored Search")
        return int((len(content)-100)/1000)

    def dnaYCnt(self):
        try:
            start = '<ul class="y">'
            end = '</ul>'
            y_dna = Util.getBetween(self.profileText, start, end)
            y_dna_cnt = y_dna.count('<li>')
        except:
            y_dna_cnt = 0
        return y_dna_cnt

    def dnaAuCnt(self):
        try:
            start = '<ul class="au">'
            end = '</ul>'
            au_dna = Util.getBetween(self.profileText, start, end)
            au_dna_cnt = au_dna.count('<li>')
        except:
            au_dna_cnt = 0
        return au_dna_cnt

    def dnaHasGedmatch(self):
        try:
            start = '<ul class="au">'
            end = '</ul>'
            au_dna = Util.getBetween(self.profileText, start, end)
            has_gedmatch = au_dna.count('gedmatch.com') > 0
        except:
            has_gedmatch = False
        return has_gedmatch


    def quality(self):

        points = 0
        probs = []

        sections = self.sections()

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
        if "Research notes" in sections or "Research Notes" in sections:
            points = points + 1
        else:
            probs.append("No research notes")

        links = self.links()
        if "FindAGrave" in links:
            points = points + 1
        else:
            probs.append("No findagrave")

        if "FamilySearch" in links:
            points = points + 3
        else:
            probs.append("No familysearch")

        if self.person.complete() < 4:
            probs.append("Missing "+str(4 - self.person.complete())+" fields")
        points = points + self.person.complete()

        stats = self.stats()
        for m in ["father","mother","siblings","spouse","children"]:
            if m in stats:
                points = points + 1
            else:
                probs.append("No "+m)

        size_pnts = self.size()
        probs.append("Size is "+str(size_pnts))
        if size_pnts > 8:
            size_pnts = 8
        points = points + size_pnts

        return (points, self.person.name, probs)


if __name__ == '__main__':
    print("This is a library")
