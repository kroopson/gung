from PySide import QtGui, QtCore
from PySide.QtCore import Slot, QMimeData, Signal
from PySide.QtGui import QDrag
from gungnode import GungNode, GungItem
from gungscene import GungScene
QString = str
versionString = "GUNG v.0.0.5"


class GungGraphicsView(QtGui.QGraphicsView):
    undoSignal = Signal()
    redoSignal = Signal()
    deleteSignal = Signal()
    groupSignal = Signal()

    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.previousMousePosition = None
        self.setSceneRect(-64000, -64000, 128000, 128000)
        self.centerOn(0, 0)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.currentScale = 1
        self.baseSize = None

        self.textPen = QtGui.QPen(QtGui.QColor(128, 128, 128))
        self.textBrush = QtGui.QBrush(QtGui.QColor(128, 128, 128))
        self.font = QtGui.QFont("Impact", 18)
        self.namefont = QtGui.QFont("Impact", 8)

        self.zoomStart = QtCore.QPoint()
        self.zoomStartTransform = QtGui.QTransform()
        
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.previousMousePosition = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            self.zoomStart = event.pos()
            self.zoomStartTransform = self.transform()
        else:
            return QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MidButton:
            if self.previousMousePosition:
                currentMousePosition = event.globalPos()
                x = (currentMousePosition - self.previousMousePosition).x()
                y = (currentMousePosition - self.previousMousePosition).y()
                self.translate(x / self.currentScale, y / self.currentScale)
            self.previousMousePosition = event.globalPos()
        elif event.buttons() == QtCore.Qt.RightButton:
            if event.pos().x() > self.zoomStart.x():
                scaleValue = 1 + abs((event.x() - self.zoomStart.x()) / 100.0)
                self.zoom(scaleValue)
            elif event.pos().x() < self.zoomStart.x():
                scaleValue = 1.0 / (1 + (abs((event.x() - self.zoomStart.x())) / 100.0))
                self.zoom(scaleValue)
        else:
            return QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def zoom(self, scaleValue):
        if scaleValue <= 0.1:
            scaleValue = .01
        
        currentTransform = self.zoomStartTransform
        self.setTransform(currentTransform)
        scenePos = self.mapToScene(self.zoomStart)

        scaleMatrix = QtGui.QTransform.fromScale(scaleValue, scaleValue)
        scaledTransform = scaleMatrix * currentTransform
        self.setTransform(scaledTransform)

        newMap = self.mapToScene(self.zoomStart)
        translateVal = [newMap.x() - scenePos.x(), newMap.y() - scenePos.y()]

        scaledTransform.translate(translateVal[0], translateVal[1])
        self.setTransform(scaledTransform)
        self.getCurrentScale()
        

    def getCurrentScale(self):
        matrix = self.transform()
        mapPointZero = QtCore.QPointF(0.0, 0.0)
        mapPointOne = QtCore.QPointF(1.0, 0.0)

        mappedPointZero = matrix.map(mapPointZero)
        mappedPointOne = matrix.map(mapPointOne)
        self.currentScale = mappedPointOne.x() - mappedPointZero.x()

    def wheelEvent(self, event):
        delta = event.delta()
        self.zoomStartTransform = self.transform()

        self.zoomStart = event.pos()
        if delta < 0:
            scaleValue = .9
        else:
            scaleValue = 1.1

        self.zoom(scaleValue)

    def resizeEvent(self, event):
        currentSize = self.size()

        if self.baseSize is None:
            self.setBaseSize()
        if self.baseSize is not 0 and self.baseSize is not None:
            scaleValue = float(currentSize.width()) / float(self.baseSize.width())
            self.baseSize = self.size()
            self.scale(scaleValue, scaleValue)

        self.getCurrentScale()
        return QtGui.QGraphicsView.resizeEvent(self, event)

    def setBaseSize(self):
        self.baseSize = self.size()

    def zoomToSelected(self):
        scenka = self.scene()
        selItems = scenka.selectedItems()
        if len(selItems) > 0:
            zoomRect = QtCore.QRectF()
            for item in selItems:
                if not isinstance(item, GungNode):
                    continue
                itemrect = item.boundingRect()
                zoomRect = zoomRect.united(itemrect.translated(item.x(), item.y()))

            self.fitInView(zoomRect, QtCore.Qt.KeepAspectRatio)
            self.getCurrentScale()

    def zoomToAll(self):
        allnodes = self.getnodes()
        if len(allnodes) > 0:
            zoomRect = allnodes[0].boundingRect().translated(allnodes[0].x(), allnodes[0].y())
            for item in allnodes[1:]:
                itemrect = item.boundingRect()
                zoomRect = zoomRect.united(itemrect.translated(item.x(), item.y()))
            self.fitInView(zoomRect, QtCore.Qt.KeepAspectRatio)
            self.getCurrentScale()
        else:
            self.setTransform(QtGui.QTransform())

    def getnodes(self):
        scenka = self.scene()
        sceneItems = scenka.items()
        nodes = []
        for item in sceneItems:
            if not isinstance(item, GungItem):
                continue
            nodes.append(item)
        return nodes

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.zoomToSelected()
            event.accept()

        if event.key() == QtCore.Qt.Key_A:
            self.zoomToAll()
            event.accept()

        if event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ControlModifier:
            self.undoSignal.emit()

        if event.key() == QtCore.Qt.Key_Y and event.modifiers() == QtCore.Qt.ControlModifier:
            self.redoSignal.emit()
            
        if event.key() == QtCore.Qt.Key_Delete:
            self.deleteSignal.emit()

        if event.key() == QtCore.Qt.Key_G and event.modifiers() == QtCore.Qt.ControlModifier:
            self.groupSignal.emit()

        return QtGui.QGraphicsView.keyPressEvent(self, event)

    def drawBackground(self, painter, rect):
        painter.setFont(self.font)
        painter.setPen(self.textPen)
        painter.setBrush(self.textBrush)
        painter.setWorldMatrixEnabled(False)

        image = QtGui.QImage()

        w = image.size().width()
        h = image.size().height()
        r = QtCore.QRect(1, self.height() - h - 5, w, h)
        painter.drawImage(r, image)

        painter.drawText(w + 2, self.height() - 6, QString(versionString))

        return QtGui.QGraphicsView.drawBackground(self, painter, rect)

    def setScene(self, scene):
        if isinstance(scene, GungScene):
            #scene.draggingStarted.connect(self.startDragging)
            self.undoSignal.connect(scene.undoCalled)
            self.redoSignal.connect(scene.redoCalled)
            self.deleteSignal.connect(scene.deleteCalled)
            self.groupSignal.connect(scene.createGroupCalled)
        return QtGui.QGraphicsView.setScene(self, scene)

    # @Slot(int)
    # def startDragging(self, itemid):
    #     drag = QDrag(self)
    #     data = QMimeData()
    #     data.setText(str(itemid))
    #     drag.setMimeData(data)
    #     drag.exec_()

