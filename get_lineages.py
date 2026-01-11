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

    cli_parser.add_argument('--min-descendants', metavar='GEN', type=int,
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
        self.loadStudyPersons()
        self.loadManualEdits()


    def loadStudyPersons(self):
        studyAreaName = '{surname}_Name_Study'.format(surname=self.studySurname)

        self.studyPersons = sorted(PersonDb.getPersonsByCategory(studyAreaName), key=lambda p:p.name)
        self.studyIds = [x.id for x in self.studyPersons]

        Util.log(' found {cnt} profiles in study'.format(cnt=len(self.studyPersons)))


    def loadManualEdits(self):
        self.uncertainFatherWikiIds = {}
        self.ignoreLineageWikiIds = {}
        self.labelLineageWikiIds = {}
        for line in open("manualEdits.txt"):
            tokens = line.strip().split("-",1)
            if len(tokens) > 1:
                action = tokens[0].strip()
                wtId = Util.getWikiId(tokens[1])
                if action == "UncertainFather":
                    self.uncertainFatherWikiIds[wtId] = True
                elif action == "IgnoreLineage":
                    self.ignoreLineageWikiIds[wtId] = True
                elif action == "LabelLineage":
                    self.labelLineageWikiIds[wtId] = Util.getLabel(tokens[1])
                else:
                    print ("unknown action: "+action)


####################################################
class Lineage:

    def __init__(self, color, lineName, wtId, inStudy):
        self.color = color
        self.lineName = lineName
        self.wtId = wtId
        self.inStudy = inStudy

    def __repr__(self):
        return "(color: "+self.color+", lineName="+self.lineName+", wtId="+self.wtId+", inStudy="+str(self.inStudy)+")"


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
            wtId = Util.getBetween(classified, '<a href="/wiki/', '"')

            self.allLineages[wtId] = Lineage(color, lineName, wtId, False)

    def loadStudyLineages(self):
        for studyPerson in self.config.studyPersons:
            if studyPerson.wtId not in self.allLineages:
                studyLabel = self.getStudyLabel(studyPerson)
                self.allLineages[studyPerson.wtId] = Lineage('WhiteSmoke', studyLabel, studyPerson.wtId, True)


    def findDnaLine2(self, person, includeStudy, lines, depth):

        wtId = person.wtId
        if wtId in self.allLineages and (includeStudy or not self.allLineages[wtId].inStudy):
            lines.append(self.allLineages[wtId])
        else:
            for child in person.children():
                if child.lastNameAtBirth in self.config.args.surnames and child.wtId not in self.config.uncertainFatherWikiIds:
                    if depth < 50:
                        self.findDnaLine2(child, includeStudy, lines, depth + 1)


    def findDnaLine(self, person):

        lines = []
        self.findDnaLine2(person, False, lines, 0)
        if len(lines) == 0:
            self.findDnaLine2(person, True, lines, 0)
        return lines


    def findLinesByName(self, lineName):
        ret = []
        for line in self.allLineages.values():
            if line.lineName == lineName:
                ret.append(line.wtId)
        return ret



####################################################
class History:

  def __init__(self, config):
      self.config = config
      self.personIndex = 0
      self.newPersons = {}
      self.oldPersons = {}

  def appendPersons(self, records, wtId, children, depth):

    if len(children) > 0:
        for child in children:
            self.personIndex = self.personIndex + 1
            records.write("{wtId}|{descendant}|{n}\n".format(wtId=wtId, descendant=child.wtId, n=self.personIndex))
    else:
        if depth==0:
            self.personIndex = self.personIndex + 1
            records.write("{wtId}||{n}\n".format(wtId=wtId, n=self.personIndex))

    for child in children:
        children = [c for c in child.children() if c.lastNameAtBirth in self.config.args.surnames]
        self.appendPersons(records, wtId, children, depth+1)

  def writePersons(self, persons, path):
    records = open(path,"w")
    for person in persons:
        children = [c for c in person.children() if c.lastNameAtBirth in self.config.args.surnames]
        self.appendPersons(records, person.wtId, children, 0)
    records.close()
    return self.readPersons(path)


  def readPersons(self, path):
    retPersons = {}
    for line in open(path):
        tok = line.strip().split("|")
        ancestorId   = tok[0]
        descendantId = tok[1]
        n            = int(tok[2])
        if ancestorId not in retPersons:
            retPersons[ancestorId] = {}
        retPersons[ancestorId][descendantId] = n
    return retPersons

  def loadPersons(self, persons):

    newPath = self.config.studySurname+"_AllProfiles-{date}.txt".format(date=self.config.args.date)

    self.writePersons(persons, newPath)
    self.newPersons = self.readPersons(newPath)

    if self.config.args.last_update:
        oldPath = self.config.studySurname+"_AllProfiles-{date}.txt".format(date=self.config.args.last_update)
        self.oldPersons = self.readPersons(oldPath)


  def whatChanged(self, person):

    # if we have the ancestor is previous update and now have more descendants
    change = ""

    pId = person.wtId

    newDescendantList = self.newPersons[pId]
    oldDescendantList = self.oldPersons.get(pId)

    if oldDescendantList:

        whatChangedId = None

        if len(oldDescendantList) < len(newDescendantList):

            # what was added
            for newDescendantId in newDescendantList:
                if newDescendantId not in oldDescendantList:
                    if whatChangedId == None or newDescendantList[newDescendantId] < newDescendantList[whatChangedId]:
                        whatChangedId = newDescendantId

        else:

            #what was removed
            for oldDescendantId in oldDescendantList:
                if oldDescendantId not in newDescendantList:
                    if whatChangedId == None or oldDescendantList[oldDescendantId] < oldDescendantList[whatChangedId]:
                        whatChangedId = oldDescendantId


        difCnt = len(newDescendantList) - len(oldDescendantList)
        if difCnt == 0:
            difCnt = ""
        elif difCnt > 0:
            difCnt = "+"+str(difCnt)
        else:
            difCnt = str(difCnt)

        if whatChangedId != None:
            change = "[[{0}|{1}]]".format(whatChangedId, difCnt)
        else:
            change = " {0}".format(difCnt)

    return change


class Reporter:

  def __init__(self):

    self.config = Config()
    self.history = History(self.config)

  def readOldLineage(self):
    path = self.config.studySurname+"_Lineages-{time}.txt".format(time=self.config.args.last_update)
    with open(path, 'r') as file:
        return file.read().rstrip()


  def writeLineages(self, persons):

    self.history.loadPersons(persons)

    Util.log("Found {0} previous descendants, lastUpdate={1}".format(len(self.history.oldPersons), self.config.args.last_update))

    path = self.config.studySurname+"_Lineages-{time}.txt".format(time=self.config.args.date)
    fp = open(path,"w")
    fp.write( "''Auto-generated: {time}''\n".format(time=self.config.args.date) )

    fp.write ( """
{{| border="2" align="center" cellpadding=5 class="wikitable sortable"
|-
! No.
! Size<ref>count of descendants with {studySurname} surname</ref>
! Δ
! Most Distant Known Ancestor
! DNA Notes
|-
""".format(studySurname=self.config.studySurname))

    n = 0
    for person in persons:

        wtId = person.wtId
        label = person.name

        if wtId in self.config.ignoreLineageWikiIds:
            Util.log("Ignoring lineage "+label)
            continue

        n = n + 1

        ancestor = '[[{wikitreeId}|{label}]]'.format(wikitreeId=wtId, label=label)
        ancestor_notes = []
        ancestor_color = ''
        if wtId in self.config.uncertainFatherWikiIds:
            ancestor_notes.append('Uncertain Father')

        fsId = person.profile.getFamilySearchId()
        if fsId:
            ancestor_notes.append("[https://www.familysearch.org/tree/person/details/"+fsId+" "+fsId+"]")

        if person.isRecentEmigrant():
            ancestor_notes.append("Recent Emigrant")
            ancestor_color = 'WhiteSmoke'

        if wtId in self.config.labelLineageWikiIds:
            lineage = self.config.labelLineageWikiIds[wtId]
            ancestor_notes.append(lineage)
            ancestor_color = 'WhiteSmoke'

        dnaLines = {}
        for line in person.lines:

            if wtId != line.wtId:
                lineage = '[[{link}|{label}]]'.format(link=line.wtId, label=line.lineName)
            else:
                lineage = line.lineName

            if line.inStudy == False:
                dnaLines[line.lineName] = line

            ancestor_notes.append(lineage)
            ancestor_color = line.color

        if len(dnaLines)>1:
            ancestor_notes.append("Multiple DNA lines?")


        dna_text = ''
        if person.profile.dnaYCnt() > 0:
            dna_text = 'Y-DNA: {kits}'.format(kits=person.profile.dnaYCnt())
        if person.profile.dnaAuCnt() > 0:
            if dna_text != '':
                dna_text = dna_text + ', '
            dna_text = dna_text + 'auDNA: {kits}'.format(kits=person.profile.dnaAuCnt())
        if person.profile.dnaHasGedmatch() == True:
            dna_text = dna_text + ', GEDMatch'

        change = self.history.whatChanged(person)

        if person.birthPlace:
            flag_img = Util.getFlag(person.birthPlace)
        elif person.deathPlace:
            flag_img = Util.getFlag(person.deathPlace)
        else:
            flag_img = None
        if flag_img:
            flag = "[[Image:"+flag_img+"|35px |"+person.birthPlace+"]] "
        else:
            flag = ""

        if ancestor_color:
            color = " bgcolor="+ancestor_color+" |"
        else:
            color = ""

        if ancestor_notes:
            notes = "<br><sup>" + ", ".join(ancestor_notes)+"</sup>"
        else:
            notes = ""

        if fsId:
            statusColor = " bgcolor=#ECFADC |"
        else:
            statusColor = ""

        if person.wtId not in self.readOldLineage():
            statusColor = " bgcolor=LightBlue |"

        if len(dnaLines)>1:
            statusColor = " bgcolor=#FFC1C3 |"


        fp.write ("""|{statusColor} {rank}
|{numDescendants}
|{change}
|{color} {flag} {ancestor} {notes}
|{dna}
|-\n""".format(
            statusColor=statusColor,
            rank=n,
            numDescendants=len(person.descendants),
            change=change,
            color=color,
            flag=flag,
            ancestor=ancestor,
            notes=notes,
            dna=dna_text,
            ))

    fp.write("|}\n")
    fp.close()

    Util.log(" wrote {n} lineages".format(n=n))



class PersonList:

    def __init__(self):
        self.config = Config()
        self.persons = {}
        self.load()

    def load(self):
        self.persons = PersonDb.getPersonsBySurnames(self.config.args.surnames)
        for pid in self.persons:
            self.persons[pid].descendants = {}
            self.persons[pid].descendants[pid] = self.persons[pid] #simplifies to include self as part of descendants
            self.persons[pid].gen = 1

    def findPersonByWtId(self, wtId):
        for pid in self.persons:
            if self.persons[pid].wtId == wtId:
                return self.persons[pid]

    def calculateEarliestAncestors(self):
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
                father.descendants.update(child.descendants)
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

        good = person.gen >= self.config.args.min_gen \
            or len(person.descendants) >= self.config.args.min_descendants \
            or (person.gen >= self.config.args.min_gen_dna and has_dna) \
            or len(person.lines) > 0 \
            or person.id   in self.config.studyIds \
            or person.wtId in self.config.labelLineageWikiIds \
            or person.wtId in self.config.uncertainFatherWikiIds

        return good


    def getEarliestAncestors(self):

        Util.logr("Calculating lineages ...")
        self.calculateEarliestAncestors()

        Util.logr("Reading lineages ...")

        ancestorList1 = self.earliestAncestors.values()

        lineages = LineageList(self.config)

        Util.logr("Finding lineages ...")

        for person in ancestorList1:
            person.lines = lineages.findDnaLine(person)

            multipleCommonLineages = False
            person.maxLineageDescendantCount = len(person.descendants)
            for lineage in person.lines:
                if lineage.lineName != 'In Study':
                    for relatedLineageWtId in lineages.findLinesByName(lineage.lineName):
                        relatedPerson = self.findPersonByWtId(relatedLineageWtId)
                        if relatedPerson:
                            lineageDescendantCount = len(relatedPerson.descendants)
                            if person.maxLineageDescendantCount < lineageDescendantCount:
                                person.maxLineageDescendantCount = lineageDescendantCount
                            multipleCommonLineages = True

            if multipleCommonLineages:
                person.maxLineageDescendantCount = person.maxLineageDescendantCount + 0.001

        ancestorList2 = sorted([person for person in ancestorList1 if self.isGoodLineagePass1(person)],
                                    key=lambda person: (-person.maxLineageDescendantCount, -len(person.descendants), person.birthYear))

        Util.log("Found "+str(len(ancestorList2))+" good lineages (pass1)")

        for person in ancestorList2:
            person.profile = Profile(person)

        ancestorList3 = [person for person in ancestorList2 if self.isGoodLineagePass2(person)]

        Util.log("Found "+str(len(ancestorList3))+" good lineages (pass2)")

        return ancestorList3



def main():

    PersonDb.init(reload=str(os.getenv('RELOAD'))=="1")

    ancestors = PersonList().getEarliestAncestors()

    reporter = Reporter()
    reporter.writeLineages(ancestors)


if __name__ == "__main__":
    main()
