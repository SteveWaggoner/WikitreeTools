#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse

from family_tree_lib import *

####################################################
def readArgs():

    from datetime import datetime
    curDate = Util.getLatestDataDate()

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
                        help='Surname used for exact name. 0=first, 1=second, etc (default is 0)')

    cli_parser.add_argument('--min-gen', metavar='GEN', type=int,
                        default=6,
                        help='Minimum tree depth to include in output')

    cli_parser.add_argument('--min-descendents', metavar='GEN', type=int,
                        default=30,
                        help='Minimum tree width to include in output')

    cli_parser.add_argument('--min-gen-dna', metavar='GEN', type=int,
                        default=1,
                        help='Minimum tree depth to include in output when have DNA')

    args = cli_parser.parse_args()
    studySurname = args.surnames[args.study]
    exactSurname = args.surnames[args.exact]

    Util.log(args)

    return (args, studySurname, exactSurname)


####################################################
class Config:

    def __init__(self):
        (self.args, self.studySurname, self.exactSurname) = readArgs()
        self.studyPersons = Config.getStudyPersons(self.studySurname)
        self.studyIds = [x.id for x in self.studyPersons]
        self.previousDescendents = Config.getPreviousDescendents(self.args.last_update, self.studySurname)
        (self.uncertainFatherWikiIds, self.ignoreLineageWikiIds, self.labelLineageWikiIds) = Config.readManualEdits()


    @staticmethod
    def getStudyPersons(studySurname):
        studyAreaName = '{surname}_Name_Study'.format(surname=studySurname)
        persons = sorted(PersonDb.getPersonsByCategory(studyAreaName), key=lambda p:p.name)

        Util.log(' found {cnt} profiles in study'.format(cnt=len(persons)))
        return persons

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
                    print ("unknown action: "+action)
        return (uncertainFatherWikiIds, ignoreLineageWikiIds, labelLineageWikiIds)


####################################################
class Lineage:

    def __init__(self, color, lineName, wikiId, inStudy):
        self.color = color
        self.lineName = lineName
        self.wikiId = wikiId
        self.inStudy = inStudy

    def __repr__(self):
        return "(color: "+self.color+", lineName="+self.lineName+", wikiId="+self.wikiId+", inStudy="+str(self.inStudy)+")"


class LineageList:

    allLineages = {}

    def __init__(self, config):
        self.config = config
        self.loadDnaLineages()
        self.loadStudyLineages()

    def getStudyLabel(self, studyPerson):

        if studyPerson.wtId in self.config.labelLineageWikiIds:
            return self.config.labelLineageWikiIds[studyPerson.wtId]
        else:

            children = studyPerson.children()
            for child in children:
                if child.wtId in self.config.labelLineageWikiIds:
                    return self.config.labelLineageWikiIds[child.wtId]

            return 'In Study'


    def loadDnaLineages(self):

        dnaTabName = 'Space:{surname}_Name_Study_-_DNA'.format(surname=self.config.studySurname)
        dnaTab = Util.getWebPage('https://www.wikitree.com/wiki/{dnaTabName}'.format(dnaTabName=dnaTabName))
        start = '<th> Lineage'
        end = '</table>'
        for classified in Util.getBetween(dnaTab, start, end).split('<tr>'):
            color = Util.getBetween(classified, ' bgcolor="', '"')
            lineName = Util.getBetween(Util.getBetween(classified, ' bgcolor="',
                                  '/td>'), '>', '<').strip()
            wikiId = Util.getBetween(classified, '<a href="/wiki/', '"')

            self.allLineages[wikiId] = Lineage(color, lineName, wikiId, False)

    def loadStudyLineages(self):
        for studyPerson in self.config.studyPersons:
            if studyPerson.wtId not in self.allLineages:
                studyLabel = self.getStudyLabel(studyPerson)
                self.allLineages[studyPerson.wtId] = Lineage('WhiteSmoke', studyLabel, studyPerson.wtId, True)


    def findDnaLine2(self, profile, includeStudy, lines, depth):

        wikiId = profile.wtId
        if wikiId in self.allLineages and (includeStudy or not self.allLineages[wikiId].inStudy):
            lines.append(self.allLineages[wikiId])
        else:
            for child in profile.children():
                if child.lastNameAtBirth in config.args.surnames and child.wtId not in self.config.uncertainFatherWikiIds:
                    if depth < 50:
                        self.findDnaLine2(child, includeStudy, lines, depth + 1)


    def findDnaLine(self, profile):

        lines = []
        self.findDnaLine2(profile, False, lines, 0)
        if len(lines) == 0:
            self.findDnaLine2(profile, True, lines, 0)
        return lines



####################################################
class History:

  def __init__(self, config, profiles):
      self.config = config
      self.np = 0
      self.newprofs = {}
      self.oldprofs = {}
      self.updateDescendents(profiles)


  def appendDescendents(self, records, wikiId, children):

    for child in children:
        self.np = self.np + 1
        records.write("{wikiId}|{descendent}|{np}\n".format(wikiId=wikiId, descendent=child.wtId, np=self.np))
    for child in children:
        children = [c for c in child.children() if c.lastNameAtBirth in config.args.surnames]
        self.appendDescendents(records, wikiId, children)

  def writeDescendents(self, path, profiles):
    records = open(path,"w")
    for p in profiles:
        children = [c for c in p.children() if c.lastNameAtBirth in config.args.surnames]
        self.appendDescendents(records, p.wtId, children)
    records.close()
    return self.readDescendents(path)


  def readDescendents(self, path):
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

  def updateDescendents(self, profiles):
    newpath = self.config.studySurname+"_AllProfiles-{time}.txt".format(time=self.config.args.date)
    self.newprofs = self.writeDescendents(newpath, profiles)
    if self.config.args.last_update:
        oldpath = self.config.studySurname+"_AllProfiles-{time}.txt".format(time=self.config.args.last_update)
        self.oldprofs = self.readDescendents(oldpath)


  def whatChanged(self, profile):

    # if we have the ancestor is previous update and now have more descendents
    change = ""

    pId = profile.wtId

    if pId in self.config.previousDescendents:
        whatchangedId = None
        numDescendents = len(profile.descendents)-1  # exclude yourself

        if numDescendents > self.config.previousDescendents[pId]:
            if pId in self.newprofs:
                new_decs = self.newprofs[pId]
                for new_dec_id in new_decs:
                    if new_dec_id not in self.oldprofs[pId]:
                        if whatchangedId == None or new_decs[new_dec_id] < new_decs[whatchangedId]:
                            whatchangedId = new_dec_id

        if numDescendents < self.config.previousDescendents[pId]:
            if pId in self.newprofs:
                old_decs = self.oldprofs[pId]
                for old_dec_id in old_decs:
                    if old_dec_id not in self.newprofs[pId]:
                        if whatchangedId == None or old_decs[old_dec_id] < old_decs[whatchangedId]:
                            whatchangedId = old_dec_id

        if whatchangedId != None:
            change = "[[{0}|{1}]]".format(whatchangedId, numDescendents - self.config.previousDescendents[pId])
        else:
            change = " {0}".format(numDescendents - self.config.previousDescendents[pId])

    return change


class Reporter:

  def __init__(self, config, history):
    self.config = config
    self.history = history


  def writeProspects(self, profiles):

    descendent_cnts = []
    good_descendent_cnts = []

    prospects = []

    for profile in profiles:
        descendent_cnts.append( profile.descendents )

        if len(profile.birthYear) > 2 and int(profile.birthYear) < 1960 and len(profile.firstName) > 2:
            good_descendent_cnts.append( profile.descendents )
            if  profile.bornAfter(1770) and profile.profile.dnaAuCnt() > 0 and not profile.isForeignBorn():
                prospects.append( profile )


    pf = open(self.config.studySurname+"_Prospects-{time}.txt".format(time=self.config.args.date),"w")

    prospects.sort(key=lambda profile: (profile.profile.dnaAuCnt() > 1, profile.lastNameAtBirth==self.config.exactSurname, profile.birthYear), reverse=True)

    for i in range(250):
        if i < len(prospects):
            pf.write("Prospect{n} = {p}  {l} {t}\n".format(n=i+1, p=prospects[i].name,l=prospects[i].wtId,t=prospects[i].touched))
    pf.close()

    if len(good_descendent_cnts) == 0:
        Util.log("No good descendents ?!?")



  def writeLineages(self, persons):

    path = self.config.studySurname+"_Lineages-{time}.txt".format(time=self.config.args.date)

    Util.log("Found {0} previous descendents, lastUpdate={1}".format(len(self.config.previousDescendents), self.config.args.last_update))

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
! Size<ref>count of descendents with {studySurname} surname</ref>
{changeHeader}
! Most Distant Known Ancestor
! colspan=2 | Lineage<ref>from [[Space:{studySurname} Name Study - DNA|DNA page]]</ref>
! DNA Notes
|-
""".format(changeHeader=changeHeader, studySurname=self.config.studySurname))

    n = 0
    for person in persons:

        wtId = person.wtId
        label = person.name

        if wtId in self.config.ignoreLineageWikiIds:
            Util.log("Ignoring lineage "+label)
            continue

        n = n + 1

        ancestor = '[[{wikitreeId}|{label}]]'.format(wikitreeId=wtId, label=label)
        if wtId in self.config.uncertainFatherWikiIds:
            ancestor = ancestor + " <sup>[uncertain father]</sup>"


        if person.lines and len(person.lines) > 0:
            if wtId != person.lines[0].wikiId:
                lineage = '[[{link}|{label}]]'.format(link=person.lines[0].wikiId, label=person.lines[0].lineName)
            else:
                lineage = person.lines[0].lineName

            if len(person.lines)>1:
                extra = ''

                color2 = ' || bgcolor=' + person.lines[1].color + ' | '
                if wtId != person.lines[1].wikiId:
                    lineage2 = '[[{link}|{label}]]'.format(link=person.lines[1].wikiId, label=person.lines[1].lineName)
                else:
                    lineage2 = person.lines[1].lineName
            else:

                extra = 'colspan=2 '
                color2 = ''
                lineage2 = ''

            color = extra + 'bgcolor=' + person.lines[0].color + ' |'
        else:

            if wtId in self.config.labelLineageWikiIds:
               color = 'colspan=2 bgcolor=WhiteSmoke |'
               lineage = self.config.labelLineageWikiIds[wtId]
            elif person.isRecentEmigrant():
               color = 'colspan=2 bgcolor=WhiteSmoke |'
               lineage = 'Recent Emigrant'
            else:
               color = 'colspan=2 |'
               lineage = ''
            lineage2 = ''
            color2 = ''


        dna_text = ''
        if person.profile.dnaYCnt() > 0:
            dna_text = 'Y-DNA: {kits}'.format(kits=person.profile.dnaYCnt())
        if person.profile.dnaAuCnt() > 0:
            if dna_text != '':
                dna_text = dna_text + ', '
            dna_text = dna_text + 'auDNA: {kits}'.format(kits=person.profile.dnaAuCnt())
        if person.profile.dnaHasGedmatch() == True:
            dna_text = dna_text + ', GEDMatch'

        change = "|" + self.history.whatChanged(person)


        fp.write ("""| {rank}
| {gen}
| {numDescendents}
{change}
| {ancestor}
| {color} {lineage} {color2} {lineage2}
| {dna}
|-\n""".format(
            rank=n,
            gen=person.gen,
            numDescendents=len(person.descendents)-1, # exclude yourself
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



class Profiles:

    def __init__(self, config):
        self.config = config
        self.persons = {}
        self.load()

    def load(self):
        self.persons = PersonDb.getPersonsBySurnames(self.config.args.surnames)
        for pid in self.persons:
            self.persons[pid].descendents = {}
            self.persons[pid].descendents[pid] = self.persons[pid] #simplifies to include self as part of descendents
            self.persons[pid].gen = 1


    def updateEarliestAncestors(self):
        self.earliestAncestors = {}
        for pid in self.persons:
            person = self.persons[pid]

            # find earliest ancestr
            child = person
            while child.fatherId in self.persons:
                father = self.persons[child.fatherId]
                if child.wtId in self.config.uncertainFatherWikiIds:
                    break
                father.gen = child.gen + 1
                father.descendents.update(child.descendents)
                child = father
            person.earliestAncestor = child
            #

            self.earliestAncestors[person.earliestAncestor.id] = person.earliestAncestor

    def isGoodLineagePass1(self, person):

        good = (person.gen > 1 and len(person.firstName) > 0 and not person.wtId in self.config.ignoreLineageWikiIds) \
            or len(person.lines) > 0 \
            or person.id in self.config.studyIds \

        return good


    def isGoodLineagePass2(self, person):

        has_dna = person.profile.dnaHasGedmatch() or person.profile.dnaYCnt() > 0

        good = person.gen >= config.args.min_gen \
            or len(person.descendents) >= config.args.min_descendents \
            or (person.gen >= config.args.min_gen_dna and has_dna) \
            or len(person.lines) > 0 \
            or person.id in config.studyIds \
            or person.wtId in config.labelLineageWikiIds \
            or person.wtId in config.uncertainFatherWikiIds

        return good


    def getLineages(self):

        Util.logr("Reading lineages ...")

        ea_persons1 = sorted(self.earliestAncestors.values(), key=lambda person: (-len(person.descendents), person.birthYear)) # num descendents desc, birthyear asc

        lineages = LineageList(config)

        Util.logr("Finding lineages ...")

        for p in ea_persons1:
            p.lines = lineages.findDnaLine(p)

        ea_persons2 = [p for p in ea_persons1 if self.isGoodLineagePass1(p)]

        Util.log("Found "+str(len(ea_persons2))+" good lineages (pass1)")

        for p in ea_persons2:
            p.profile = Profile(p)

        ea_persons3 = [p for p in ea_persons2 if self.isGoodLineagePass2(p)]

        Util.log("Found "+str(len(ea_persons3))+" good lineages (pass2)")

        return ea_persons3


PersonDb.init(reload=str(os.getenv('RELOAD'))=="1")

config = Config()
profiles = Profiles(config)

profiles.updateEarliestAncestors()

lineages = profiles.getLineages()

history = History(config, lineages)

reporter = Reporter(config, history)
reporter.writeLineages(lineages)
reporter.writeProspects(lineages)

