from PySide.QtGui import QGraphicsScene

from gungnode import GungItem, GungNode, getGungNodeClasses

import xml.dom.minidom as xmldom
from xml.dom import Node


class GungScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.topZ = 0.0000

    def getNewId(self):
        index = 0
        currentIds = []
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if not "nodeId" in item.properties.keys():
                continue
            
            currentIds.append(item.properties["nodeId"])

        while index in currentIds:
            index += 1

        return index

    def getNodeById(self, id_):
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if item.properties["nodeId"] == id_:
                return item
        return None

    def asXml(self):
        """
        Returns self as an xml document.
        """
        impl = xmldom.getDOMImplementation()
        doc = impl.createDocument(None, "GungGraph", None)

        for node in self.items():
            
            if isinstance(node, GungNode):
                if not node.parentItem() is None:
                    continue
                
                xmlnode = node.asXml(doc)
                doc.documentElement.appendChild(xmlnode)
                sc = node.scene()  # I don't know why it's corrupted without it...
        return doc
    
    def fromXml(self, xmlstring):
        """
        Parses XML string and fills the current scene with the nodes. The scene MUST be empty since
        this method sets the node id's that are loaded to the values stored in an xml.
        """
        dom = xmldom.parseString(xmlstring)
        
        classes = getGungNodeClasses()
         
        for node in dom.documentElement.childNodes:
            if not node.nodeType == Node.ELEMENT_NODE:
                continue
            if not node.tagName in classes.keys():
                continue
            gn = classes[node.tagName](parent=None, scene=self)
            gn.fromXml(node)

