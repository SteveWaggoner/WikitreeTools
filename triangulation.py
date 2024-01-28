#!/bin/python

from family_tree_lib import *


class AncestorPair:
    def __init__(self, name, fatherWtId, motherWtId):
        self.name = name
        self.fatherWtId = fatherWtId
        self.motherWtId = motherWtId

class Match:
    def __init__(self, name, guid):
        self.name = name
        self.guid = guid

        self.ancestorPair = None
        self.descendentWtId = None
        self.icwMatches = []

        self.cM = None
        self.segments = None


    def __str__(self):
        return "Match("+self.name+")"

#---------------------

PersonDb.init(reload=str(os.getenv('RELOAD'))=="1")


