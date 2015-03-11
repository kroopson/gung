import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from PySide.QtCore import QPoint


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
        
        self.properties = {}
        
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


class GungNode(GungItem):
    elementType = "GungNode"
    """
    Base class of the graphical node. Inherit this to get some specific look of your nodes.
    """
    def __init__(self, name, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.resizer = None

        self.properties['nodeWidth'] = 0.0
        self.properties['nodeHeight'] = 0.0
        self.properties['minimalWidth'] = 0.0
        self.properties['minimalHeight'] = 0.0

        # TODO: settings file implementation
        self.color = QtGui.QColor(76, 118, 150)
        self.lightGrayBrush = QtGui.QBrush(self.color)
        self.darkGrayBrush = QtGui.QBrush(QtCore.Qt.darkGray)

        self.selectedPen = QtGui.QPen(QtGui.QColor(255, 255, 255))
        self.selectedPen.setWidth(2)
        self.unselectedPen = QtGui.QPen(QtGui.QColor(58, 57, 57))
        self.unselectedPen.setWidth(2)
        self.textPen = QtGui.QPen(QtGui.QColor(255, 255, 255))

        self.plugFont = QtGui.QFont("Arial", 7)

        # Initialize settings
        self.initSettings()

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

        self.name = name

        self.plugNodes = []

        self.draggingNode = None

        self.createResizer()
        self.updateBBox()

    def requestMinimumWidth(self, minimumWidth):
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
        self.resizer = GungNodeResizer(self, self.scene())
        self.resizer.setX(self.properties['nodeWidth'] - self.resizer.itemWidth)
        self.resizer.setY(self.properties['nodeHeight'] - self.resizer.itemHeight)

    def initSettings(self):
        # TODO: make this loaded from config
        self.properties['nodeWidth'] = 100
        self.properties['nodeHeight'] = 30

        self.properties['minimalWidth'] = 0.0
        self.properties['minimalHeight'] = 0.0

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

            childitem.setX(1)
            childitem.setY(currentheight)
            currentheight += childitem.properties['attrHeight'] + 2

        if currentheight >= 35:
            self.properties['minimalHeight'] = currentheight + 20
        else:
            self.properties['minimalHeight'] = 35 + 20

        self.properties['nodeHeight'] = self.properties['minimalHeight']
        self.resizer.setY(self.properties['minimalHeight'] - self.resizer.itemHeight)

    def mousePressEvent(self, event):
        self.scene().topZ += .001
        self.setZValue(self.scene().topZ)
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def setSize(self, size):
        growing = False
        if size.x() >= self.properties['nodeWidth'] or size.y() >= self.properties['nodeHeight']:
            growing = True

        self.properties['nodeWidth'] = size.x()
        self.properties['nodeHeight'] = size.y()
        self.update()

        self.updateBBox()
        if growing:
            self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # draw body of a node
        if self.isSelected():
            painter.setPen(self.selectedPen)
        else:
            painter.setPen(self.unselectedPen)

        painter.setBrush(self.darkGrayBrush)
        painter.drawRect(0, 0, self.properties['nodeWidth'] - 1, self.properties['nodeHeight'] - 1)

        # draw name of an element
        painter.setPen(self.textPen)
        painter.drawText(5, 15, self.name)

    def boundingRect(self):
        return QtCore.QRectF(-1, -1, self.bboxW + 1, self.bboxH + 1)


class GungAttribute(GungItem):
    elementType = "GungAttribute"
    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent, scene)

        self.properties['attrHeight'] = 15

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

        index = 0
        totalWidth = 0
        for p in plugs:
            w = index * p.properties['plugWidth']
            p.setX(w)
            p.setY(0)
            totalWidth += p.properties['plugWidth']
            index += 1

        if isinstance(self.parentItem(), GungNode):
            self.parentItem().requestMinimumWidth(totalWidth)

    def boundingRect(self):
        """
        Override this in child classes.
        """

        return QtCore.QRectF(0, 0, self.parentItem().properties['nodeWidth'] - 4, self.properties['attrHeight'])


class GungPlug(GungItem):
    elementType = "GungPlug"
    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.properties['plugWidth'] = 14
        self.properties['plugHeight'] = 14

        plugColor = QtGui.QColor(150, 255, 150)

        self.plugPen = QtGui.QPen(plugColor.lighter())

        self.plugBrush = QtGui.QBrush(plugColor)

    def paint(self, painter, option, widget=None):
        """
        Override this method to give your plugs a custom look.
        """
        painter.setPen(self.plugPen)

        painter.setBrush(self.plugBrush)
        painter.drawRect(1, 1, self.properties['plugWidth'] - 1, self.properties['plugHeight'] - 1)

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(-1, -1, self.properties['plugWidth'] + 1, self.properties['plugHeight'] + 1)


class GungNodeResizer(QtGui.QGraphicsItem):
    def __init__(self, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

        self.itemWidth = 10
        self.itemHeight = 10

        self.sizePoint = QPoint(self.itemWidth, self.itemHeight)

        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))

    def paint(self, painter, option, widget=None):
        """
        Override of a paint class from QGraphicsItem.
        Implement this to give a resizer the desired look.
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self.pen)
        painter.setBrush(self.brush )

        painter.drawPolygon([QPoint(self.itemWidth - 1, self.itemHeight - 1),
                             QPoint(self.itemWidth-1, 0),
                             QPoint(0, self.itemHeight-1)],
                            QtCore.Qt.OddEvenFill)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.itemWidth, self.itemHeight )

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
            parentMinHeight = self.parentItem().properties['minimalWidth'] - self.itemHeight

            if value.x() < parentMinWidth:
                value.setX(parentMinWidth)
                self.setX(parentMinWidth)

            if value.y() < parentMinHeight:
                value.setY(parentMinHeight)
                self.setY(parentMinHeight)

            self.parentItem().setSize(self.pos() + self.sizePoint)

        return QtGui.QGraphicsItem.itemChange(self, change, value)
