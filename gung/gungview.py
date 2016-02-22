from PySide import QtGui, QtCore
from PySide.QtCore import Signal
from gungnode import GungNode, GungItem
from gungscene import GungScene

QString = str  # <- this is to keep the compatibility between PySide and PyQt
versionString = "GUNG v.0.2.1"


class GungGraphicsView(QtGui.QGraphicsView):
    """
    GUNG graph viewport class. Handles view manipulation (move, zoom, select).
    """
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

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

        # =======================================================================
        # SELECTION OF NODES
        # =======================================================================
        # If true the widget will add to the selection
        self.extend_selection = False
        self.remove_selection = False
        self.selection_start = QtCore.QPoint()
        self.rubber_band = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):
        """
        Called whenever the mouse is pressed inside the view

            :param QtGui.QMouseEvent event:
        """
        # --- If shift is pressed items will be added to selection
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            self.extend_selection = True
        else:
            self.extend_selection = False

        # --- If alt is pressed items will be removed from selection
        if event.modifiers() == QtCore.Qt.AltModifier:
            self.remove_selection = True
        else:
            self.remove_selection = False

        if event.button() == QtCore.Qt.MidButton:  # Start viewport translation
            self.prev_mouse_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:  # Start viewport zoom
            self.zoom_start = event.pos()
            self.zoom_start_transform = self.transform()
        elif event.button() == QtCore.Qt.LeftButton:  # Left mouse pressed. Either select node or start rubber band drag
            node = self.scene().get_node_at_point(self.mapToScene(event.pos()))
            if node:
                if not self.extend_selection and not node.isSelected() and not self.remove_selection:
                    for item in self.scene().selectedItems():
                        item.setSelected(False)

                if self.remove_selection:
                    node.setSelected(False)
                else:
                    node.setSelected(True)

                if self.extend_selection or self.remove_selection:
                    event.accept()
                    return
                else:
                    return QtGui.QGraphicsView.mousePressEvent(self, event)
            else:
                self.selection_start = event.pos()
                self.rubber_band.setGeometry(QtCore.QRect(self.selection_start, self.selection_start))
                self.rubber_band.show()
                event.accept()
        else:  # Unknown type of mouse button. Just skip it.
            return QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Called whenever the mouse is moved inside the viewport and one of mouse buttons is pressed.

            :param QtGui.QMouseEvent event:
        """
        if event.buttons() == QtCore.Qt.MidButton:  # Translate the viewport
            if self.prev_mouse_pos:
                current_mouse_pos = event.globalPos()
                x = (current_mouse_pos - self.prev_mouse_pos).x()
                y = (current_mouse_pos - self.prev_mouse_pos).y()
                self.translate(x / self.current_scale, y / self.current_scale)
            self.prev_mouse_pos = event.globalPos()
        elif event.buttons() == QtCore.Qt.RightButton:  # Zoom viewport
            if event.pos().x() > self.zoom_start.x():
                scale_value = 1 + abs((event.x() - self.zoom_start.x()) / 100.0)
                self.zoom(scale_value)
            elif event.pos().x() < self.zoom_start.x():
                scale_value = 1.0 / (1 + (abs((event.x() - self.zoom_start.x())) / 100.0))
                self.zoom(scale_value)
        elif event.buttons() == QtCore.Qt.LeftButton:  # Drag selection rubber band
            if self.rubber_band.isHidden():
                return QtGui.QGraphicsView.mouseMoveEvent(self, event)
            selection_rect = QtCore.QRect()
            point = event.pos()
            selection_rect.setX(point.x() if point.x() < self.selection_start.x() else self.selection_start.x())
            selection_rect.setY(point.y() if point.y() < self.selection_start.y() else self.selection_start.y())

            selection_rect.setWidth(abs(point.x() - self.selection_start.x()))
            selection_rect.setHeight(abs(point.y() - self.selection_start.y()))
            self.rubber_band.setGeometry(selection_rect)
            event.accept()
        else:  # Unknown type of mouse button. Just skip it.
            return QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Called whenever the mouse button is released after it's been clicked inside viewport.

            :param QtGui.QMouseEvent event:
        """
        if event.button() == QtCore.Qt.LeftButton:
            if not self.rubber_band.isHidden():
                # --- selection of items with rubber band is handled here
                select = True
                if event.modifiers() == QtCore.Qt.ShiftModifier:
                    self.extend_selection = True
                elif event.modifiers() == QtCore.Qt.AltModifier:
                    self.extend_selection = True
                    select = False
                else:
                    self.extend_selection = False
                self.select_items_in_rubber_band(self.rubber_band.geometry(), self.extend_selection, select)
            else:
                # --- selection through click is handled here
                item = self.itemAt(event.pos())
                if item is not None:
                    if not self.remove_selection:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        self.rubber_band.hide()
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def select_items_in_rubber_band(self, rect, append=True, select=True):
        """
        Iterates all the items that collides with selection rubber band and selects them if they are selectable.

            :param QtCore.QRect rect: selection rectangle (this is the rubber band geometry)
            :param bool append: if set to True an old selection will be preserved.
            :param select: if set to False those items will be unselected.
        """
        modified = False
        if append is False:
            self.scene().clearSelection()
        scene_top_left = self.mapToScene(rect.topLeft())
        scene_bottom_right = self.mapToScene(rect.bottomRight())
        items = self.scene().items(QtCore.QRectF(scene_top_left, scene_bottom_right),
                                   QtCore.Qt.IntersectsItemBoundingRect)
        for item in items:
            if (item.flags() & QtGui.QGraphicsItem.ItemIsSelectable) == QtGui.QGraphicsItem.ItemIsSelectable:
                item.setSelected(select)
                modified = True
        if modified:
            self.scene().emit(QtCore.SIGNAL("selectionChanged()"))

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
        """
        Returns the scale value of current viewport matrix.

            :rtype: float
        """
        matrix = self.transform()
        map_point_zero = QtCore.QPointF(0.0, 0.0)
        map_point_one = QtCore.QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        self.current_scale = mapped_point_one.x() - mapped_point_zero.x()

    @staticmethod
    def get_matrix_scale(matrix):
        """
        Gets the scale component of a matrix provided as an argument

            :param matrix:
            :rtype: float
        """
        map_point_zero = QtCore.QPointF(0.0, 0.0)
        map_point_one = QtCore.QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        return (mapped_point_one - mapped_point_zero).manhattanLength()

    def wheelEvent(self, event):
        """
        Called when user uses the mouse wheel inside the viewport.

            :param QtGui.QMouseEvent event:
        """
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
        Resize the scene together with scaling of the viewport.

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
        """
        """
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
        translated_center = QtCore.QPointF(current_window_size.width() / 2.0, current_window_size.height() / 2.0)
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
        """
        Tries to fit the viewport so that all the items of the scene are visible.
        """
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
        """
        Called whenever a keyboard button is pressed and the viewport has a keyboard focus

            :param QtGui.QKeyEvent event:
        """
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
        """
        Called whenever the background re-paint is required. Override this in your child classes to have a custom graph
        look.
            :param QtGui.QPainter painter:
            :param QtCore.QRect rect:
        """
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

        painter.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
        painter.drawLine(0, self.height() / 2, self.width(), self.height() / 2)

        painter.drawText(w + 2, self.height() - 6, QString(versionString))

        return QtGui.QGraphicsView.drawBackground(self, painter, rect)

    def setScene(self, scene):
        """
        Sets the provided scene as the viewport scene. If the GungScene is provided it will also connect all the signals
        and slots.

            :param gung.gungscene.GungScene scene:
        """
        if isinstance(scene, GungScene):
            # scene.draggingStarted.connect(self.startDragging)
            self.undoSignal.connect(scene.undo_called)
            self.redoSignal.connect(scene.redo_called)
            self.deleteSignal.connect(scene.delete_called)
            self.groupSignal.connect(scene.create_group_called)
        return QtGui.QGraphicsView.setScene(self, scene)
