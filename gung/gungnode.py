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
        
        self.inplugs = []
        self.outplugs = []

        self.draggingNode = None
        self.properties = []
        
        self.createResizer()
        self.updateBBox()
        
    def createResizer(self):
        self.resizer = GungNodeResizer(self, self.scene())
        self.resizer.setX(self.nodeWidth - self.resizer.itemWidth)
        self.resizer.setY(self.nodeHeight  - self.resizer.itemHeight)

    def initSettings( self ):
        self.nodeWidth = 200
        self.nodeHeight = 150
        
        self.minimalWidth = 200
        self.minimalHeight = 150
        
    def updateBBox(self):
        self.bboxW = self.nodeWidth
        self.bboxH = self.nodeHeight
#         self.nodeWidth = Settings().nodeWidth
#         self.nodeHeight = Settings().nodeHeight
#         self.plugSize = Settings().plugSize
        
        #self.plugSize = Settings().plugSize

        #self.leftBorder = 0
        #self.rightBorder = self.nodeWidth - self.plugSize

        #self.plugsHeightStart = Settings().plugsHeightStart

        #self.nodeMargin = 2

        # move this to some setting section
        self.color = QtGui.QColor(76, 118, 150)
        self.lightGrayBrush = QtGui.QBrush( self.color )
        self.darkGrayBrush = QtGui.QBrush( QtCore.Qt.darkGray )
        #self.plugsBrush = QtGui.QBrush( Settings().nodePlugsColor )

        self.selectedPen = QtGui.QPen( QtGui.QColor(255, 255, 255) )
        self.unselectedPen = QtGui.QPen( QtGui.QColor(58, 57, 57) )
        self.textPen = QtGui.QPen( QtGui.QColor(255, 255, 255) )

        self.plugFont = QtGui.QFont( "Arial", 7 )

    def addInPlug( self, name ):
        pass
#         if name.endswith( "_SNAP" ):
#             plugInColor = QtGui.QColor( 84, 244, 238 )
#         else:
#             plugInColor = QtGui.QColor( 238, 244, 84 )
# 
#         self.inplugs.append( NatalPlug( name, self, dir="in", plugInColor=plugInColor ) )
#         self.updatePlugs()

    def addOutPlug( self, name ):
        pass
#         if name.endswith( "_snapPoint" ):
#             plugOutColor = QtGui.QColor( 74, 250, 150 )
#         else:
#             plugOutColor = QtGui.QColor( 150, 250, 74 )
# 
#         self.outplugs.append( NatalPlug( name, self, dir="out", plugOutColor=plugOutColor ) )
#         self.updatePlugs()

#     def getPlugByName( self, name ):
#         result = None
#         for plugCollection in [self.inplugs, self.outplugs]:
#             for plug in plugCollection:
#                 if plug.name == name:
#                     result = plug
#         return result

    def mousePressEvent( self, event ):
        self.scene().topZ += .001
        self.setZValue( self.scene().topZ )
        return QtGui.QGraphicsItem.mousePressEvent(self, event )

    def mouseDoubleClickEvent( self, event ):
        #if event.pos().y() < 20:
        #    self.scene().emit( QtCore.SIGNAL( "elementRename()" ) )
        return QtGui.QGraphicsItem.mousePressEvent(self, event )

    def updatePlugs( self ):
        plug = None
        inout = 0

        # place the plugs on right and left
        for plugCollection in [self.inplugs, self.outplugs]:
            indx = 0

#            for plug in sorted( plugCollection, key=lambda sorted: str( sorted.name ) ):
            for plug in plugCollection:
                plug.setX( inout * self.rightBorder )
                plug.setY( self.plugsHeightStart + ( ( self.plugSize * 2 ) * indx ) )
                indx += 1
            inout += 1

            # Set height of node
            plugsHeight = self.plugsHeightStart + ( len( plugCollection ) * ( self.plugSize * 2 ) )
            if self.nodeHeight < plugsHeight:
                self.nodeHeight = plugsHeight

        #repaint node
        self.update()

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
        painter.drawRoundedRect( 0, 0, self.nodeWidth, self.nodeHeight, 5, 5 )

        # draw name of an element
        #painter.setBrush( self.plugsBrush )
        painter.setPen( self.textPen )
        painter.drawText( 5, 15, self.name )

        # draw inplugs and outplugs labels
#         painter.setFont( self.plugFont )
#         for inPlug in self.inplugs:
#             painter.drawText( int( self.plugSize + self.nodeMargin ),
#                               int( inPlug.y() - self.nodeMargin ),
#                               int( self.nodeWidth / 2 ),
#                               int( inPlug.y() + self.plugSize ),
#                               QtCore.Qt.AlignLeft,
#                               inPlug.getNameWithoutNamespace() )
# 
#         for outPlug in self.outplugs:
#             painter.drawText( int( self.nodeWidth / 2 ),
#                               int( outPlug.y() - self.nodeMargin ),
#                               int( ( self.nodeWidth / 2 ) - self.plugSize - self.nodeMargin ),
#                               int( outPlug.y() + self.plugSize ),
#                               QtCore.Qt.AlignRight,
#                               outPlug.getNameWithoutNamespace() )

    def rename( self, newName, namespace ):
        self.setName( str( newName ) )
        self.setNamespace( namespace )
        for p in self.inplugs + self.outplugs:
            p.rename( namespace )

    def remove( self ):
        for plug in self.inplugs:
            plug.remove()
            self.scene().removeItem( plug )

        for plug in self.outplugs:
            plug.remove()
            self.scene().removeItem( plug )

        self.inplugs = []
        self.outplugs = []

    def boundingRect( self ):
        return QtCore.QRectF( -1, -1, self.bboxW + 1, self.bboxH + 1 )


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

