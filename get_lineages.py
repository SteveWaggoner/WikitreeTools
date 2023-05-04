#!/usr/bin/python2
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
        import urllib2
        try:
            contents = urllib2.urlopen(url).read()
            return contents
        except:
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

        for partial, cnt in substring_counts.iteritems():
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
def readArgs():

    from datetime import datetime
    curDate = datetime.today().strftime('%Y-%m-%d')

    cli_parser = argparse.ArgumentParser(description='Get wikitree lineages from database dumps')

    cli_parser.add_argument('--date', metavar='DATE', type=str,
                        default=curDate,
                        help='What day to process')

    cli_parser.add_argument('--last-update', metavar='UPDATE', type=str,
                        default=None,
                        help='What day did we last process')


    cli_parser.add_argument('surnames', metavar='SURNAME', type=str,
                        nargs='+',
                        help='Surnames to process: first surname is exact and others are alternatives')

    cli_parser.add_argument('--study', metavar='INDEX',
                        type=int, default=0,
                        help='Surname used for Study Name. 0=first, 1=second, etc (default is 0)')

    cli_parser.add_argument('--exact', metavar='INDEX',
                        type=int, default=0,
                        help='Surname used to "--min-gen-dna-exact-name" option (default is 0)')

    cli_parser.add_argument('--ignore-dna-cache', action='store_true',
                        help='Force updating the DNA status (default is False)')

    cli_parser.add_argument('--people-user-file', metavar='PATH', type=str,
                        default='data/dump_people_users.csv.gz',
                        help='Path to people user file')
    cli_parser.add_argument('--category-file', metavar='PATH', type=str,
                        default='data/dump_categories.csv.gz',
                        help='Path to category file')


    cli_parser.add_argument('--min-gen', metavar='GEN', type=int,
                        default=4,
                        help='Minimum tree depth to include in output')

    cli_parser.add_argument('--min-gen-dna', metavar='GEN', type=int,
                        default=1,
                        help='Minimum tree depth to include in output when have DNA')

    cli_parser.add_argument('--min-gen-dna-exact-name', metavar='GEN',
                        type=int, default=1,
                        help='Minimum tree depth to include in output when have DNA and exact surname')


    args = cli_parser.parse_args()
    studySurname = args.surnames[args.study]
    exactSurname = args.surnames[args.exact]

    Util.log(args)

    return (args, studySurname, exactSurname)


####################################################
class ConfigLoader:

    @staticmethod
    def getStudyIds(date, studySurname):
        studyName = '{surname}_Name_Study'.format(surname=studySurname)
        userIds = []
        n = 0
        gzpath = "data_{0}/dump_categories.csv.gz".format(date.replace("-","_"))
        for line in Util.openGz(gzpath):
            n = n + 1
            if n % 1000000 == 0:
                Util.logr(n)
            tokens = line.split('\t')
            if tokens[1].strip() == studyName:
                userIds.append(tokens[0])

            #for testing
            if os.getenv("DEBUG")!=None and len(userIds)>5:
                break

        Util.log(' found {cnt} profiles in study'.format(cnt=len(userIds)))
        return userIds

    @staticmethod
    def getPreviousDescendents(last_update, studySurname):

        previousDescendents = {}
        if last_update:
            prev_path = studySurname+"_Lineages-{time}.txt".format(time=last_update)
            Util.log("Reading " + prev_path)
            n = 0
            for rawline in open(prev_path):
                line = rawline.strip()

                if line[:1] == "|":
                    if line == "|-":
                        n = 0
                    if n == 3:
                        descendentCnt = int(line.split('|')[1])
                    if n == 5:
                        wtId = Util.getBetween(line,"[[", "|")
                        previousDescendents[wtId] = descendentCnt
                    n = n + 1

            Util.log(" found {cnt} previous descendents for {lastUpdate}".format(cnt=len(previousDescendents),lastUpdate=last_update))
        else:
            Util.log(" skipping previous descendents since didn't provide a --last-update")

        return previousDescendents

    @staticmethod
    def readManualEdits():
        uncertainFatherWikiIds = {}
        ignoreLineageWikiIds = {}
        labelLineageWikiIds = {}
        for line in open("manualEdits.txt"):
            tokens = line.strip().split("-",1)
            if len(tokens) > 1:
                action = tokens[0].strip()
                wikiId = Util.getWikiId(tokens[1])
                if action == "UncertainFather":
                    uncertainFatherWikiIds[wikiId] = True
                elif action == "IgnoreLineage":
                    ignoreLineageWikiIds[wikiId] = True
                elif action == "LabelLineage":
                    labelLineageWikiIds[wikiId] = Util.getLabel(tokens[1])
                else:
                    print "unknown action: "+action
        return (uncertainFatherWikiIds, ignoreLineageWikiIds, labelLineageWikiIds)



####################################################
class Profile:

  def __init__(self, row):
        self._row = row
        self.ancestor = None
        self.father = None
        self.children = []

        self.line = None
        self.line2 = None
        self.gen = 0
        self.descendents = 0
        self.dna = DNA("",0,0,0,"")

  def __repr__(self):
        return "{"+self.wikiId()+" "+self.getLabel()+"}"

  def wikiId(self):
        return self._row['WikiTree ID']

  def userId(self):
        return self._row['User ID']

  def touched(self):
        return self._row['Touched']

  def countDescendents(self):

        cnt = len(self.children)
        for child in self.children:
            cnt = cnt + child.countDescendents()
        return cnt

  def countGenerations(self, depth=0):

    max_depth = depth
    for child in self.children:
        tmp_depth = child.countGenerations(depth + 1)
        if max_depth < tmp_depth:
            max_depth = tmp_depth
    return max_depth

  def firstName(self):
      return self._row['First Name']

  def middleName(self):
      return self._row['Middle Name']

  def lastNameAtBirth(self):
      return self._row['Last Name at Birth']

  def birthYear(self):
      return int((self._row['Birth Date'])[:4])

  def deathYear(self):
      return int((self._row['Death Date'])[:4])

  def birthLocation(self):
      return Util.getAbbreviatedLocation(self._row['Birth Location'])

  def deathLocation(self):
      return Util.getAbbreviatedLocation(self._row['Death Location'])

  def isForeignBorn(self):
      return self.birthLocation() in ['Ger','France','Russia','England','Prussia','Austria','Luxembourg','Holland','England','Czech','Austria-Hungray']

  # death in new world
  def deathInStates(self):
      death_location = self.deathLocation()
      return (len(death_location) == 2 and death_location.isupper()) or death_location in ['Canada','Australia','South America','United States']

  def isRecentEmigrant(self):
      return self.isForeignBorn() and self.deathInStates() and self.birthYear() > 1800

  def getLabel(self):
      birth_year = str(self.birthYear())
      death_year = str(self.deathYear())

      if birth_year == '0':
         birth_year = ''

      if death_year == '0':
         death_year = ''

      birth_location = self.birthLocation()
      death_location = self.deathLocation()

      if birth_location == death_location:
         death_location = ''

      birth_text = (birth_year + ' ' + birth_location).strip()
      death_text = (death_year + ' ' + death_location).strip()

      dates = ''
      if birth_text != '' and death_text != '':
         dates = '({birth} - {death})'.format(birth=birth_text, death=death_text)
      else:
        if birth_text != '':
            dates = '({birth})'.format(birth=birth_text)
        if death_text != '':
            dates = '(died {death})'.format(death=death_text)

      firstName = (self.firstName() + ' ' + self.middleName()).strip()

      label = '{first} {last} {dates}'.format(first=firstName, last=self.lastNameAtBirth(), dates=dates)
      return label



class ProfileCollection:

  _allProfiles = {}
  _userToWikiLU = {}

  def __init__(self, config):
      self.config = config

  def lookupWikiId(self, userId):
    if userId in self._userToWikiLU:
        return self._userToWikiLU[userId]

  def append(self, row):
      profile = Profile(row)
      wikiId = profile.wikiId()
      self._allProfiles[wikiId] = profile
      self._userToWikiLU[profile.userId()] = wikiId

  def exists(self, wikiId):
      return wikiId in self._allProfiles

  def find(self, wikiId):
      return self._allProfiles[wikiId]

  def list(self):
      return self._allProfiles.iteritems()

  def count(self):
      return len(self._allProfiles)


  def lookupFather(self, profile):

      if profile.wikiId() not in self.config.uncertainFatherWikiIds:
            wikiId =  self.lookupWikiId(profile._row['Father'])
            if wikiId != None:
                return self.find(wikiId)

  def lookupEarliestAncestor(self, profile):

    ancestor = profile
    father = self.lookupFather(ancestor)
    while father != None and not father.wikiId() in self.config.uncertainFatherWikiIds:
        ancestor = father
        father = self.lookupFather(ancestor)

    return ancestor


  def load(self):

    partialSurName = Util.commonSubstring(self.config.args.surnames)
    Util.log(' partialSurName = ' + partialSurName)

    i = 0
    gzpath = "data_{0}/dump_people_users.csv.gz".format(self.config.args.date.replace("-","_"))
    for line in Util.openGz(gzpath):
        i = i + 1
        if i % 1000000 == 0:
            Util.logr(str(i) + "  " + str(self.count()))

        #for testing
        if os.getenv("DEBUG")!=None and self.count()>150:
            break

        if i == 1:
            tokens = line.strip().split('\t')
            fields = tokens
        else:
            if partialSurName in line:

                tokens = line.strip().split('\t')
                row = dict(zip(fields, tokens))

                lastName = row['Last Name at Birth']
                if lastName in self.config.args.surnames:
                    self.append(row)

    Util.log(' found {cnt} profiles matching surnames'.format(cnt=self.count()))


  def updateEarliestAncestors(self):

    Util.log('updateEarliestAncestors...')
    n = 0
    for (wikitreeId, profile) in self.list():
        n = n + 1
        if n % 100 == 0:
            Util.logr(n)
        profile.ancestor = self.lookupEarliestAncestor(profile)


  def updateChildren(self):

    Util.log('updateChildren...')
    for (childId, child) in self.list():
        father = self.lookupFather(child)
        if father != None:
            child.father = father
            if childId not in self.config.uncertainFatherWikiIds:
                father.children.append(child)
            else:
                Util.log("uncertain {father} is father of {child} ".format(father=father, child=child))


  def calculateLineages(self, lineages, dnaLoader):

    Util.log('findLineages...')

    n = 0
    ancestors = {}
    for (wikiId, profile) in self.list():
        n = n + 1
        if profile.ancestor != None:

            if profile.ancestor.father == None:

                ancestor = profile.ancestor

                ancestor.gen = ancestor.countGenerations()
                ancestor.descendents = ancestor.countDescendents()
                ancestor.dna = dnaLoader.getDNA(ancestor)

                lines = lineages.findDnaLine(ancestor)
                if len(lines) > 0:
                    ancestor.line = lines[0]
                    if len(lines) > 1:
                        ancestor.line2 = lines[1]

                ancestors[ancestor.wikiId()] = ancestor

            Util.logr(str(n)+"  "+str(len(ancestors)))

    ancestorArr = []
    for (id, ancestor) in ancestors.iteritems():
        ancestorArr.append(ancestor)

    Util.log(' found {cnt} common ancestors'.format(cnt=len(ancestorArr)))

    # sort largest descendent count first, then have dna first, then birth date ascending,
    ancestorsSorted1 = sorted(ancestorArr, key=lambda a: (not '1' in a.getLabel(), a.birthYear(), a.getLabel()))
    ancestorsSorted2 = sorted(ancestorsSorted1, key=lambda a: (a.descendents, a.dna.y_cnt > 0 or a.dna.au_cnt > 0), reverse=True)
    return ancestorsSorted2




####################################################
class DNA:

    def __init__(self, wikiId, y_cnt, au_cnt, has_gedmatch, curDate):
        self._wikiId = wikiId
        self.y_cnt = y_cnt
        self.au_cnt = au_cnt
        self.has_gedmatch = has_gedmatch
        self._curDate = curDate



class DNALoader:

    _cacheProfileDNAPath = './cache/profileDNA.txt'
    _cacheProfileDNA = {}
    _cacheTrys = 0
    _cacheHits = 0

    def __init__(self, config):
        self.config = config
        self.loadCache()

    def getDNA(self, profile, ignore_dna_cache=False):
        wikiId = profile.wikiId()

        if self._cacheTrys % 100 == 0 and self._cacheTrys > self._cacheHits:
            self.saveCache()

        self._cacheTrys = self._cacheTrys + 1
        if wikiId in self._cacheProfileDNA and not ignore_dna_cache:
            self._cacheHits = self._cacheHits + 1
            return self._cacheProfileDNA[wikiId]

        url = 'https://www.wikitree.com/wiki/' + wikiId
        contents = Util.getWebPage(url)

        try:
            start = '<ul class="y">'
            end = '</ul>'
            y_dna = Util.getBetween(contents, start, end)
            y_dna_cnt = y_dna.count('<li>')
        except:
            y_dna_cnt = 0

        try:
            start = '<ul class="au">'
            end = '</ul>'

            au_dna = Util.getBetween(contents, start, end)
            au_dna_cnt = au_dna.count('<li>')
            has_gedmatch = au_dna.count('gedmatch.com') > 0
        except:
            au_dna_cnt = 0
            has_gedmatch = False

        dna = DNA(wikiId, y_dna_cnt, au_dna_cnt, has_gedmatch, self.config.args.date)
        self._cacheProfileDNA[wikiId] = dna
        return dna


    def loadCache(self):
        Util.log('Reading ' + self._cacheProfileDNAPath)
        try:
            for line in open(self._cacheProfileDNAPath):
                tokens = line.strip().split('|')
                wikiId = tokens[0]
                self._cacheProfileDNA[wikiId] = DNA(wikiId, int(tokens[1]), int(tokens[2]), tokens[3], tokens[4])

        except Exception, e:
            print 'Failed to load: {file} ({e})'.format(file=self._cacheProfileDNAPath, e=e)
        Util.log(" {cnt} cached profiles loaded".format(cnt=len(self._cacheProfileDNA)))


    def saveCache(self):
        Util.log('Writing {file} (trys={trys}, hits={hits})'.format(file=self._cacheProfileDNAPath, trys=self._cacheTrys, hits=self._cacheHits))
        f = open(self._cacheProfileDNAPath, 'w')
        for (id, dna) in sorted(self._cacheProfileDNA.iteritems()):
            f.write('{id}|{t1}|{t2}|{t3}|{t4}\n'.format(id=id, t1=dna.y_cnt, t2=dna.au_cnt, t3=dna.has_gedmatch, t4=dna._curDate))
        f.close()



####################################################
class Lineage:

    def __init__(self, color, lineName, wikiId, inStudy):
        self.color = color
        self.lineName = lineName
        self.wikiId = wikiId
        self.inStudy = inStudy

    def __repr__(self):
        return "(color: "+self.color+", lineName="+self.lineName+", wikiId="+self.wikiId+", inStudy="+str(self.inStudy)+")"



class LineageCollection:

    _allLines = {}

    def __init__(self, config, profiles):
        self.config   = config
        self.profiles = profiles

    def list(self):
        return self._allLines.iteritems()

    def getStudyLabel(self, studyId):

        wikiId = self.profiles.lookupWikiId(studyId)
        if wikiId and self.profiles.exists(wikiId):

            profile = self.profiles.find(wikiId)

            if profile.wikiId() in self.config.labelLineageWikiIds:
                return self.config.labelLineageWikiIds[profile.wikiId()]

            father = profile.father
            if father:
                if father.wikiId() in self.config.labelLineageWikiIds:
                    return self.config.labelLineageWikiIds[father.wikiId()]
            for child in profile.children:
                if child.wikiId() in self.config.labelLineageWikiIds:
                    return self.config.labelLineageWikiIds[child.wikiId()]
        else:
            Util.log("Cannot find profile for user id: "+studyId+" ???")

        return 'In Study'


    def load(self):

        Util.log('getDnaLines...')

        dnaTabName = 'Space:{surname}_Name_Study_-_DNA'.format(surname=self.config.studySurname)

        dnaTab = Util.getWebPage('https://www.wikitree.com/wiki/{dnaTabName}'.format(dnaTabName=dnaTabName))

        start = '<th> Lineage'
        end = '</table>'
        for classified in Util.getBetween(dnaTab, start, end).split('<tr>'):
            color = Util.getBetween(classified, ' bgcolor="', '"')
            lineName = Util.getBetween(Util.getBetween(classified, ' bgcolor="',
                                  '/td>'), '>', '<').strip()
            wikiId = Util.getBetween(classified, '<a href="/wiki/', '"')

            self._allLines[wikiId] = Lineage(color, lineName, wikiId, False)

        n=0
        for studyId in self.config.studyIds:
            wikiId = self.profiles.lookupWikiId(studyId)

            n = n + 1
            Util.log("{n} - studyId={studyId}, wikiId={wikiId}, notInLines={noIn}".format(n=n,studyId=studyId, wikiId=wikiId, noIn=wikiId not in self._allLines))

            if wikiId not in self._allLines:
                studyLabel = self.getStudyLabel(studyId)
                self._allLines[wikiId] = Lineage('WhiteSmoke', studyLabel, wikiId, True)


    def findDnaLine2(self, profile, includeStudy, lines):

        wikiId = profile.wikiId()
        if wikiId in self._allLines and (includeStudy or not self._allLines[wikiId].inStudy):
            lines.append(self._allLines[wikiId])
        else:
            for child in profile.children:
                self.findDnaLine2(child, includeStudy, lines)


    def findDnaLine(self, profile):
        lines = []
        self.findDnaLine2(profile, False, lines)
        if len(lines) == 0:
            self.findDnaLine2(profile, True, lines)
        return lines


####################################################
####################################################

def isGoodLineage(config, profile):

    # criteria: must have dna, be assign to a line or be in the study or have manual edits
    has_dna = profile.dna.au_cnt > 0

    good = profile.gen >= config.args.min_gen \
            or (profile.gen >= config.args.min_gen_dna and has_dna) \
            or (profile.gen >= config.args.min_gen_dna_exact_name and has_dna and profile.lastNameAtBirth() == config.exactSurname) \
            or profile.line != None \
            or profile.userId() in config.studyIds \
            or profile.wikiId() in config.labelLineageWikiIds \
            or profile.wikiId() in config.uncertainFatherWikiIds

    return good


def prospectSortOrder(profile):
    return (profile.dna.au_cnt > 0, profile.touched())



####################################################
class History:

  def __init__(self, config, profiles):
      self.config = config
      self.np = 0
      self.newprofs = {}
      self.oldprofs = {}
      self.updateAllProfiles(profiles)


  def writeAllProfile(self, records, wikiId, children):
    for child in children:
        self.np = self.np + 1
        records.write("{wikiId}|{descendent}|{np}\n".format(wikiId=wikiId, descendent=child.wikiId(), np=self.np))
    for child in children:
        self.writeAllProfile(records, wikiId, child.children)

  def writeAllProfiles(self, path, profiles):
    records = open(path,"w")
    for p in profiles:
        self.writeAllProfile(records, p.wikiId(), p.children)
    records.close()
    return self.readAllProfiles(path)


  def readAllProfiles(self, path):
    ret = {}
    for line in open(path):
        tok = line.strip().split("|")
        anc = tok[0]
        dec = tok[1]
        n   = int(tok[2])
        if anc not in ret:
            ret[anc] = {}
        ret[anc][dec] = n
    return ret

  def updateAllProfiles(self, profiles):
    newpath = self.config.studySurname+"_AllProfiles-{time}.txt".format(time=self.config.args.date)
    self.newprofs = self.writeAllProfiles(newpath, profiles)
    if self.config.args.last_update:
        oldpath = self.config.studySurname+"_AllProfiles-{time}.txt".format(time=self.config.args.last_update)
        self.oldprofs = self.readAllProfiles(oldpath)


  def whatChanged(self, profile):

    # if we have the ancestor is previous update and now have more descendents
    change = ""
    if profile.wikiId in self.config.previousDescendents:
        whatchangedId = None
        if profile.descendents > self.config.previousDescendents[ancestorId]:

            new_decs = newprofs[pId]
            for new_dec_id in new_decs:
                if new_dec_id not in oldprofs[pId]:
                    if whatchangedId == None or new_decs[new_dec_id] < new_decs[whatchangedId]:
                        whatchangedId = new_dec_id

        if whatchangedId != None:
            change = "[[{0}|{1}]]".format(whatchangedId, profile.descendents - previousDescendents[pId])
        else:
            change = "{0}".format(profile.descendents - previousDescendents[pId])

    return change


class Reporter:

  def __init__(self, config):
    self.config = config


  def writeProspects(self, profiles):

    descendent_cnts = []
    good_descendent_cnts = []

    prospects = []

    for profile in profiles:
        descendent_cnts.append( profile.descendents )
        birth_year = profile.birthYear()
        if birth_year > 0 and birth_year < 1950 and len(profile.firstName()) > 2: # and profile.lastNameAtBirth() == self.config.exactSurname:
            good_descendent_cnts.append( profile.descendents )
            if birth_year > 1830:
                prospects.append( profile )


    pf = open(self.config.studySurname+"_Prospects-{time}.txt".format(time=self.config.args.date),"w")
    prospects.sort(key=prospectSortOrder)
    for i in range(250):
        if i < len(prospects):
            pf.write("Prospect{n} = {p}  {l} {t}\n".format(n=i+1, p=prospects[i].getLabel(),l=prospects[i].wikiId(),t=prospects[i].touched()))
    pf.close()

    if len(good_descendent_cnts) == 0:
        Util.log("No good descendents ?!?")
        return

    Util.log("Total profiles:      {total_cnt}".format(total_cnt = len(descendent_cnts)))
    Util.log("Total good profiles: {good_cnt} ({good_pct}%)".format(good_cnt = len(good_descendent_cnts), good_pct=100*len(good_descendent_cnts)/len(descendent_cnts)))
    Util.log("Total prospects:     {prospect_cnt} ({prospect_pct}%)".format(prospect_cnt = len(prospects), prospect_pct=100*len(prospects)/len(descendent_cnts)))

    cnt0  = len([x for x in good_descendent_cnts if x >= 0])
    cnt1  = len([x for x in good_descendent_cnts if x >= 1])
    cnt3  = len([x for x in good_descendent_cnts if x >= 3])
    cnt10 = len([x for x in good_descendent_cnts if x >= 10])
    Util.log("")
    Util.log("To-Do:")
    Util.log("Lineages greater than 0 people:  {cnt} ({pct}%)".format(cnt=cnt0,  pct=100*cnt0/len(good_descendent_cnts)))
    Util.log("Lineages greater than 1 people:  {cnt} ({pct}%)".format(cnt=cnt1,  pct=100*cnt1/len(good_descendent_cnts)))
    Util.log("Lineages greater than 3 people:  {cnt} ({pct}%)".format(cnt=cnt3,  pct=100*cnt3/len(good_descendent_cnts)))
    Util.log("Lineages greater than 10 people: {cnt} ({pct}%)".format(cnt=cnt10, pct=100*cnt10/len(good_descendent_cnts)))
    Util.log("")


  def writeLineages(self, profiles):

    history  = History(self.config, profiles)

    Util.log('printLineages...')

    path = self.config.studySurname+"_Lineages-{time}.txt".format(time=self.config.args.date)

    Util.log("Found {0} descendents, lastUpdate={1}".format(len(self.config.previousDescendents), self.config.args.last_update))

    fp = open(path,"w")
    fp.write( "''Auto-generated: {time}''\n".format(time=self.config.args.date) )

    changeHeader = ""
    if self.config.args.last_update:
        changeHeader = "! Chg<ref>change in descendents since {lastUpdate}</ref>".format(lastUpdate=self.config.args.last_update)


    fp.write ( """
{{| border="2" align="center" cellpadding=5 class="wikitable sortable"
|-
! Rank
! Gen<ref>generations deep</ref>
! Size<ref>count of descendents with Wagner surname</ref>
{changeHeader}
! Most Distant Known Ancestor
! colspan=2 | Lineage<ref>from [[Space:Wagner Name Study - DNA|DNA page]]</ref>
! DNA Notes
|-
""".format(changeHeader=changeHeader))

    n = 0
    for profile in profiles:

        pId = profile.wikiId()

        if pId in self.config.ignoreLineageWikiIds:
            Util.log("Ignoring lineage "+profile.getLabel())
            continue

        good = isGoodLineage(self.config, profile)
        if not good:
            continue

        n = n + 1
        label = profile.getLabel()

        ancestor = '[[{wikitreeId}|{label}]]'.format(wikitreeId=pId, label=label.strip())
        if pId in self.config.uncertainFatherWikiIds:
            ancestor = ancestor + " <sup>[uncertain father]</sup>"

        if profile.line:
            if pId != profile.line.wikiId:
                lineage = '[[{link}|{label}]]'.format(link=profile.line.wikiId, label=profile.line.lineName)
            else:
                lineage = profile.line.lineName

            if profile.line2:
                extra = ''

                color2 = ' || bgcolor=' + profile.line2.color + ' | '
                if pId != profile.line2.wikiId:
                    lineage2 = '[[{link}|{label}]]'.format(link=profile.line2.wikiId, label=profile.line2.lineName)
                else:
                    lineage2 = profile.line2.lineName
            else:

                extra = 'colspan=2 '
                color2 = ''
                lineage2 = ''

            color = extra + 'bgcolor=' + profile.line.color + ' |'
        else:

            if pId in self.config.labelLineageWikiIds:
               color = 'colspan=2 bgcolor=WhiteSmoke |'
               lineage = self.config.labelLineageWikiIds[pId]
            elif profile.isRecentEmigrant():
               color = 'colspan=2 bgcolor=WhiteSmoke |'
               lineage = 'Recent Emigrant'
            else:
               color = 'colspan=2 |'
               lineage = ''
            lineage2 = ''
            color2 = ''


        dna_text = ''
        if profile.dna.y_cnt > 0:
            dna_text = 'Y-DNA: {kits}'.format(kits=profile.dna.y_cnt)
        if profile.dna.au_cnt > 0:
            if dna_text != '':
                dna_text = dna_text + ', '
            dna_text = dna_text + 'auDNA: {kits}'.format(kits=profile.dna.au_cnt)
        if str(profile.dna.has_gedmatch) == 'True':
            dna_text = dna_text + ', GEDMatch'

        change = "|" + history.whatChanged(profile)


        fp.write ("""| {rank}
| {gen}
| {descendents}
{change}
| {ancestor}
| {color} {lineage} {color2} {lineage2}
| {dna}
|-\n""".format(
            rank=n,
            gen=profile.gen,
            descendents=profile.descendents,
            change=change,
            ancestor=ancestor,
            color=color,
            lineage=lineage,
            color2=color2,
            lineage2=lineage2,
            dna=dna_text,
            ))

    fp.write("|}\n")
    fp.close()

    Util.log(" wrote {n} lineages".format(n=n))



class Config:

    def __init__(self):
        (self.args, self.studySurname, self.exactSurname) = readArgs()
        self.studyIds = ConfigLoader.getStudyIds(self.args.date, self.studySurname)
        self.previousDescendents = ConfigLoader.getPreviousDescendents(self.args.last_update, self.studySurname)
        (self.uncertainFatherWikiIds, self.ignoreLineageWikiIds, self.labelLineageWikiIds) = ConfigLoader.readManualEdits()

class App:

    def __init__(self, config):
        self.config = config
        self.dnaLoader = DNALoader(self.config)
        self.profiles = ProfileCollection(self.config)
        self.lineages = LineageCollection(self.config, self.profiles)
        self.reporter = Reporter(self.config)

    def run(self):

        self.profiles.load()
        self.lineages.load()

        self.profiles.updateEarliestAncestors()
        self.profiles.updateChildren()

        lineageResults = self.profiles.calculateLineages(self.lineages, self.dnaLoader)

        self.reporter.writeLineages(lineageResults)
        self.reporter.writeProspects(lineageResults)



def main():

    config = Config()
    app = App(config)
    app.run()


main()

