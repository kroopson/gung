import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from PySide.QtCore import QPoint
from xml.dom import Node
import inspect
import sys

from config import GungConfig
config = GungConfig()



def getGungNodeClasses():
    gungClasses = {}
    for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if "elementType" in obj.__dict__.keys():
            gungClasses[name] = obj
    return gungClasses


class GungNodeResizer(QtGui.QGraphicsItem):
    """
    A small widget displayed in a bottom right corner of the node. When it is moved
    it will resize the parent GungNode.
    """

    def __init__(self, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.storedPos = QtCore.QPointF()

        # TODO: Store this in some settings.
        self.itemWidth = 10
        self.itemHeight = 10

        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))

        self.sizePoint = QPoint(self.itemWidth, self.itemHeight)

    def mousePressEvent(self, *args, **kwargs):
        self.setCursor(QtCore.Qt.SizeFDiagCursor)
        self.storedPos = self.pos()
        return QtGui.QGraphicsItem.mousePressEvent(self, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.unsetCursor()
        p = self.pos()
        if p != self.storedPos:
            # --- When this item position is changed call the trigger signal resizeNode.
            #--- This allows undo/redo of this command.
            self.scene().resizeNode(self.parentItem().properties['nodeId'], p + self.sizePoint,
                                    self.storedPos + self.sizePoint)
        return QtGui.QGraphicsItem.mouseReleaseEvent(self, *args, **kwargs)

    def paint(self, painter, option, widget=None):
        """
        Override of a paint class from QGraphicsItem.
        Implement this to give a resizer the desired look.
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # draw body of a node
        if self.parentItem().isSelected():
            painter.setPen(self.parentItem().selectedPen)
        else:
            painter.setPen(self.parentItem().unselectedPen)
        painter.setBrush(self.brush)

        painter.drawPolygon([QPoint(self.itemWidth - 1, self.itemHeight - 1),
                             QPoint(self.itemWidth - 1, 0),
                             QPoint(0, self.itemHeight - 1)],
                            QtCore.Qt.OddEvenFill)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.itemWidth, self.itemHeight)

    def itemChange(self, change, value):
        """
        Called whenever a change happens to the instance of this class like move, click, resize ect.
        In this case used to resize the parent node and to limit the position to the minimal size constraints
        of a node.
        :param change: defines a type of a change
        :param value: defines a value of a change
        :return: QVariant
        """
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            parentMinWidth = self.parentItem().properties['minimalWidth'] - self.itemWidth
            parentMinHeight = self.parentItem().properties['minimalHeight'] - self.itemHeight

            if value.x() < parentMinWidth:
                value.setX(parentMinWidth)
                self.setX(parentMinWidth)

            if value.y() < parentMinHeight:
                value.setY(parentMinHeight)
                self.setY(parentMinHeight)
            self.parentItem().setSize(self.pos() + self.sizePoint)

        return QtGui.QGraphicsItem.itemChange(self, change, value)


class GungItem(QtGui.QGraphicsItem):
    elementType = "GungNode"

    """
    Base class for all GUNG scene items. Inside the constructor it will try to obtain the unique id for this item
    that will be used later in every important operation (especially during the connection of the plugs, undo/redo,
    save/load). The utility items like resizer are not considered as a GUNG items.
    """

    def __init__(self, parent=None, scene=None, nodeId=None):
        QtGui.QGraphicsItem.__init__(self, parent, scene)
        self.id_ = None

        self.properties = dict()

        self.properties['posX'] = 0.0
        self.properties['posY'] = 0.0

        if nodeId is None:
            nodeId = self.scene().getNewId()

        self.properties["nodeId"] = nodeId

    def asXml(self, document):
        """
        Returns this item and all its sub items as an xml element.
        """
        element = document.createElement(self.elementType)

        self.properties["posX"] = self.pos().x()
        self.properties["posY"] = self.pos().y()

        for p in self.properties.keys():
            element.setAttribute(p, str(self.properties[p]))

        for item in self.childItems():
            if not isinstance(item, GungItem):
                continue
            item_element = item.asXml(document)
            element.appendChild(item_element)

        return element

    def fromXml(self, xmlnode):
        for k in xmlnode.attributes.keys():
            if not k in self.properties.keys():
                continue
            self.properties[k] = type(self.properties[k])(xmlnode.attributes[k].value)

        self.setX(self.properties['posX'])
        self.setY(self.properties['posY'])

        classes = getGungNodeClasses()
        for node in xmlnode.childNodes:
            if not node.nodeType == Node.ELEMENT_NODE:
                continue
            if not node.tagName in classes.keys():
                continue
            gn = classes[node.tagName](parent=self, scene=self.scene())
            gn.fromXml(node)


class GungNode(GungItem):
    elementType = "GungNode"
    resizerClass = GungNodeResizer
    """
    Base class of the graphical node. Inherit this to get some specific look of your nodes.
    """

    def __init__(self, name="", parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.resizer = None

        self.properties['name'] = name
        self.properties['nodeWidth'] = config.getfloat("Node", "MinimalWidth")
        self.properties['nodeHeight'] = config.getfloat("Node", "MinimalHeight")
        self.properties['minimalWidth'] = config.getfloat("Node", "MinimalWidth")
        self.properties['minimalHeight'] = config.getfloat("Node", "MinimalHeight")

        self.bboxW = config.getfloat("Node", "MinimalWidth")
        self.bboxH = config.getfloat("Node", "MinimalHeight")

        # TODO: settings file implementation
        self.color = QtGui.QColor(76, 118, 150)
        self.lightGrayBrush = QtGui.QBrush(self.color)
        self.darkGrayBrush = QtGui.QBrush(QtCore.Qt.darkGray)

        self.selectedPen = QtGui.QPen(QtGui.QColor(255, 255, 255))
        self.unselectedPen = QtGui.QPen(QtGui.QColor(58, 57, 57))
        self.textPen = QtGui.QPen(QtGui.QColor(255, 255, 255))

        self.plugFont = QtGui.QFont("Arial", 7)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

        self.draggingNode = None

        self.createResizer()
        self.updateBBox()

    def requestMinimumWidth(self, minimumWidth):

        if minimumWidth < config.getfloat("Node", "MinimalWidth"):
            minimumWidth = config.getfloat("Node", "MinimalWidth")

        if self.properties['minimalWidth'] < minimumWidth:
            self.properties['minimalWidth'] = minimumWidth

        if self.properties['nodeWidth'] < minimumWidth:
            self.properties['nodeWidth'] = minimumWidth

        if self.resizer.pos().x() < minimumWidth:
            self.resizer.setX(minimumWidth)

    def createResizer(self):
        """
        Adds a special type of child item that will control the size of this node.
        This is a typical behaviour of a node systems, that allows you to resize the nodes with a small widget.
        """
        self.resizer = self.resizerClass(self, self.scene())
        self.resizer.setX(self.properties['nodeWidth'] - self.resizer.itemWidth)
        self.resizer.setY(self.properties['nodeHeight'] - self.resizer.itemHeight)

    def updateBBox(self):
        self.bboxW = self.properties['nodeWidth']
        self.bboxH = self.properties['nodeHeight']

    def rearrangeAttributes(self):
        currentheight = -1
        for childitem in self.childItems():
            if not isinstance(childitem, GungAttribute):
                continue

            childitem.setX(0)
            if currentheight == -1:
                currentheight = 20

            childitem.setX(0)
            childitem.setY(currentheight)
            currentheight += childitem.properties['attrHeight'] + 2

        if currentheight >= 35:
            self.properties['minimalHeight'] = currentheight + 20.0
        else:
            self.properties['minimalHeight'] = 35 + 20.0

        self.properties['nodeHeight'] = self.properties['minimalHeight']
        self.resizer.setY(self.properties['minimalHeight'] - self.resizer.itemHeight)

        for childitem in self.childItems():
            if not isinstance(childitem, GungAttribute):
                continue
            childitem.rearrangePlugs()

    def mousePressEvent(self, event):
        self.scene().topZ += .0001
        self.setZValue(self.scene().topZ)
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def fromXml(self, xmlnode):
        GungItem.fromXml(self, xmlnode)
        self.resizer.setX(self.properties['nodeWidth'] - self.resizer.itemWidth)
        self.resizer.setY(self.properties['nodeHeight'] - self.resizer.itemHeight)

    def setSize(self, size):
        """
        Sets an attributes in properties dict, updates bounding box and calls the rearrangement
        of all attributes. This is needed if you want to have plugs "sticked" to the right edge
        of this node.
        """
        self.properties['nodeWidth'] = size.x()
        self.properties['nodeHeight'] = size.y()
        self.update()

        self.prepareGeometryChange()
        self.updateBBox()

        self.rearrangeAttributes()

    def paint(self, painter, option, widget=None):
        """
        Override of QGraphicsItem.paint method. Implement this in your child classes to
        make nodes with the look you want.
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        #--- Distinguish the selected nodes from the unselected ones.
        if self.isSelected():
            painter.setPen(self.selectedPen)
        else:
            painter.setPen(self.unselectedPen)

        painter.setBrush(self.darkGrayBrush)
        painter.drawRect(0, 0, self.properties['nodeWidth'], self.properties['nodeHeight'])

        #--- Draw name of the node
        painter.setPen(self.textPen)
        painter.drawText(5, 15, self.properties['name'])

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.bboxW, self.bboxH)

    def itemChange(self, change, value):
        """
        Called whenever a change happens to the instance of this class like move, click, resize ect.
        In this case used to register position changes of the nodes, so that they can be reverted using the
        undo queue.
        :param change: defines a type of a change
        :param value: defines a value of a change
        :return: QVariant
        """
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            #--- inform the scene that this item has moved.
            self.scene().nodesHaveMoved = True

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def getAllEdges(self):
        """
        Returns all edges connected to plugs for this node.
        """
        result = []
        for item in self.childItems():
            if not isinstance(item, GungAttribute):
                continue
            for subitem in item.childItems():
                if not isinstance(subitem, GungPlug):
                    continue
                result += subitem.edges
        return result

    def getAllPlugs(self):
        """
        Returns all plugs for this node.
        """
        result = []
        for item in self.childItems():
            if not isinstance(item, GungAttribute):
                continue
            for subitem in item.childItems():
                if not isinstance(subitem, GungPlug):
                    continue
                result.append(subitem)
        return result


class GungAttribute(GungItem):
    elementType = "GungAttribute"

    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent, scene)

        self.properties['attrHeight'] = config.getfloat("Attribute", "Height")

    def paint(self, painter, option, widget=None):
        painter.setPen(QtGui.QPen(QtGui.QColor(180, 210, 180)))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.drawRect(self.boundingRect())

    def rearrangePlugs(self):
        plugs = []
        for childitem in self.childItems():
            if not isinstance(childitem, GungPlug):
                continue
            plugs.append(childitem)

        if not len(plugs):
            return

        inplugs = []
        outplugs = []

        for p in plugs:
            if isinstance(p, GungOutPlug):
                outplugs.append(p)
                continue
            if isinstance(p, GungPlug):
                inplugs.append(p)

        index = 0
        totalWidth = 0
        for p in inplugs:
            w = index * p.properties['plugWidth']
            p.setX(w)
            p.setY(0)
            totalWidth += p.properties['plugWidth']
            index += 1

        parentBounding = self.parentItem().boundingRect()
        index = 1
        for p in outplugs:
            w = (index * p.properties['plugWidth']) + 1
            p.setX(parentBounding.width() - w)
            p.setY(0)
            totalWidth += p.properties['plugWidth']
            index += 1

        if isinstance(self.parentItem(), GungNode):
            self.parentItem().requestMinimumWidth(totalWidth)

    def boundingRect(self):
        """
        Override this in child classes.
        """

        return QtCore.QRectF(0, 0, self.parentItem().properties['nodeWidth'], self.properties['attrHeight'])


class GungPlug(GungItem):
    elementType = "GungPlug"
    acceptsConnections = "GungOutPlug"

    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.properties['plugWidth'] = 14.0
        self.properties['plugHeight'] = 14.0

        self.isHighlighted = False

        plugColor = QtGui.QColor(150, 255, 150)

        self.plugPen = QtGui.QPen(plugColor.lighter())
        self.plugBrush = QtGui.QBrush(plugColor)
        self.highlightedPlugBrush = QtGui.QBrush(plugColor.lighter())

        self.edges = []

        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)

    def acceptsDrop(self, plugOut):
        result = False
        if plugOut.elementType in self.acceptsConnections.split(","):
            result = True
        return result

    def mousePressEvent(self, event):
        event.accept()
        self.scene().initDraggingEdge(self.mapToScene(self.boundingRect().center()), self)

    def mouseMoveEvent(self, event):
        return GungItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.scene().draggingEnded(self.mapToScene(event.pos()))
        return GungItem.mouseReleaseEvent(self, event)

    def paint(self, painter, option, widget=None):
        """
        Override this method to give your plugs a custom look.
        """
        painter.setPen(self.plugPen)

        if self.isHighlighted:
            painter.setBrush(self.highlightedPlugBrush)
        else:
            painter.setBrush(self.plugBrush)
        painter.drawRect(0, 0, self.properties['plugWidth'], self.properties['plugHeight'])

    def setHighlighted(self, state):
        self.isHighlighted = state
        self.update()

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.properties['plugWidth'], self.properties['plugHeight'])

    def itemChange(self, change, value):
        """
        Called whenever a change happens to the instance of this class like move, click, resize ect.
        In this case used to resize the parent node and to limit the position to the minimal size constraints
        of a node.
        :param change: defines a type of a change
        :param value: defines a value of a change
        :return: QVariant
        """

        if change == QtGui.QGraphicsItem.ItemScenePositionHasChanged:
            for edge in self.edges:
                if edge is None:
                    continue
                if edge.itemTo is self:
                    edge.prepareGeometryChange()
                    edge.setToPos(self.mapToScene(self.boundingRect().center()))
                if edge.itemFrom is self:
                    edge.prepareGeometryChange()
                    edge.setFromPos(self.mapToScene(self.boundingRect().center()))

        return QtGui.QGraphicsItem.itemChange(self, change, value)


class GungOutPlug(GungPlug):
    elementType = "GungOutPlug"
    acceptsConnections = "GungPlug"

    def __init__(self, parent=None, scene=None):
        GungPlug.__init__(self, parent=parent, scene=scene)


class GungEdge(GungItem):
    def __init__(self, itemFromId, itemToId, parent=None, scene=None):
        GungItem.__init__(self, None, scene)

        self.properties['itemFromId'] = itemFromId
        self.properties['itemToId'] = itemToId

        self.itemFrom = None
        self.itemTo = None

        itemfrom = self.scene().getItemById(int(itemFromId))
        itemto = self.scene().getItemById(int(itemToId))

        self.fromPos = itemfrom.mapToScene(itemfrom.boundingRect().center())
        self.toPos = itemto.mapToScene(itemto.boundingRect().center())

        self.edgePen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.setZValue(self.scene().topEdgeZ)
        self.scene().topEdgeZ += .0001

        self.brect = QtCore.QRectF()

    def reconnectEdge(self):
        if not self.properties['itemFromId'] == -1 and not self.properties['itemFromId'] == self.properties['nodeId']:
            self.itemFrom = self.scene().getItemById(int(self.properties['itemFromId']))
            if not self.itemFrom is None:
                self.itemFrom.edges.append(self)
                self.setFromPos(self.itemFrom.mapToScene(self.itemFrom.boundingRect().center()))
        if not self.properties['itemToId'] == -1 and not self.properties['itemToId'] == self.properties['nodeId']:
            self.itemTo = self.scene().getItemById(int(self.properties['itemToId']))
            if not self.itemTo is None:
                self.itemTo.edges.append(self)
                self.setToPos(self.itemTo.mapToScene(self.itemTo.boundingRect().center()))
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)

    def disconnectEdge(self):
        # TODO: Make it more loose coupled. Now it's a field for errors.
        while self in self.itemFrom.edges:
            self.itemFrom.edges.remove(self)
        while self in self.itemTo.edges:
            self.itemTo.edges.remove(self)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, True)

    def paint(self, painter, option, widget=None):
        if self.itemFrom is None or self.itemTo is None:
            return
        painter.setPen(self.edgePen)
        posStart = self.itemFrom.mapToScene(QtCore.QPointF()) + self.itemFrom.boundingRect().center()
        posEnd = self.itemTo.mapToScene(QtCore.QPointF()) + self.itemTo.boundingRect().center()

        painter.drawLine(posStart, posEnd)

    def setFromPos(self, pointFrom):
        self.fromPos = QtCore.QPointF(pointFrom)

        topleftX = min(float(self.fromPos.x()), float(self.toPos.x()))
        topleftY = min(float(self.fromPos.y()), float(self.toPos.y()))

        bottomrightX = max(float(self.fromPos.x()), float(self.toPos.x()))
        bottomrightY = max(float(self.fromPos.y()), float(self.toPos.y()))
        self.brect = QtCore.QRectF(topleftX, topleftY, bottomrightX - topleftX, bottomrightY - topleftY)

    def setToPos(self, pointTo):
        self.toPos = QtCore.QPointF(pointTo)

        topleftX = min(float(self.fromPos.x()), float(self.toPos.x()))
        topleftY = min(float(self.fromPos.y()), float(self.toPos.y()))

        bottomrightX = max(float(self.fromPos.x()), float(self.toPos.x()))
        bottomrightY = max(float(self.fromPos.y()), float(self.toPos.y()))
        self.brect = QtCore.QRectF(topleftX, topleftY, bottomrightX - topleftX, bottomrightY - topleftY)

    def boundingRect(self, *args, **kwargs):
        return self.brect

