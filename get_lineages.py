#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse
import gzip

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


def log(msg):
    sys.stderr.write('{m}\n'.format(m=msg))


def logr(msg):
    sys.stderr.write('{m}                 \r'.format(m=msg))


log(args)


def openGz(path):
    log('Reading ' + path)
    return gzip.open(path, 'rb')


def getStudyIds():
    studyName = '{surname}_Name_Study'.format(surname=studySurname)
    userIds = []
    n = 0
    for line in openGz(args.category_file):
        n = n + 1
        if n % 1000000 == 0:
            logr(n)
        tokens = line.split('\t')
        if tokens[1].strip() == studyName:
            userIds.append(tokens[0])
        if args.test:
            break

    log(' found {cnt} profiles in {surname} study'.format(cnt=len(userIds),
        surname=studySurname))
    return userIds


studyIds = getStudyIds()


def getWebPage(url):
    import urllib2
    try:
        contents = urllib2.urlopen(url).read()
        return contents
    except:
        return ''


def getBetween(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except:
        return ''


cacheProfileDNA = {}
cacheTrys = 0
cacheHits = 0


def getProfileDNA(profile):
    wikitreeId = profile['WikiTree ID']

    global cacheTrys
    global cacheHits

    if cacheTrys % 100 == 0 and cacheTrys > cacheHits:
        saveCacheProfileDNA()

    cacheTrys = cacheTrys + 1
    if wikitreeId in cacheProfileDNA and not args.ignore_dna_cache:
        cacheHits = cacheHits + 1
        return cacheProfileDNA[wikitreeId]

    url = 'https://www.wikitree.com/wiki/' + wikitreeId
    contents = getWebPage(url)

    editedByMe = "Waggoner-1719" in getBetween(contents, '<span class=\'HISTORY-ITEM\'>', '</span>')

    try:
        start = '<ul class="y">'
        end = '</ul>'
        y_dna = getBetween(contents, start, end)
        y_dna_cnt = y_dna.count('<li>')
    except:
        y_dna_cnt = 0

    try:
        start = '<ul class="au">'
        end = '</ul>'

        au_dna = getBetween(contents, start, end)
        au_dna_cnt = au_dna.count('<li>')
        au_dna_best = au_dna.split('<li>')[1]

        start2 = 'share about '
        end2 = '% of their DNA'
        au_dna_best_pct = getBetween(au_dna_best, start2, end2)

        au_has_gedmatch = au_dna.count('gedmatch.com') > 0
    except:

        au_dna_cnt = 0
        au_dna_best_pct = None
        au_has_gedmatch = False

    from datetime import datetime
    curDate = datetime.today().strftime('%Y-%m-%d')
    stats = (y_dna_cnt, au_dna_cnt, au_dna_best_pct, au_has_gedmatch, curDate, editedByMe)
    cacheProfileDNA[wikitreeId] = stats
    return stats


cacheProfileDNAPath = './cache/profileDNA.txt'


def loadCacheProfileDNA():
    log('Reading ' + cacheProfileDNAPath)
    try:
        for line in open(cacheProfileDNAPath):
            tokens = line.strip().split('|')
            cacheProfileDNA[tokens[0]] = (tokens[1], tokens[2],
                    tokens[3], tokens[4], tokens[5], tokens[6])

    except Exception, e:
        print 'Failed to load: {file} ({e})'.format(file=cacheProfileDNAPath,
                e=e)
    log(" {cnt} cached profiles loaded".format(cnt=len(cacheProfileDNA)))


loadCacheProfileDNA()


def saveCacheProfileDNA():
    log('Writing {file} (trys={trys}, hits={hits})'.format(file=cacheProfileDNAPath,
        trys=cacheTrys, hits=cacheHits))
    f = open(cacheProfileDNAPath, 'w')
    for (id, t) in sorted(cacheProfileDNA.iteritems()):
        f.write('{id}|{t0}|{t1}|{t2}|{t3}|{t4}|{t5}\n'.format(id=id, t0=t[0],
                t1=t[1], t2=t[2], t3=t[3], t4=t[4], t5=t[5]))
    f.close()


cachedUserIds = {}


def getWikitreeId(userId, profiles):
    if userId in cachedUserIds:
        return cachedUserIds[userId]

    for (wikitreeId, profile) in profiles.iteritems():
        if profile['User ID'] == userId:
            cachedUserIds[userId] = wikitreeId
            return wikitreeId


def getFather(child, profiles):
    return getWikitreeId(child['Father'], profiles)


def earliestAncestor(row, profiles):
    ancestor = row

    id = getFather(ancestor, profiles)
    while id != None:
        ancestor = profiles[id]
        id = getFather(ancestor, profiles)

    return {'wikitreeId': ancestor['WikiTree ID']}


def countDescendents(row, profiles):

    if 'Children' in row:
        cnt = len(row['Children'])
        for c in row['Children']:
            cnt = cnt + countDescendents(profiles[c], profiles)

        return cnt
    else:
        return 0


def countGenerations(row, profiles, depth=0):

    if 'Children' in row:

        max_depth = depth

        for c in row['Children']:
            tmp_depth = countGenerations(profiles[c], profiles, depth
                    + 1)
            if max_depth < tmp_depth:
                max_depth = tmp_depth

        return max_depth
    else:
        return depth


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


def getDnaLines(profiles):

    log('getDnaLines...')
    lines = {}

    dnaTabName = 'Space:{surname}_Name_Study_-_DNA'.format(surname=studySurname)

    dnaTab = getWebPage('https://www.wikitree.com/wiki/{dnaTabName}'.format(dnaTabName=dnaTabName))



    start = '<th> Lineage'
    end = '</table>'
    start2 = '<a name="Other_Lineages_without_DNA'
    end2 = 'work in progress'
    for classified in getBetween(dnaTab, start, end).split('<tr>'):
        try:
            color = getBetween(classified, ' bgcolor="', '"')
            lineName = getBetween(getBetween(classified, ' bgcolor="',
                                  '/td>'), '>', '<').strip()
            wikitreeId = getBetween(classified, '<a href="/wiki/', '"')

            lines[wikitreeId] = {'Color': color, 'Name': lineName,
                                 'WikitreeId': wikitreeId}
        except:
            log('no profile')

    for unclassified in getBetween(dnaTab, start2, end2).split('<tr>'):
        try:
            wikitreeId = getBetween(unclassified, '<a href="/wiki/', '"'
                                    )
            lines[wikitreeId] = {'Color': 'WhiteSmoke',
                                 'Name': 'Unclassified',
                                 'WikitreeId': wikitreeId}
        except:
            log('no profile')

    for studyId in studyIds:
        studyWikitreeId = getWikitreeId(studyId, profiles)
        if studyWikitreeId not in lines:
            lines[studyWikitreeId] = {'Color': 'WhiteSmoke',
                    'Name': 'In Study', 'WikitreeId': studyWikitreeId}

    return lines


def findDnaLine2(wikitreeId, profiles, dnaLines, includeStudy, lines):

    if wikitreeId in dnaLines and (includeStudy
                                   or dnaLines[wikitreeId]['Name']
                                   != 'In Study'):
        lines.append(dnaLines[wikitreeId])
    else:
        profile = profiles[wikitreeId]
        if 'Children' in profile:
            for child in profile['Children']:
                findDnaLine2(child, profiles, dnaLines, includeStudy,
                             lines)


# prioritize dna lines over just in study

def findDnaLine(wikitreeId, profiles, dnaLines):
    lines = []
    findDnaLine2(wikitreeId, profiles, dnaLines, False, lines)
    if len(lines) == 0:
        findDnaLine2(wikitreeId, profiles, dnaLines, True, lines)
    return lines


def getPeople():

    partialSurName = commonSubstring(args.surnames)

    i = 0
    profiles = {}
    for line in openGz(args.people_user_file):
        i = i + 1
        if i % 1000000 == 0:
            logr(str(i) + "  " + str(len(profiles)))

        if i == 1:
            log(' partialSurName = ' + partialSurName)
            tokens = line.strip().split('\t')
            fields = tokens
        else:
            if partialSurName in line:

                tokens = line.strip().split('\t')
                row = dict(zip(fields, tokens))

                lastName = row['Last Name at Birth']
                if lastName in args.surnames:
                    wikitreeId = row['WikiTree ID']
                    profiles[wikitreeId] = row
        if args.test and len(profiles) > 100:
            break
    log(' found {cnt} profiles matching surnames'.format(cnt=len(profiles)))
    return profiles


def updateEarliestAncestors(profiles):

    log('updateEarliestAncestors...')
    n = 0
    for (wikitreeId, profile) in profiles.iteritems():
        n = n + 1
        if n % 100 == 0:
            logr(n)
        profile['Ancestor'] = earliestAncestor(profile, profiles)


def updateChildren(profiles):

    log('updateChildren...')
    for (childId, child) in profiles.iteritems():
        fatherId = getFather(child, profiles)
        if fatherId in profiles:
            father = profiles[fatherId]
            if 'Children' in father:
                father['Children'].append(childId)
            else:
                father['Children'] = [childId]


def getProfileLabel(profile):
    birth_year = (profile['Birth Date'])[:4]
    death_year = (profile['Death Date'])[:4]

    if int(birth_year) == 0:
        birth_year = ''

    if int(death_year) == 0:
        death_year = ''

    birth_location = getAbbreviatedLocation(profile['Birth Location'])
    death_location = getAbbreviatedLocation(profile['Death Location'])

    if birth_location == death_location:
        death_location = ''

    birth_text = (birth_year + ' ' + birth_location).strip()
    death_text = (death_year + ' ' + death_location).strip()

    dates = ''
    if birth_text != '' and death_text != '':
        dates = '({birth} - {death})'.format(birth=birth_text,
                death=death_text)
    else:
        if birth_text != '':
            dates = '({birth})'.format(birth=birth_text)
        if death_text != '':
            dates = '(died {death})'.format(death=death_text)

    label = '{first} {last} {dates}'.format(first=(profile['First Name'] +
            ' ' + profile['Middle Name']).strip(),
            last=profile['Last Name at Birth'], dates=dates)
    return label


def isGood(profile):

    # criteria: must have dna, be assign to a line or be in the study
    try:
        has_dna = int(profile['DNA'][1]) > 0
    except:
        has_dna = True   # if don't know, assume you have it

    good = profile['Gen'] >= args.min_gen \
            or (profile['Gen'] >= args.min_gen_dna and has_dna) \
            or (profile['Gen'] >= args.min_gen_dna_exact_name and has_dna and profile['Last Name at Birth'] == exactSurname) \
            or profile['Line'] != None \
            or profile['User ID'] in studyIds
    return good


def getAncestors(profiles, dnaLines):

    log('getAncestors...')

    n = 0
    ancestors = {}
    for (wikitreeId, profile) in profiles.iteritems():
        n = n + 1
        ancestorId = profile['Ancestor']['wikitreeId']
        if not ancestorId in ancestors:

            ancestor = profiles[ancestorId]
            if getFather(ancestor, profiles) == None:
                ancestor['Gen'] = countGenerations(ancestor, profiles)
                ancestor['Descendents'] = countDescendents(ancestor,
                        profiles)
                lines = findDnaLine(ancestorId, profiles, dnaLines)
                if len(lines) > 0:
                    ancestor['Line'] = lines[0]
                    if len(lines) > 1:
                        ancestor['Line2'] = lines[1]
                    else:
                        ancestor['Line2'] = None
                else:
                    ancestor['Line'] = None
                    ancestor['Line2'] = None

                if isGood(ancestor):
                    ancestor['DNA'] = getProfileDNA(ancestor)
                else:
                    ancestor['DNA'] = (0,0,None,None,'','')
                ancestors[ancestorId] = ancestor

            logr(str(n)+"  "+str(len(ancestors)))

    ancestorArr = []
    for (id, ancestor) in ancestors.iteritems():
        ancestorArr.append(ancestor)

    log(' found {cnt} common ancestors'.format(cnt=len(ancestorArr)))

    # sort largest descendent count first, then have dna first, then birth date ascending,
    ancestorsSorted1 = sorted(ancestorArr, key=lambda a: (not '1' in getProfileLabel(a), int((a['Birth Date'])[:4]), getProfileLabel(a)))
    ancestorsSorted2 = sorted(ancestorsSorted1, key=lambda a: (a['Descendents'], int(a['DNA'][0]) > 0 or int(a['DNA'][1]) > 0), reverse=True)
    return ancestorsSorted2


def getAbbreviatedLocation(location):

    abbrs = [
        ('Germany', 'Ger'),
        ('Deutschland', 'Ger'),
        ('Saxony', 'Ger'),
        ('Heiliges R', 'Ger'),
        ('Pennsylvania', 'PA'),
        ('North Carolina', 'NC'),
        ('France', 'France'),
        ('Illinois', 'IL'),
        ('Virginia', 'VA'),
        (' Pa.', 'PA'),
        ('Luxembourg', 'Luxembourg'),
        (', MD', 'MD'),
        ('Ohio', 'OH'),
        ('Maryland', 'MD'),
        (', Pa', 'PA'),
        ('West Prussia', 'Prussia'),
        ('Prussia', 'Prussia'),
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


def printAncestors(profiles, previousDescendents, lastUpdate):

    log('printAncestors...')


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

        good = isGood(profile)
        if not good:
            continue

        n = n + 1
        label = getProfileLabel(profile)

        ancestor = '[[{wikitreeId}|{label}]]'.format(wikitreeId=profile['WikiTree ID'], label=label.strip())

        dna = profile['DNA']

        if profile['Line']:
            if profile['WikiTree ID'] != profile['Line']['WikitreeId']:
                lineage = '[[{link}|{label}]]'.format(link=profile['Line']['WikitreeId'],
                        label=profile['Line']['Name'])
            else:
                lineage = profile['Line']['Name']

            if profile['Line2']:
                extra = ''

                color2 = ' || bgcolor=' + profile['Line2']['Color'] + ' | '
                if profile['WikiTree ID'] != profile['Line2']['WikitreeId']:
                    lineage2 = '[[{link}|{label}]]'.format(link=profile['Line2']['WikitreeId'], label=profile['Line2']['Name'])
                else:
                    lineage2 = profile['Line2']['Name']
            else:

                extra = 'colspan=2 '
                color2 = ''
                lineage2 = ''

            color = extra + 'bgcolor=' + profile['Line']['Color'] + ' | '
        else:

            if dna[5] == 'True':
               color = ' colspan=2 bgcolor=WhiteSmoke |'
               lineage = 'Recent Edit'
            else:
               color = ' colspan=2 | '
               lineage = ''
            lineage2 = ''
            color2 = ''


        dna_text = ''
        if int(dna[0]) > 0:
            dna_text = 'Y-DNA: {kits}'.format(kits=dna[0])
        if int(dna[1]) > 0:
            if dna_text != '':
                dna_text = dna_text + ', '
            dna_text = dna_text + 'auDNA: {kits} ({pct}%)'.format(kits=dna[1], pct=dna[2])
        if str(dna[3]) == 'True':
            dna_text = dna_text + ', GEDMatch'

        change = ""
        if args.last_update_file != "":
            if profile['WikiTree ID'] in previousDescendents:
                change = "| {0:+d}".format(profile['Descendents'] - previousDescendents[profile['WikiTree ID']])
            else:
                change = "|"

        print """
| #{rank}
| {gen}
| {descendents}
{change}
| {ancestor}
| {color} {lineage} {color2} {lineage2}
| {dna}
|-""".format(
            rank=n,
            gen=profile['Gen'],
            descendents=profile['Descendents'],
            change=change,
            ancestor=ancestor,
            color=color,
            lineage=lineage,
            color2=color2,
            lineage2=lineage2,
            dna=dna_text,
            )

    print '|}'

    log(" wrote {n} lineages".format(n=n))


def getPreviousDescendents():
    previousDescendents = {}
    lastUpdate = ""
    if len(args.last_update_file):
        lastUpdate = args.last_update_file.split('-',1)[1].split('.')[0]
        log("Reading " + args.last_update_file)
        n = 0
        for rawline in open(args.last_update_file):
            line = rawline.strip()

            if line[:1] == "|":
                if line == "|-":
                    n = 0
                if n == 3:
                    descendentCnt = int(line.split('|')[1])
                if n == 5:
                    wtId = getBetween(line,"[[", "|")
                    previousDescendents[wtId] = descendentCnt
                n = n + 1

        log(" found {cnt} previous descendents for {lastUpdate}".format(cnt=len(previousDescendents),lastUpdate=lastUpdate))
    return (previousDescendents,lastUpdate)


def main():
    (previousDescendents, lastUpdate) = getPreviousDescendents()

    people = getPeople()
    updateEarliestAncestors(people)
    updateChildren(people)

    dnaLines = getDnaLines(people)
    ancestors = getAncestors(people, dnaLines)

    printAncestors(ancestors,previousDescendents, lastUpdate)

    saveCacheProfileDNA()


main()

