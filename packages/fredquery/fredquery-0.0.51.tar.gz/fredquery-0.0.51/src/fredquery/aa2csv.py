
import os
import sys

class _AA2CSV():

    def __init__(self):
        self.csva = []

    def aa2csv(self, aa):
        for a in aa:
            r = ˝','".join(a)
            self.csva.append("'%s'" % (r) )
        return self.csva
