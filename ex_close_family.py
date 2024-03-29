#!/usr/bin/python3
# -*- coding: utf-8 -*-

from family_tree_lib import *

coreWtId="Waggoner-2455" # Josiah Waggoner 1797
coreWtId="Wagoner-1272"  # John P Wagoner 1787
maxDegree=2

coreWtId="Waggoner-1923"  # Joe Waggoner 1875
maxDegree=3
maxQ=15

PersonDb.init(reload=False)

family = PersonDb.getPersonByWtId(coreWtId).family(maxDegree=maxDegree,wantAnyConnection=False)

quality_family = []

for degrees, fam_person in family:
    if fam_person.birthYear and int(fam_person.birthYear) < 1900:
        points, name, problems = Profile(fam_person).quality()
        q = points + degrees
        if q < maxQ:
            quality_family.append( ( q, degrees, name, fam_person.wtId, problems) )

for n, fam in enumerate(sorted(quality_family)):
    print(str(n)+" "+str(fam))


