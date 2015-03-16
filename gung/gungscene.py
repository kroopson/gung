from PySide import QtGui
from PySide.QtGui import QGraphicsScene, QGraphicsItem, QUndoStack, QUndoCommand
from PySide.QtCore import Signal, Slot, QPointF, QRectF

from gungnode import GungItem, GungNode, GungEdge, getGungNodeClasses

import xml.dom.minidom as xmldom
from xml.dom import Node
from gungnode import GungPlug



class GungScene(QGraphicsScene):
    draggingStarted = Signal(int)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.topZ = 0.0000
        self.topEdgeZ = 1.0000
        self.isDragging = False
        self.dragFrom = None
        self.draggingEdge = GungDragEdge(scene=self)
        self.nodesHaveMoved = False
        self.undoStack = QUndoStack(self)

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
        if self.nodesHaveMoved:
            self.checkIfNodesMoved()
            self.nodesHaveMoved = False
        
        if self.isDragging:
            self.draggingEnded(event.pos())
        return QGraphicsScene.mouseReleaseEvent(self, event)

    def checkIfNodesMoved(self):
        #--- iterate all the nodes to see if they positions changed in comparison to the
        #--- position values that they have stored in properties dictionary
        nodesThatHaveMoved = []
        for item in self.items():
            if not isinstance(item, GungNode):
                continue
            p = item.pos()
            if p.x() != item.properties['posX'] or p.y() != item.properties['posY']:
                nodesThatHaveMoved.append(item)

        #--- if no nodes have moved return
        if not len(nodesThatHaveMoved):
            return

        undo = GungMoveCommand(self)
        for node in nodesThatHaveMoved:
            nodepos = node.pos()
            undo.nodes[node.properties['nodeId']] = [
                node.properties['posX'],
                node.properties['posY'],
                nodepos.x(),
                nodepos.y()
            ]

            #--- keep current position in the values of a dictionary so that this node will not be collected as moved
            #--- next time when scene checks if some nodes have moved.
            node.properties['posX'] = nodepos.x()
            node.properties['posY'] = nodepos.y()

        self.undoStack.push(undo)
        self.nodesHaveMoved = False

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
        
        #--- check if the in-plug actually accepts connections from the GungPlug held in self.dragFrom
        if not hititem.acceptsDrop(self.dragFrom):
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

        command = GungCreateEdgeCommand(self, self.dragFrom, hititem)
        self.undoStack.push(command)
        
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

    @Slot()
    def redoCalled(self):
        self.undoStack.redo()

    @Slot()
    def undoCalled(self):
        self.undoStack.undo()


class GungMoveCommand(QUndoCommand):
    def __init__(self, scene):
        """
        This dictionary has to hold the id's as the keys and positions as values.
        i.e.
        {
        10 : [0,0,250,100]
        }
        """
        QUndoCommand.__init__(self)
        self.nodes = {}
        self.scene = scene

    def undo(self, *args, **kwargs):
        for n in self.nodes.keys():
            gnode = self.scene.getNodeById(n)
            gnode.setX(self.nodes[n][0])
            gnode.setY(self.nodes[n][1])
            gnode.properties['posX'] = self.nodes[n][0]
            gnode.properties['posY'] = self.nodes[n][1]
        self.scene.nodesHaveMoved = False

    def redo(self, *args, **kwargs):
        for n in self.nodes.keys():
            gnode = self.scene.getNodeById(n)
            gnode.setX(self.nodes[n][2])
            gnode.setY(self.nodes[n][3])
            gnode.properties['posX'] = self.nodes[n][2]
            gnode.properties['posY'] = self.nodes[n][3]
        self.scene.nodesHaveMoved = False

class GungCreateEdgeCommand(QUndoCommand):
    def __init__(self, scene, fromNode, toNode):
        """
        This dictionary has to hold the id's as the keys and positions as values.
        i.e.
        {
        10 : [0,0,250,100]
        }
        """
        QUndoCommand.__init__(self)
        self.fromNode = fromNode
        self.toNode = toNode
        self.scene = scene
        self.createdEdge = None

    def undo(self, *args, **kwargs):
        self.createdEdge.disconnectEdge()
        self.scene.removeItem(self.createdEdge)

    def redo(self, *args, **kwargs):
        e = GungEdge(scene=self.scene)
        e.properties['itemFromId'] = self.fromNode.properties['nodeId']
        e.properties['itemToId'] = self.toNode.properties['nodeId']
        e.reconnectEdge()
        self.createdEdge = e

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
