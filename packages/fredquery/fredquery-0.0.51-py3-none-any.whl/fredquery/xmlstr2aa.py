
import os
import sys
import xml
from xml.etree import ElementTree as ET

class _XMLStr2AA():

    def __init__(self):
        pass

    def xmlstr2aa(self, xmlstr):
        """ xmlstr2aa(xmlstr)

        from an xml string, return an array of rows
        the 0th row contains the keys
        xmlstr - xmlstring to process
        """
        xroot = ET.fromstring(xmlstr)
        rowaa = []
        for child in xroot:
            rowa = []
            if len(rowaa) == 0:
                keya = [k for k in child.attrib.keys()]
                rowaa.append(keya)
            try:
                rowa = [child.attrib[k] for k in rowaa[0]]
            except Exception as e:
                for i in range(len(rowaa[0]) ):
                    key = rowaa[0][i]
                    if key not in child.attrib.keys():
                        rowa.append('no %s' % key)
                    else:
                        rowa.append(child.attrib[key])
            rowaa.append(rowa)
        return rowaa

    def _xmlchild2html(self, croot, htmla):
        for child in croot:
            tag = child.tag
            txt = child.text
            ca = child.attrib
            for c in child:
                self._xmlchild2html(child, htmla)

    def xmlstr2html(self, xmlstr, name):
        """ xmlstr2html(xmlstr)

        SKELETON
        convert an xml strin to an htmlpage that can be a tree of 
        nested tables
        xmlstr - xmlstring to process
        """
        htmla = []
        xroot = ET.fromstring(xmlstr)
        for child in xroot:
            tag = child.tag
            txt = child.text
            ca = child.attrib
            for c in child:
                self._xmlchild2html(child, htmla)
