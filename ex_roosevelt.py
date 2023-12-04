#!/usr/bin/python3
# -*- coding: utf-8 -*-


from family_tree_lib import *


FDR="Roosevelt-1"
Teddy="Roosevelt-18"
Astor="Astor-15"

PersonDb.init()

fdrFamily   = PersonDb.getPersonByWtId(FDR).family(maxDegree=3,wantAnyConnection=True)
teddyFamily = PersonDb.getPersonByWtId(Teddy).family(maxDegree=3,wantAnyConnection=True)
astorFamily = PersonDb.getPersonByWtId(Astor).family(maxDegree=3,wantAnyConnection=True)
#meFamily = Person.getPersonByWtId("Waggoner-1719").family(maxDegree=3,wantAnyConnection=True)
meFamily = PersonDb.getPersonByWtId("Waggoner-1945").family(maxDegree=3,wantAnyConnection=True)


def getFirstPerson(person):
    firstPerson = person
    firstPerson.nextPerson = None #clear last
    while firstPerson.prevPerson is not None:
        firstPerson.prevPerson.nextPerson = firstPerson  # update next person
        firstPerson = firstPerson.prevPerson

    return firstPerson


def getChain(person):
    person = getFirstPerson(person)
    chain = []
    while person is not None:
        chain.append(person)
        person = person.nextPerson
    return chain


def commonMembers(family1,family2):

    common = {}
    min_ttl_deg = None

    for deg1, per1 in family1:
        for deg2, per2 in family2:
            if per1.id == per2.id:
                ttl_deg = deg1 + deg2

                if min_ttl_deg is None or min_ttl_deg >= ttl_deg:
                    min_ttl_deg = ttl_deg

                if per1.id in common:
                    if common[per1.id][1] > ttl_def:
                        common[per1.id] = (per1, per2, ttl_deg)
                else:
                    common[per1.id] = (per1, per2, ttl_deg)

    if len(common)==0:
        print("Nothing in common.")


    part1 = []
    part2 = []
    for common_id in common:
        per1, per2, deg = common[common_id]
        if deg == min_ttl_deg:

            part1 = getChain(per1)
            part2 = getChain(per2)

            print("==== "+str(deg) +" ====")

            for n, p in enumerate(part1):
                print(str(n)+". "+str(p))

            print("")
            for n, p in enumerate(reversed(part2)):
                print(str(n)+". "+str(p))

common = commonMembers(fdrFamily, astorFamily)

