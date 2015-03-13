from PySide import QtGui
from PySide.QtGui import QGraphicsScene, QGraphicsItem
from PySide.QtCore import Signal, QPointF, QRectF

from gungnode import GungItem, GungNode, GungEdge, getGungNodeClasses

import xml.dom.minidom as xmldom
from xml.dom import Node
from gungnode import GungPlug


class GungDragEdge(QGraphicsItem):
    def __init__(self, scene=None):
        QGraphicsItem.__init__(self, None, scene)

        self.edgePen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.setZValue(2.000)

        self.posStart = None
        self.posEnd = None

    def paint(self, painter, option, widget=None):
        if not self.scene().isDragging:
            return

        painter.setPen(self.edgePen)

        if self.posStart is None or self.posEnd is None:
            return

        currentpos = self.mapToScene(QPointF())

        painter.drawLine(self.posStart - currentpos, self.posEnd - currentpos )

    def updatePosition(self):
        if self.posStart is None or self.posEnd is None:
            return

        topleftX = min(self.posStart.x(), self.posEnd.x())
        topleftY = min(self.posStart.y(), self.posEnd.y())
        
        self.setPos(QPointF(topleftX, topleftY))
        self.update()

    def boundingRect(self, *args, **kwargs):
        if not self.scene().isDragging:
            return QRectF()

        if self.posStart is None or self.posEnd is None:
            return QRectF()

        topleftX = min(self.posStart.x(), self.posEnd.x())
        topleftY = min(self.posStart.y(), self.posEnd.y())

        bottomrightX = max(self.posStart.x(), self.posEnd.x())
        bottomrightY = max(self.posStart.y(), self.posEnd.y())

        return QRectF(0, 0, bottomrightX - topleftX, bottomrightY - topleftY)

    def mouseReleaseEvent(self, *args, **kwargs):
        return QGraphicsItem.mouseReleaseEvent(self, *args, **kwargs)

class GungScene(QGraphicsScene):
    draggingStarted = Signal(int)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.topZ = 0.0000
        self.topEdgeZ = 1.0000
        self.isDragging = False
        self.createDraggingEdge()

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

        for i in self.items():
            if not isinstance(i, GungEdge):
                continue
            i.reconnectEdge()

    def createDraggingEdge(self):
        self.draggingEdge = GungDragEdge(scene=self)

    def initDraggingEdge(self, dragStart, dragFrom):
        """
        Starts the dragging and sets the start position of a dragged edge.
        :param dragStart: QPointF
        :param dragFrom: GungItem
        :return:
        """
        """
        :param dragStart:
        :return:
        """
        self.isDragging = True
        self.draggingEdge.posStart = dragStart
        self.draggingEdge.posEnd = dragStart
        self.dragFrom = dragFrom
        self.draggingEdge.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.draggingEdge.update()
        
    def mouseMoveEvent(self, event):
        if self.isDragging:
            self.updateDraggingEdge(event.scenePos())
        return QGraphicsScene.mouseMoveEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        return QGraphicsScene.mouseReleaseEvent(self, event)

    def draggingEnded(self, pos):
        #--- it the scene is not in "dragging" state then it means that
        #--- no action is necessary here
        if not self.isDragging:
            return
        
        #--- stop displaying the utility edge
        self.hideDraggingEdge()
        
        #--- iterate all the items that occlude with the place where dragging stopped
        #--- and see if there is a GungPlug among them. If not then return None
        hititems = self.items(pos)
        if not len(hititems):
            return
        hititem = None
        for hi in hititems:
            if isinstance(hi, GungPlug):
                hititem = hi
                break
        
        #--- stop if no plug is found
        if hititem is None:
            return
        
        #--- top if there is no item from which the dragging started
        if self.dragFrom is None:
            return
        
        #--- quit if the dragging ended on the same item
        if self.dragFrom is hititem:
            return
        
        #--- check it maybe there is already a connection between those plugs
        for edge in self.dragFrom.edges:
            if edge is None:
                continue
            if hititem in [edge.itemFrom, edge.itemTo]:
                return
        for edge in hititem.edges:
            if edge is None:
                continue
            if self.dragFrom in [edge.itemFrom, edge.itemTo]:
                return
        
        #--- finally create an edge
        e = GungEdge(scene=self)
        e.properties['itemFromId'] = self.dragFrom.properties['nodeId']
        e.properties['itemToId'] = hititem.properties['nodeId']
        e.reconnectEdge()
        
    def updateDraggingEdge(self, pos):
        self.draggingEdge.posEnd = pos
        self.draggingEdge.updatePosition()

    def hideDraggingEdge(self):
        self.isDragging = False
        self.draggingEdge.posStart = None
        self.draggingEdge.posEnd = None
        self.draggingEdge.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, True)
        self.draggingEdge.update()
        self.update()
