import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from PySide.QtCore import QPoint, QPointF


class GungItem(QtGui.QGraphicsItem):
    """
    Base class for all major GUNG scene items. Inside the constructor it will try to obtain the unique id for this item
    that will be used later on in every important operation (especially during the connection of the plugs etc.
    """
    def __init__(self, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent, scene)
        self.id_ = None

        self.id_ = self.scene().getNewId()


class GungNode(GungItem):
    """
    Base class of the graphical node. Inherit this to get some specific look of your nodes.
    """
    def __init__( self, name, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.resizer = None
        self.nodeWidth = 0
        self.nodeHeight = 0
        self.minimalHeight = 0

        # move this to some setting section
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

        self.setFlag( QtGui.QGraphicsItem.ItemIsMovable, True )
        self.setFlag( QtGui.QGraphicsItem.ItemIsSelectable, True )
        self.setFlag( QtGui.QGraphicsItem.ItemClipsToShape, True )
        self.setFlag( QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)

        self.name = name

        self.plugNodes = []

        self.draggingNode = None
        self.properties = []

        self.createResizer()
        self.updateBBox()

    def createResizer(self):
        """
        Adds a special type of child item that will control the size of this node.
        This is a typical behaviour of a node systems, that allows you to resize the nodes with a small widget.
        """
        self.resizer = GungNodeResizer(self, self.scene())
        self.resizer.setX(self.nodeWidth - self.resizer.itemWidth)
        self.resizer.setY(self.nodeHeight - self.resizer.itemHeight)

    def initSettings(self):
        self.nodeWidth = 100
        self.nodeHeight = 30

        self.minimalWidth = 100
        self.minimalHeight = 30

    def updateBBox(self):
        self.bboxW = self.nodeWidth
        self.bboxH = self.nodeHeight

    def rearrangePlugs(self):
        currentheight = -1
        for childitem in self.childItems():
            if not isinstance(childitem, GungPlug):
                continue

            childitem.setX(0)
            if currentheight == -1:
                currentheight = childitem.plugHeight

            currentheight += 3
            childitem.setX(1)
            childitem.setY(currentheight)
            currentheight += childitem.plugHeight

        if currentheight >= 35:
            self.minimalHeight = currentheight + 20
        else:
            self.minimalHeight = 35 + 20

        self.nodeHeight = self.minimalHeight
        self.resizer.setY(self.minimalHeight - self.resizer.itemHeight)

    def mousePressEvent(self, event):
        self.scene().topZ += .001
        self.setZValue(self.scene().topZ)
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        # if event.pos().y() < 20:
        #    self.scene().emit( QtCore.SIGNAL( "elementRename()" ) )
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def getSize( self ):
        sizeX = self.nodeWidth

        plugsCount = len(self.outplugs)
        if len(self.inplugs) > len(self.outplugs):
            plugsCount = len(self.inplugs)

        sizeY = self.plugsHeightStart + (self.plugSize * plugsCount)

        for prop in self.properties:
            sizeY += prop.getSizeY()

        return QtCore.QRectF(0, 0, sizeX, sizeY)

    def setSize(self, size):
        growing = False
        if size.x() >= self.nodeWidth or size.y() >= self.nodeHeight:
            growing = True

        self.nodeWidth = size.x()
        self.nodeHeight = size.y()
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
        painter.drawRect(0, 0, self.nodeWidth - 1, self.nodeHeight - 1)

        # draw name of an element
        painter.setPen(self.textPen)
        painter.drawText(5, 15, self.name)

    def boundingRect(self):
        return QtCore.QRectF(-1, -1, self.bboxW + 1, self.bboxH + 1)


class GungAttribute(GungItem):
    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent, scene)

        # This list is supposed to hold the plugs for those attributes
        self.plugs = []

        self.attrHeight = 15

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.parentItem().nodeWidth, self.parentItem().attrHeight)

class GungPlug(GungItem):
    def __init__( self, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.plugWidth = 15
        self.plugHeight = 15

        self.plugPen = QtGui.QPen(QtGui.QColor(200,200,200))
        self.plugPen.setWidth(2)
        self.plugBrush = QtGui.QBrush(QtGui.QColor(200,200,200))

    def paint(self, painter, option, widget=None):
        """
        Override this method to give your plugs a custom look.
        """
        painter.setRenderHint( QtGui.QPainter.Antialiasing )

        painter.setPen( self.plugPen )

        painter.setBrush( self.plugBrush )
        painter.drawRect( 1, 1, self.plugWidth - 1 , self.plugHeight - 1 )

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF( -1,-1, self.plugWidth + 1, self.plugHeight + 1 )


class GungNodeResizer(QtGui.QGraphicsItem):
    def __init__( self, parent=None, scene=None):
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
            parentMinWidth = self.parentItem().minimalWidth - self.itemWidth
            parentMinHeight = self.parentItem().minimalHeight - self.itemHeight

            if value.x() < parentMinWidth:
                value.setX(parentMinWidth)
                self.setX(parentMinWidth)

            if value.y() < parentMinHeight:
                value.setY(parentMinHeight)
                self.setY(parentMinHeight)

            self.parentItem().setSize(self.pos() + self.sizePoint)

        return QtGui.QGraphicsItem.itemChange(self, change, value)
