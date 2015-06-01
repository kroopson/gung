from PySide import QtGui, QtCore
from PySide.QtCore import Signal
from gungnode import GungNode, GungItem
from gungscene import GungScene
QString = str
versionString = "GUNG v.0.0.6"


class GungGraphicsView(QtGui.QGraphicsView):
    undoSignal = Signal()
    redoSignal = Signal()
    deleteSignal = Signal()
    groupSignal = Signal()

    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.prev_mouse_pos = None
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
        self.zoom_start_transform = QtGui.QTransform()

        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.prev_mouse_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            self.zoomStart = event.pos()
            self.scene_zoom_start = self.mapToScene(event.pos())
            self.zoom_start_transform = self.transform()
        else:
            return QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MidButton:
            if self.prev_mouse_pos:
                current_mouse_pos = event.globalPos()
                x = (current_mouse_pos - self.prev_mouse_pos).x()
                y = (current_mouse_pos - self.prev_mouse_pos).y()
                self.translate(x / self.currentScale, y / self.currentScale)
            self.prev_mouse_pos = event.globalPos()
        elif event.buttons() == QtCore.Qt.RightButton:
            if event.pos().x() > self.zoomStart.x():
                scale_value = 1 + abs((event.x() - self.zoomStart.x()) / 100.0)
                self.zoom(scale_value)
            elif event.pos().x() < self.zoomStart.x():
                scale_value = 1.0 / (1 + (abs((event.x() - self.zoomStart.x())) / 100.0))
                self.zoom(scale_value)
        else:
            return QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def zoom(self, scale_value):
        if scale_value <= 0.1:
            scale_value = .01

        maxscale = 1.20

        current_transform = self.zoom_start_transform

        scene_pos = self.zoomStart

        zoom_start_scale = self.get_matrix_scale(self.zoom_start_transform)

        target_scale = scale_value * zoom_start_scale

        # if target_scale >= maxscale and scale_value > 1.0:
        #     scale_value = zoom_start_scale * maxscale
        #     print scale_value

        translate_matrix = QtGui.QTransform.fromTranslate(scene_pos.x(), scene_pos.y())
        inv_translate_matrix = translate_matrix.inverted()
        local_current_transform = current_transform * inv_translate_matrix[0]
        scale_matrix = QtGui.QTransform.fromScale(scale_value, scale_value)

        scaled_transform = local_current_transform * scale_matrix * translate_matrix

        # self.setTransform(scaled_transform)
        #
        # new_map = self.mapToScene(self.zoomStart)
        # translate_val = [new_map.x() - scene_pos.x(), new_map.y() - scene_pos.y()]
        #
        # scaled_transform.translate(translate_val[0], translate_val[1])
        self.setTransform(scaled_transform)
        self.get_current_scale()

    def get_current_scale(self):
        matrix = self.transform()
        map_point_zero = QtCore.QPointF(0.0, 0.0)
        map_point_one = QtCore.QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        self.currentScale = mapped_point_one.x() - mapped_point_zero.x()

    @staticmethod
    def get_matrix_scale(matrix):
        map_point_zero = QtCore.QPointF(0.0, 0.0)
        map_point_one = QtCore.QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        return (mapped_point_one - mapped_point_zero).manhattanLength()

    def wheelEvent(self, event):
        delta = event.delta()
        self.zoom_start_transform = self.transform()

        self.zoomStart = event.pos()
        if delta < 0:
            scale_value = .9
        else:
            scale_value = 1.1

        self.zoom(scale_value)

    def resizeEvent(self, event):
        current_size = self.size()

        if self.baseSize is None:
            self.setBaseSize()
        if self.baseSize is not 0 and self.baseSize is not None:
            scale_value = float(current_size.width()) / float(self.baseSize.width())
            self.baseSize = self.size()
            self.scale(scale_value, scale_value)

        self.get_current_scale()
        return QtGui.QGraphicsView.resizeEvent(self, event)

    def setBaseSize(self):
        self.baseSize = self.size()

    # def fitInView(self, rect, keep_aspect_ratio):
    #     self.setTransform(QtGui.QTransform())
    #     top_left_offset = self.mapToScene(0, 0)
    #     top_left_transform = QtGui.QTransform.fromTranslate(top_left_offset.x(), top_left_offset.y())
    #     current_window_size = self.size()
    #     position = rect.center()
    #
    #     view_mapped = self.mapFromScene(rect).boundingRect()
    #
    #     #scale_value = min(self.width() / float(rect.width()), 3.0)
    #     scale_value = self.width() / float(rect.width())
    #     # scale_value = 2.0
    #
    #     translated_center = QtCore.QPointF(current_window_size.width()/2.0, current_window_size.height()/2.0)
    #
    #     to_center_transform = QtGui.QTransform.fromTranslate(position.x(), position.y())
    #     to_screen_center_transform = QtGui.QTransform.fromTranslate(translated_center.x(), translated_center.y())
    #
    #     scale_matrix = QtGui.QTransform.fromScale(scale_value, scale_value)
    #
    #     centered_matrix = top_left_transform * to_center_transform.inverted()[0] * to_screen_center_transform
    #
    #     self.setTransform(centered_matrix)
    #     return

    def fitInView(self, rect, keep_aspect_ratio):
        self.setTransform(QtGui.QTransform())
        top_left_offset = self.mapToScene(0, 0)
        top_left_transform = QtGui.QTransform.fromTranslate(top_left_offset.x(), top_left_offset.y())
        current_window_size = self.size()
        position = rect.center()

        scale_value = min(self.width() / float(rect.width()), 3.0)

        scale_matrix = QtGui.QTransform.fromScale(scale_value, scale_value)
        scaled = scale_matrix * top_left_transform
        self.setTransform(scaled)

        translate = scaled.map(QtCore.QPoint(position.x(), position.y()))
        to_bound_center_matrix = QtGui.QTransform.fromTranslate(translate.x(), translate.y())
        translated_center = QtCore.QPointF(current_window_size.width()/2.0, current_window_size.height()/2.0)
        to_center_offset = translated_center + top_left_offset
        to_screen_center_transform = QtGui.QTransform.fromTranslate(to_center_offset.x(), to_center_offset.y())
        self.setTransform(scaled * to_bound_center_matrix.inverted()[0] * to_screen_center_transform)

        return

    def zoom_to_selected(self):
        scenka = self.scene()
        sel_items = scenka.selectedItems()
        if len(sel_items) > 0:
            zoom_rect = QtCore.QRectF()
            for item in sel_items:
                if not isinstance(item, GungNode):
                    continue
                itemrect = item.boundingRect()
                zoom_rect = zoom_rect.united(itemrect.translated(item.x(), item.y()))

            self.fitInView(zoom_rect, QtCore.Qt.KeepAspectRatio)
            self.get_current_scale()

    def zoom_to_all(self):
        allnodes = self.getnodes()
        if len(allnodes) > 0:
            zoom_rect = allnodes[0].boundingRect().translated(allnodes[0].x(), allnodes[0].y())
            for item in allnodes[1:]:
                itemrect = item.boundingRect()
                zoom_rect = zoom_rect.united(itemrect.translated(item.x(), item.y()))
            self.fitInView(zoom_rect, QtCore.Qt.KeepAspectRatio)
            self.get_current_scale()
        else:
            self.setTransform(QtGui.QTransform())

    def getnodes(self):
        scenka = self.scene()
        scene_items = scenka.items()
        nodes = []
        for item in scene_items:
            if not isinstance(item, GungItem):
                continue
            nodes.append(item)
        return nodes

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.zoom_to_selected()
            event.accept()

        if event.key() == QtCore.Qt.Key_A:
            self.zoom_to_all()
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
        painter.drawLine(0, 0, 100, 0)
        painter.drawLine(0, 0, 0, 100)
        painter.setWorldMatrixEnabled(False)

        image = QtGui.QImage()

        w = image.size().width()
        h = image.size().height()
        r = QtCore.QRect(1, self.height() - h - 5, w, h)
        painter.drawImage(r, image)

        painter.drawLine(self.width() / 2, 0, self.width()/2, self.height())
        painter.drawLine(0, self.height() / 2, self.width(),  self.height() / 2)

        painter.drawText(w + 2, self.height() - 6, QString(versionString))

        return QtGui.QGraphicsView.drawBackground(self, painter, rect)

    def setScene(self, scene):
        if isinstance(scene, GungScene):
            # scene.draggingStarted.connect(self.startDragging)
            self.undoSignal.connect(scene.undo_called)
            self.redoSignal.connect(scene.redo_called)
            self.deleteSignal.connect(scene.delete_called)
            self.groupSignal.connect(scene.create_group_called)
        return QtGui.QGraphicsView.setScene(self, scene)

        # @Slot(int)
        # def startDragging(self, itemid):
        #     drag = QDrag(self)
        #     data = QMimeData()
        #     data.setText(str(itemid))
        #     drag.setMimeData(data)
        #     drag.exec_()
