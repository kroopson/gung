from PySide import QtGui, QtCore
from PySide.QtCore import Signal
from gungnode import GungNode, GungItem
from gungscene import GungScene
QString = str
versionString = "GUNG v.0.1.1"


class GungGraphicsView(QtGui.QGraphicsView):
    undoSignal = Signal()
    redoSignal = Signal()
    deleteSignal = Signal()
    groupSignal = Signal()

    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.prev_mouse_pos = None
        self.setSceneRect(-64000, -64000, 128000, 128000)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.current_scale = 1
        self.max_zoom = 3.0
        self.base_size = None

        self.text_pen = QtGui.QPen(QtGui.QColor(128, 128, 128))
        self.text_brush = QtGui.QBrush(QtGui.QColor(128, 128, 128))
        self.font = QtGui.QFont("Impact", 18)
        self.name_font = QtGui.QFont("Impact", 8)

        self.zoom_start = QtCore.QPoint()
        self.zoom_start_transform = QtGui.QTransform()

        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.prev_mouse_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            self.zoom_start = event.pos()
            self.zoom_start_transform = self.transform()
        else:
            return QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MidButton:
            if self.prev_mouse_pos:
                current_mouse_pos = event.globalPos()
                x = (current_mouse_pos - self.prev_mouse_pos).x()
                y = (current_mouse_pos - self.prev_mouse_pos).y()
                self.translate(x / self.current_scale, y / self.current_scale)
            self.prev_mouse_pos = event.globalPos()
        elif event.buttons() == QtCore.Qt.RightButton:
            if event.pos().x() > self.zoom_start.x():
                scale_value = 1 + abs((event.x() - self.zoom_start.x()) / 100.0)
                self.zoom(scale_value)
            elif event.pos().x() < self.zoom_start.x():
                scale_value = 1.0 / (1 + (abs((event.x() - self.zoom_start.x())) / 100.0))
                self.zoom(scale_value)
        else:
            return QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def zoom(self, scale_value):
        """
        Changes the scale of the current scene by the value provided with argument. This scale is calculated mostly
        during the right mouse dragging.
        :type scale_value: float
        :return: None
        :rtype: None
        """
        if scale_value <= 0.1:
            scale_value = .01

        current_transform = self.zoom_start_transform  # Get the current transform for calculations

        # Zoom start is a zoom focus point. The scene will be zooming in or out against this point
        translate_matrix = QtGui.QTransform.fromTranslate(self.zoom_start.x(), self.zoom_start.y())
        inv_translate_matrix = translate_matrix.inverted()
        # This is current transform translated so that the zoom start point is in 0, 0
        local_current_transform = current_transform * inv_translate_matrix[0]

        # noinspection PyCallByClass,PyTypeChecker
        scale_matrix = QtGui.QTransform.fromScale(scale_value, scale_value)

        scaled_transform = local_current_transform * scale_matrix * translate_matrix

        # Check if the scale exceeds the max_zoom value. Zooming too much destroys the render quality of a graph
        scaled_transform_scale = self.get_matrix_scale(scaled_transform)
        if scaled_transform_scale > self.max_zoom:
            keep_scale_value = self.max_zoom / scaled_transform_scale
            # noinspection PyCallByClass,PyTypeChecker
            scale_matrix = scale_matrix * QtGui.QTransform.fromScale(keep_scale_value, keep_scale_value)
            scaled_transform = local_current_transform * scale_matrix * translate_matrix

        # set the final transform and keep the current scale in a variable
        self.setTransform(scaled_transform)
        self.get_current_scale()

    def get_current_scale(self):
        matrix = self.transform()
        map_point_zero = QtCore.QPointF(0.0, 0.0)
        map_point_one = QtCore.QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        self.current_scale = mapped_point_one.x() - mapped_point_zero.x()

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

        self.zoom_start = event.pos()
        if delta < 0:
            scale_value = .9
        else:
            scale_value = 1.1

        self.zoom(scale_value)

    def resizeEvent(self, event):
        """
        Resizes the scene together with scaling of the viewport.
        :param event:
        :return: None
        """
        current_size = self.size()

        if self.base_size is None:
            self.setBaseSize()

        if self.base_size is not 0 and self.base_size is not None:
            scale_value = float(current_size.width()) / float(self.base_size.width())

            if scale_value * self.current_scale > self.max_zoom:  # Keep the maximum scale allowed
                scale_value *= self.max_zoom / (scale_value * self.current_scale)

            self.base_size = self.size()
            self.scale(scale_value, scale_value)

        self.get_current_scale()
        return QtGui.QGraphicsView.resizeEvent(self, event)

    def setBaseSize(self):
        self.base_size = self.size()

    def fitInView(self, rect, keep_aspect_ratio):
        """
        Overrides default fitInView method to keep the maximum zoom value (we want to prevent from zooming too much)
        :param rect: Rectangle to fit in the view
        :type rect: QtCore.QRectF
        :param keep_aspect_ratio: not used.
        :return: None
        """

        self.setTransform(QtGui.QTransform())  # Start from identity transform

        top_left_offset = self.mapToScene(0, 0)  # This will put the 0,0 point of scene in 0,0 point of view
        top_left_transform = QtGui.QTransform.fromTranslate(top_left_offset.x(), top_left_offset.y())

        current_window_size = self.size()

        # calculate the scale needed to fit this rectangle in the view keeping the max zoom in
        if self.width() / float(self.height()) >= rect.width() / rect.height():
            scale_value = min(self.height() / float(rect.height()), self.max_zoom)
        else:
            scale_value = min(self.width() / float(rect.width()), self.max_zoom)
        scale_matrix = QtGui.QTransform.fromScale(scale_value, scale_value)
        scaled = scale_matrix * top_left_transform
        self.setTransform(scaled)

        # This point will be placed in a center of the view
        fit_center = rect.center()
        fit_center_scaled = scaled.map(QtCore.QPoint(fit_center.x(), fit_center.y()))  # scale matrix changed this
        fit_center_matrix = QtGui.QTransform.fromTranslate(fit_center_scaled.x(), fit_center_scaled.y())

        # Get the center of the viewport, add a top_left_offset to it to keep everything consistent
        translated_center = QtCore.QPointF(current_window_size.width()/2.0, current_window_size.height()/2.0)
        to_center_offset = translated_center + top_left_offset
        to_screen_center_transform = QtGui.QTransform.fromTranslate(to_center_offset.x(), to_center_offset.y())

        # Set the final transform
        self.setTransform(scaled * fit_center_matrix.inverted()[0] * to_screen_center_transform)

    def zoom_to_selected(self):
        """
        Fits the united bounding rect of selected gung nodes in the viewport keeping the maximum zoom value.
        :return: None
        """
        sel_items = self.scene().selectedItems()
        if len(sel_items) > 0:
            zoom_rect = QtCore.QRectF()
            for item in sel_items:
                if not isinstance(item, GungNode):
                    continue
                item_rect = item.boundingRect()
                zoom_rect = zoom_rect.united(item_rect.translated(item.x(), item.y()))

            self.fitInView(zoom_rect, QtCore.Qt.KeepAspectRatio)
            self.get_current_scale()

    def zoom_to_all(self):
        all_nodes = self.get_nodes()
        if len(all_nodes) > 0:
            zoom_rect = all_nodes[0].boundingRect().translated(all_nodes[0].x(), all_nodes[0].y())
            for item in all_nodes[1:]:
                item_rect = item.boundingRect()
                zoom_rect = zoom_rect.united(item_rect.translated(item.x(), item.y()))
            self.fitInView(zoom_rect, QtCore.Qt.KeepAspectRatio)
            self.get_current_scale()
        else:
            self.setTransform(QtGui.QTransform())

    def get_nodes(self):
        """
        Gathers all gung items from the current scene
        :return: nodes
        :rtype: list of gung.gungnode.GungItem
        """
        scene_items = self.scene().items()
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
        elif event.key() == QtCore.Qt.Key_A:
            self.zoom_to_all()
            event.accept()
        elif event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ControlModifier:
            self.undoSignal.emit()
        elif event.key() == QtCore.Qt.Key_Y and event.modifiers() == QtCore.Qt.ControlModifier:
            self.redoSignal.emit()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.deleteSignal.emit()
        elif event.key() == QtCore.Qt.Key_G and event.modifiers() == QtCore.Qt.ControlModifier:
            self.groupSignal.emit()
        else:
            return QtGui.QGraphicsView.keyPressEvent(self, event)

    def drawBackground(self, painter, rect):
        painter.setFont(self.font)
        painter.setPen(self.text_pen)
        painter.setBrush(self.text_brush)
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
