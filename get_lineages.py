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
class CLI:

    cli_parser = argparse.ArgumentParser(description='Get wikitree lineages from database dumps')

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

    cli_parser.add_argument('--last-update-file', metavar='PATH',
                        type=str, default='',
                        help='Last update file to compare against')

    cli_parser.add_argument('--test', action='store_true',
                        help='just load partial data for quick test')

    args = cli_parser.parse_args()
    studySurname = args.surnames[args.study]
    exactSurname = args.surnames[args.exact]

    Util.log(args)


####################################################
class Config:

    @staticmethod
    def getStudyIds():
        studyName = '{surname}_Name_Study'.format(surname=CLI.studySurname)
        userIds = []
        n = 0
        for line in Util.openGz(CLI.args.category_file):
            n = n + 1
            if n % 1000000 == 0:
                Util.logr(n)
            tokens = line.split('\t')
            if tokens[1].strip() == studyName:
                userIds.append(tokens[0])
            if CLI.args.test:
                break

        Util.log(' found {cnt} profiles in study'.format(cnt=len(userIds)))
        return userIds

    @staticmethod
    def getPreviousDescendents():
        previousDescendents = {}
        lastUpdate = ""
        if len(CLI.args.last_update_file):
            lastUpdate = CLI.args.last_update_file.split('-',1)[1].split('.')[0]
            Util.log("Reading " + CLI.args.last_update_file)
            n = 0
            for rawline in open(CLI.args.last_update_file):
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

            Util.log(" found {cnt} previous descendents for {lastUpdate}".format(cnt=len(previousDescendents),lastUpdate=lastUpdate))
        return (previousDescendents,lastUpdate)

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

Config.studyIds = Config.getStudyIds()
(Config.uncertainFatherWikiIds,Config.ignoreLineageWikiIds,Config.labelLineageWikiIds) = Config.readManualEdits()



####################################################
class Profile:

  _allProfiles = {}
  _userToWikiLU = {}

  @staticmethod
  def getWikiId(userId):
    if userId in Profile._userToWikiLU:
        return Profile._userToWikiLU[userId]

  @staticmethod
  def load(row):
      profile = Profile(row)
      wikiId = profile.wikiId()
      Profile._allProfiles[wikiId] = profile
      Profile._userToWikiLU[profile.userId()] = wikiId

  @staticmethod
  def exists(wikiId):
      return wikiId in Profile._allProfiles

  @staticmethod
  def find(wikiId):
      return Profile._allProfiles[wikiId]

  @staticmethod
  def list():
      return Profile._allProfiles.iteritems()

  @staticmethod
  def count():
      return len(Profile._allProfiles)

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

  def getFather(self):

      if self.father:
         return self.father

      if self.wikiId() not in Config.uncertainFatherWikiIds:
            wikiId =  Profile.getWikiId(self._row['Father'])
            if wikiId != None:
                self.father = Profile.find(wikiId)

      return self.father

  def touched(self):
      return self._row['Touched']

  def earliestAncestor(self):
    if self.ancestor != None:
        return self.ancestor

    ancestor = self
    father = ancestor.getFather()
    while father != None and not father.wikiId() in Config.uncertainFatherWikiIds:
        ancestor = father
        father = ancestor.getFather()

    return ancestor

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
      return self.birthLocation() in ['Ger','France','Russia','England','Prussia','Austria','Luxembourg','Holland','England','Czech']

  # death in new world
  def deathInStates(self):
      death_location = self.deathLocation()
      return (len(death_location) == 2 and death_location.isupper()) or death_location in ['Canada','Australia','South America']

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




####################################################
class DNA:

    _cacheProfileDNAPath = './cache/profileDNA.txt'
    _cacheProfileDNA = {}
    _cacheTrys = 0
    _cacheHits = 0

    def __init__(self, wikiId, y_cnt, au_cnt, has_gedmatch, curDate):
        self._wikiId = wikiId
        self.y_cnt = y_cnt
        self.au_cnt = au_cnt
        self.has_gedmatch = has_gedmatch
        self._curDate = curDate

    @staticmethod
    def getProfileDNA(profile):
        wikiId = profile.wikiId()

        if DNA._cacheTrys % 100 == 0 and DNA._cacheTrys > DNA._cacheHits:
            DNA.saveCacheProfileDNA()

        DNA._cacheTrys = DNA._cacheTrys + 1
        if wikiId in DNA._cacheProfileDNA and not CLI.args.ignore_dna_cache:
            DNA._cacheHits = DNA._cacheHits + 1
            return DNA._cacheProfileDNA[wikiId]

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

        from datetime import datetime
        curDate = datetime.today().strftime('%Y-%m-%d')
        dna = DNA(wikiId, y_dna_cnt, au_dna_cnt, has_gedmatch, curDate)
        DNA._cacheProfileDNA[wikiId] = dna
        return dna


    @staticmethod
    def loadCacheProfileDNA():
        Util.log('Reading ' + DNA._cacheProfileDNAPath)
        try:
            for line in open(DNA._cacheProfileDNAPath):
                tokens = line.strip().split('|')
                wikiId = tokens[0]
                DNA._cacheProfileDNA[wikiId] = DNA(wikiId, int(tokens[1]), int(tokens[2]), tokens[3], tokens[4])

        except Exception, e:
            print 'Failed to load: {file} ({e})'.format(file=DNA._cacheProfileDNAPath, e=e)
        Util.log(" {cnt} cached profiles loaded".format(cnt=len(DNA._cacheProfileDNA)))


    @staticmethod
    def saveCacheProfileDNA():
        Util.log('Writing {file} (trys={trys}, hits={hits})'.format(file=DNA._cacheProfileDNAPath, trys=DNA._cacheTrys, hits=DNA._cacheHits))
        f = open(DNA._cacheProfileDNAPath, 'w')
        for (id, dna) in sorted(DNA._cacheProfileDNA.iteritems()):
            f.write('{id}|{t1}|{t2}|{t3}|{t4}\n'.format(id=id, t1=dna.y_cnt, t2=dna.au_cnt, t3=dna.has_gedmatch, t4=dna._curDate))
        f.close()


DNA.loadCacheProfileDNA()

####################################################
class Lineage:

    _allLines = {}

    @staticmethod
    def list():
        return Lineage._allLines.iteritems()

    def __init__(self, color, lineName, wikiId):
        self.color = color
        self.lineName = lineName
        self.wikiId = wikiId

    def __repr__(self):
        return "(color: "+self.color+", lineName="+self.lineName+", wikiId="+self.wikiId+")"

    @staticmethod
    def loadDnaLines():

        Util.log('getDnaLines...')

        dnaTabName = 'Space:{surname}_Name_Study_-_DNA'.format(surname=CLI.studySurname)

        dnaTab = Util.getWebPage('https://www.wikitree.com/wiki/{dnaTabName}'.format(dnaTabName=dnaTabName))

        start = '<th> Lineage'
        end = '</table>'
        start2 = '<a name="Other_Lineages_without_DNA'
        end2 = 'work in progress'
        for classified in Util.getBetween(dnaTab, start, end).split('<tr>'):
            color = Util.getBetween(classified, ' bgcolor="', '"')
            lineName = Util.getBetween(Util.getBetween(classified, ' bgcolor="',
                                  '/td>'), '>', '<').strip()
            wikiId = Util.getBetween(classified, '<a href="/wiki/', '"')

            Lineage._allLines[wikiId] = Lineage(color, lineName, wikiId)

        for unclassified in Util.getBetween(dnaTab, start2, end2).split('<tr>'):
            wikiId = Util.getBetween(unclassified, '<a href="/wiki/', '"')

            #use manualEdits for unclassified
            lineageName = 'Unclassified'
            if wikiId in Config.labelLineageWikiIds:
                lineageName = Config.labelLineageWikiIds[wikiId]

            Lineage._allLines[wikiId] = Lineage('WhiteSmoke', lineageName, wikiId)

        for studyId in Config.studyIds:
            wikiId = Profile.getWikiId(studyId)
            if wikiId not in Lineage._allLines:
                Lineage._allLines[wikiId] = Lineage('WhiteSmoke', 'In Study', wikiId)


    @staticmethod
    def findDnaLine2(profile, includeStudy, lines):

        wikiId = profile.wikiId()
        if wikiId in Lineage._allLines and (includeStudy or Lineage._allLines[wikiId].lineName != 'In Study'):
            lines.append(Lineage._allLines[wikiId])
        else:
            for child in profile.children:
                Lineage.findDnaLine2(child, includeStudy, lines)


    # prioritize dna lines over just in study

    @staticmethod
    def findDnaLine(profile):
        lines = []
        Lineage.findDnaLine2(profile, False, lines)
        if len(lines) == 0:
            Lineage.findDnaLine2(profile, True, lines)
        return lines

Lineage.loadDnaLines()

####################################################
####################################################

def loadProfiles():

    partialSurName = Util.commonSubstring(CLI.args.surnames)
    Util.log(' partialSurName = ' + partialSurName)

    i = 0
    for line in Util.openGz(CLI.args.people_user_file):
        i = i + 1
        if i % 1000000 == 0:
            Util.logr(str(i) + "  " + str(Profile.count()))

        if i == 1:
            tokens = line.strip().split('\t')
            fields = tokens
        else:
            if partialSurName in line:

                tokens = line.strip().split('\t')
                row = dict(zip(fields, tokens))

                lastName = row['Last Name at Birth']
                if lastName in CLI.args.surnames:
                    Profile.load(row)

        if CLI.args.test and Profile.count() > 1000:
            break
    Util.log(' found {cnt} profiles matching surnames'.format(cnt=Profile.count()))


def updateEarliestAncestors():

    Util.log('updateEarliestAncestors...')
    n = 0
    for (wikitreeId, profile) in Profile.list():
        n = n + 1
        if n % 100 == 0:
            Util.logr(n)
        profile.ancestor = profile.earliestAncestor()


def updateChildren():

    Util.log('updateChildren...')
    for (childId, child) in Profile.list():
        father = child.getFather()
        if father != None:
            if childId not in Config.uncertainFatherWikiIds:
                father.children.append(child)
            else:
                Util.log("uncertain {father} is father of {child} ".format(father=father, child=child))


def isGood(profile):

    # criteria: must have dna, be assign to a line or be in the study or have manual edits
    has_dna = profile.dna.au_cnt > 0

    good = profile.gen >= CLI.args.min_gen \
            or (profile.gen >= CLI.args.min_gen_dna and has_dna) \
            or (profile.gen >= CLI.args.min_gen_dna_exact_name and has_dna and profile.lastNameAtBirth() == exactSurname) \
            or profile.line != None \
            or profile.userId() in Config.studyIds \
            or profile.wikiId() in Config.labelLineageWikiIds \
            or profile.wikiId() in Config.uncertainFatherWikiIds

    if profile.wikiId() == 'Wagner-801':
        Util.log("profile = {p}, profile.dna.au_cnt={au_cnt}, has_dna={has_dna}, profile.gen={gen}, CLI.args.min_gen={min_gen}, profile.line={line}, isGood={isGood}".format(p=profile,au_cnt=profile.dna.au_cnt,has_dna=has_dna, gen=profile.gen, min_gen=CLI.args.min_gen, line=profile.line, isGood=good))

    return good


def findLineages():

    Util.log('findLineages...')

    n = 0
    ancestors = {}
    for (wikiId, profile) in Profile.list():
        n = n + 1
        if profile.ancestor != None:

            if profile.ancestor.getFather() == None:

                ancestor = profile.ancestor

                ancestor.gen = ancestor.countGenerations()
                ancestor.descendents = ancestor.countDescendents()
                ancestor.dna = DNA.getProfileDNA(ancestor)

                lines = Lineage.findDnaLine(ancestor)
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


def getTouched(profile):
    return (profile.dna.au_cnt > 0, profile.touched())

def printStatistics(profiles):

    descendent_cnts = []
    good_descendent_cnts = []

    prospects = []

    for profile in profiles:
        descendent_cnts.append( profile.descendents )
        birth_year = profile.birthYear()
        if birth_year < 1950 and len(profile.firstName()) > 2:
            good_descendent_cnts.append( profile.descendents )
            if birth_year > 1830 and profile.lastNameAtBirth() == 'Waggoner':
                prospects.append( profile )

    pf = open(CLI.studySurname+"_Prospects.txt","w")
    prospects.sort(key=getTouched)
    for i in range(250):
        if i < len(prospects):
            pf.write("Prospect{n} = {p}  {l} {t}\n".format(n=i+1, p=prospects[i].getLabel(),l=prospects[i].wikiId(),t=prospects[i].touched()))
    pf.close()

    Util.log("Total profiles:      {total_cnt}".format(total_cnt = len(descendent_cnts)))
    Util.log("Total good profiles: {good_cnt} ({good_pct}%)".format(good_cnt = len(good_descendent_cnts), good_pct=100*len(good_descendent_cnts)/len(descendent_cnts)))
    Util.log("Total prospects:     {prospect_cnt} ({prospect_pct}%)".format(prospect_cnt = len(prospects), prospect_pct=100*len(prospects)/len(descendent_cnts)))

    cnt1 = len([x for x in good_descendent_cnts if x < 1])
    cnt3 = len([x for x in good_descendent_cnts if x < 3])
    cnt10 = len([x for x in good_descendent_cnts if x < 10])
    Util.log("")
    Util.log("To-Do:")
    Util.log("Lineages less then 1 people:  {cnt} ({pct}%)".format(cnt=cnt1, pct=100*cnt1/len(good_descendent_cnts)))
    Util.log("Lineages less then 3 people:  {cnt} ({pct}%)".format(cnt=cnt3, pct=100*cnt3/len(good_descendent_cnts)))
    Util.log("Lineages less then 10 people: {cnt} ({pct}%)".format(cnt=cnt10, pct=100*cnt10/len(good_descendent_cnts)))
    Util.log("")


def printLineages(profiles):

    Util.log('printLineages...')

    (previousDescendents, lastUpdate) = Config.getPreviousDescendents()

    from datetime import datetime
    print "''Auto-generated: {time}''".format(time=datetime.today().strftime('%Y-%m-%d'))

    changeHeader = ""
    if lastUpdate!="":
        changeHeader = "! Chg<ref>change in descendents since {lastUpdate}</ref>".format(lastUpdate=lastUpdate)


    print """
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
""".format(changeHeader=changeHeader)

    n = 0
    for profile in profiles:

        if profile.wikiId() in Config.ignoreLineageWikiIds:
            Util.log("Ignoring lineage "+profile.getLabel())
            continue

        good = isGood(profile)
        if not good:
            continue

        n = n + 1
        label = profile.getLabel()

        ancestor = '[[{wikitreeId}|{label}]]'.format(wikitreeId=profile.wikiId(), label=label.strip())
        if profile.wikiId() in Config.uncertainFatherWikiIds:
            ancestor = ancestor + " <sup>[uncertain father]</sup>"

        if profile.line:
            if profile.wikiId() != profile.line.wikiId:
                lineage = '[[{link}|{label}]]'.format(link=profile.line.wikiId, label=profile.line.lineName)
            else:
                lineage = profile.line.lineName

            if profile.line2:
                extra = ''

                color2 = ' || bgcolor=' + profile.line2.color + ' | '
                if profile.wikiId() != profile.line2.wikiId:
                    lineage2 = '[[{link}|{label}]]'.format(link=profile.line2.wikiId, label=profile.line2.lineName)
                else:
                    lineage2 = profile.line2.lineName
            else:

                extra = 'colspan=2 '
                color2 = ''
                lineage2 = ''

            color = extra + 'bgcolor=' + profile.line.color + ' | '
        else:

            if profile.wikiId() in Config.labelLineageWikiIds:
               color = ' colspan=2 bgcolor=WhiteSmoke |'
               lineage = Config.labelLineageWikiIds[profile.wikiId()]
            elif profile.isRecentEmigrant():
               color = ' colspan=2 bgcolor=WhiteSmoke |'
               lineage = 'Recent Emigrant'
            else:
               color = ' colspan=2 | '
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

        change = ""
        if CLI.args.last_update_file != "":
            if profile.wikiId() in previousDescendents:
                change = "| {0}".format(profile.descendents - previousDescendents[profile.wikiId()])
            else:
                change = "|"

        print """
| {rank}
| {gen}
| {descendents}
{change}
| {ancestor}
| {color} {lineage} {color2} {lineage2}
| {dna}
|-""".format(
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
            )

    print '|}'

    Util.log(" wrote {n} lineages".format(n=n))



def main():

    loadProfiles()
    updateEarliestAncestors()
    updateChildren()

    lineages = findLineages()
    printLineages(lineages)
    printStatistics(lineages)

    DNA.saveCacheProfileDNA()

main()

