import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from PySide.QtCore import QPoint, QPointF

#from natal.view.NatalPlug import NatalPlug
#from natal.view.NatalNodeProperty import NatalNodeProperty
#from natal.model.settings import Settings


class GungNode( QtGui.QGraphicsItem ):
    def __init__( self, name, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene )

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
        self.resizer = GungNodeResizer(self, self.scene())
        self.resizer.setX(self.nodeWidth - self.resizer.itemWidth)
        self.resizer.setY(self.nodeHeight  - self.resizer.itemHeight)

    def initSettings( self ):
        self.nodeWidth = 100
        self.nodeHeight = 30
        
        self.minimalWidth = 100
        self.minimalHeight = 30
        
    def updateBBox(self):
        self.bboxW = self.nodeWidth
        self.bboxH = self.nodeHeight

        # move this to some setting section
        self.color = QtGui.QColor(76, 118, 150)
        self.lightGrayBrush = QtGui.QBrush( self.color )
        self.darkGrayBrush = QtGui.QBrush( QtCore.Qt.darkGray )

        self.selectedPen = QtGui.QPen( QtGui.QColor(255, 255, 255) )
        self.selectedPen.setWidth(2)
        self.unselectedPen = QtGui.QPen( QtGui.QColor(58, 57, 57) )
        self.unselectedPen.setWidth(2)
        self.textPen = QtGui.QPen( QtGui.QColor(255, 255, 255) )

        self.plugFont = QtGui.QFont( "Arial", 7 )
        
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

    def mousePressEvent( self, event ):
        self.scene().topZ += .001
        self.setZValue( self.scene().topZ )
        return QtGui.QGraphicsItem.mousePressEvent(self, event )

    def mouseDoubleClickEvent( self, event ):
        #if event.pos().y() < 20:
        #    self.scene().emit( QtCore.SIGNAL( "elementRename()" ) )
        return QtGui.QGraphicsItem.mousePressEvent(self, event )

    def setName( self, newname ):
        self.name = newname
        self.namespace = newname.split( ":" )[0]
        for plug in self.inplugs + self.outplugs:
            plug.rename( self.namespace )
        self.update()

    def setNamespace( self, newns ):
        self.namespace = newns

    def getSize( self ):
        sizeX = self.nodeWidth

        plugsCount = len( self.outplugs )
        if len( self.inplugs ) > len( self.outplugs ):
            plugsCount = len( self.inplugs )

        sizeY = self.plugsHeightStart + ( self.plugSize * plugsCount )

        for prop in self.properties:
            sizeY += prop.getSizeY()

        return QtCore.QRectF( 0, 0, sizeX, sizeY )
    
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

    def paint( self, painter, option, widget=None ):
        painter.setRenderHint( QtGui.QPainter.Antialiasing )

        # draw body of a node
        if self.isSelected():
            painter.setPen( self.selectedPen )
        else:
            painter.setPen( self.unselectedPen )

        painter.setBrush( self.darkGrayBrush )
        painter.drawRect( 0, 0, self.nodeWidth - 1 , self.nodeHeight - 1 )

        # draw name of an element
        painter.setPen( self.textPen )
        painter.drawText( 5, 15, self.name )

    def boundingRect( self ):
        return QtCore.QRectF( -1, -1, self.bboxW + 1, self.bboxH + 1 )


class GungPlug( QtGui.QGraphicsItem ):
    def __init__( self, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene )
        
        self.plugWidth = 15
        self.plugHeight = 15
        
        self.plugPen = QtGui.QPen(QtGui.QColor(200,200,200))
        self.plugPen.setWidth(2)
        self.plugBrush = QtGui.QBrush(QtGui.QColor(200,200,200))
        
    def paint( self, painter, option, widget=None ):
        painter.setRenderHint( QtGui.QPainter.Antialiasing )

        painter.setPen( self.plugPen )
    
        painter.setBrush( self.plugBrush )
        painter.drawRect( 1, 1, self.plugWidth - 1 , self.plugHeight - 1 )
    
    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF( -1,-1, self.plugWidth + 1, self.plugHeight + 1 )


class GungNodeResizer( QtGui.QGraphicsItem ):
    def __init__( self, parent=None, scene=None):
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene )
        self.setFlag( QtGui.QGraphicsItem.ItemIsMovable )
        self.setFlag( QtGui.QGraphicsItem.ItemSendsScenePositionChanges )
        self.setFlag( QtGui.QGraphicsItem.ItemIsSelectable )
        
        self.itemWidth = 10
        self.itemHeight = 10
        
        self.sizePoint = QPoint(self.itemWidth, self.itemHeight)
        
        self.pen = QtGui.QPen(QtGui.QColor(0,0,0))
        self.brush = QtGui.QBrush(QtGui.QColor(50,50,50))
    
    def paint( self, painter, option, widget=None ):
        painter.setRenderHint( QtGui.QPainter.Antialiasing )
        painter.setPen( self.pen )
        painter.setBrush( self.brush )
        
        painter.drawPolygon([QPoint(self.itemWidth - 1,self.itemHeight - 1),
                             QPoint(self.itemWidth-1, 0),
                             QPoint(0, self.itemHeight-1)],
                            QtCore.Qt.OddEvenFill)
        
    def boundingRect( self ):
        return QtCore.QRectF(  0,0, self.itemWidth, self.itemHeight )
    
    def itemChange(self, change, value):
        
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

