from PySide import QtGui, QtCore
from PySide.QtGui import QGraphicsScene, QGraphicsItem, QUndoStack, QUndoCommand
from PySide.QtCore import Signal, Slot, QPointF, QRectF

from gungnode import GungItem, GungPlug, GungNode, GungEdge, getGungNodeClasses
import gc
import sys
import xml.dom.minidom as xmldom
from xml.dom import Node


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
        
        self.highlightedPlugs = []
        self.removedItems = []
        

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

    def getItemById(self, id_):
        
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
        self.isDragging = True
        self.draggingEdge.posStart = dragStart
        self.draggingEdge.posEnd = dragStart
        self.dragFrom = dragFrom
        self.draggingEdge.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.draggingEdge.update()
        self.parent().setCursor(QtCore.Qt.ClosedHandCursor)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MidButton:
            return QGraphicsScene.mouseMoveEvent(self, event)
        if event.buttons() == QtCore.Qt.RightButton:
            return QGraphicsScene.mouseMoveEvent(self, event)
        
        if self.isDragging:
            self.updateDraggingEdge(event.scenePos())
        
            plug = self.getPlugAtPoint(event.scenePos())
            
            highlightedPlug = None
            
            if not plug is None:
                if plug.acceptsDrop(self.dragFrom):
                    plug.setHighlighted(True)
                    highlightedPlug = plug
                    self.highlightedPlugs.append(plug)
                else:
                    self.parent().setCursor(QtCore.Qt.ForbiddenCursor)
            else:
                self.parent().setCursor(QtCore.Qt.ClosedHandCursor)
        else:
            self.parent().unsetCursor()
        
        templist = []
        for item in self.highlightedPlugs:
            if item is highlightedPlug:
                templist.append(item)
                continue
            item.setHighlighted(False)
            
        self.highlightedPlugs = templist
        
        return QGraphicsScene.mouseMoveEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        if self.nodesHaveMoved:
            self.checkIfNodesMoved()
            self.nodesHaveMoved = False
            
        for item in self.highlightedPlugs:
            item.setHighlighted(False)
        self.highlightedPlugs = []
        
        return QGraphicsScene.mouseReleaseEvent(self, event)

    def checkIfNodesMoved(self):
        """
        Iterate all the nodes to see if they positions changed in comparison to the
        position values that they have stored in properties dictionary
        """
        
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
            undo.nodes[int(node.properties['nodeId'])] = [
                float(node.properties['posX']),
                float(node.properties['posY']),
                float(nodepos.x()),
                float(nodepos.y())
            ]

            #--- keep current position in the values of a dictionary so that this node will not be collected as moved
            #--- next time when scene checks if some nodes have moved.
            node.properties['posX'] = float(nodepos.x())
            node.properties['posY'] = float(nodepos.y())

        self.undoStack.push(undo)
        self.nodesHaveMoved = False
        
    def getPlugAtPoint(self, pos):
        """
        Iterate all the items that occlude with the point passed as pos and see if there is a GungPlug among them.
        If not then return None
        @param pos: QPoint
        @return GungNode or None
        """
        hititems = self.items(pos)
        if not len(hititems):
            return
        hititem = None
        for hi in hititems:
            if isinstance(hi, GungPlug):
                hititem = hi
                break
            
        return hititem

    def draggingEnded(self, pos):
        #--- it the scene is not in "dragging" state then it means that
        #--- no action is necessary here
        if not self.isDragging:
            return
        
        #--- stop displaying the utility edge
        self.hideDraggingEdge()
        
        hititem = self.getPlugAtPoint(pos)
        
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
                print edge
                return
        for edge in hititem.edges:
            if edge is None:
                continue
            if self.dragFrom in [edge.itemFrom, edge.itemTo]:
                return
        
        #--- finally create an edge

        command = GungCreateEdgeCommand(self, self.dragFrom, hititem)
        self.undoStack.push(command)
        
    def removeEdge(self, edgeId):
        createdEdge = self.getItemById(edgeId)
        if createdEdge is None:
            return
        createdEdge.disconnectEdge()
        createdEdge.prepareGeometryChange()        
        self.removeItem(createdEdge)
        
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
        self.parent().unsetCursor()

    def resizeNode(self, nodeId, size, previousSize):
        c = GungResizeNodeCommand(self, nodeId, size.x(), size.y(), previousSize.x(), previousSize.y())
        self.undoStack.push(c)

    @Slot()
    def deleteCalled(self):
        sel = self.selectedItems()
        nodes = []
        for item in sel:
            if isinstance(item, GungNode):
                nodes.append(item)
        if len(nodes):
            command = GungDeleteItemsCommand(self, nodes)
            self.undoStack.push(command)

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
            gnode = self.scene.getItemById(n)
            gnode.setX(self.nodes[n][0])
            gnode.setY(self.nodes[n][1])
            gnode.properties['posX'] = self.nodes[n][0]
            gnode.properties['posY'] = self.nodes[n][1]
        self.scene.nodesHaveMoved = False

    def redo(self, *args, **kwargs):
        for n in self.nodes.keys():
            gnode = self.scene.getItemById(n)
            gnode.setX(self.nodes[n][2])
            gnode.setY(self.nodes[n][3])
            gnode.properties['posX'] = self.nodes[n][2]
            gnode.properties['posY'] = self.nodes[n][3]
        self.scene.nodesHaveMoved = False


class GungDeleteItemsCommand(QUndoCommand):
    """
    Removes items provided to the constructor.
    """
    def __init__(self, scene, nodes):
        QUndoCommand.__init__(self)
        self.scene = scene
        self.nodes = [x for x in nodes]
        
        self.edges = []

    def undo(self, *args, **kwargs):
        for n in self.nodes:
            self.scene.addItem(n)
            
        for e in self.edges:
            self.scene.addItem(e)
            e.reconnectEdge()
            
    def redo(self, *args, **kwargs):
        edgesToDelete = []
        for n in self.nodes:
            edgesToDelete += n.getAllEdges()
        
        for edge in edgesToDelete:
            edge.disconnectEdge()
        self.edges = edgesToDelete
        
        for e in edgesToDelete:
            self.scene.removeItem(e)
        
        for item in self.nodes:
            self.scene.removeItem(item)


class GungCreateEdgeCommand(QUndoCommand):
    """
    Creates an edge between two plugs provided in the constructor.
    """
    def __init__(self, scene, fromNode, toNode):
        QUndoCommand.__init__(self)
        self.fromNodeId = int(fromNode.properties['nodeId'])
        self.toNodeId = int(toNode.properties['nodeId'])
        self.scene = scene
        self.createdEdgeId = -1
        self.deletedEdge = None

    def undo(self, *args, **kwargs):
        self.scene.removeEdge(self.createdEdgeId)

    def redo(self, *args, **kwargs):
        e = GungEdge(int(self.fromNodeId), int(self.toNodeId), parent=None, scene=self.scene)
        e.reconnectEdge()
        self.createdEdgeId = int(e.properties['nodeId'])

class GungResizeNodeCommand(QUndoCommand):
    """
    Resizes the node.
    """
    def __init__(self, scene, nodeId, width, height, previousWith, previousHeight):
        QUndoCommand.__init__(self)
        self.nodeId = int(nodeId)
        self.width = float(width)
        self.height = float(height)
        self.previousWidth = float(previousWith)
        self.previousHeight = float(previousHeight)
        self.scene = scene

    def undo(self, *args, **kwargs):
        node = self.scene.getItemById(self.nodeId)
        node.resizer.setX(self.previousWidth)
        node.resizer.setY(self.previousHeight)

    def redo(self, *args, **kwargs):
        node = self.scene.getItemById(self.nodeId)
        node.resizer.setX(self.width)
        node.resizer.setY(self.height)

class GungDragEdge(QGraphicsItem):
    """
    Graphics item that is responsible for displaying the rubber band edge (used to visually
    create connections).
    """
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
