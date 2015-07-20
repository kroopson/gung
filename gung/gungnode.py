import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from PySide.QtCore import QPoint
from xml.dom import Node
import inspect
import sys

from config import GungConfig, ConfigParser

config = GungConfig()


def get_gung_node_classes():
    gung_classes = {}
    for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if 'element_type' in obj.__dict__.keys():
            gung_classes[name] = obj
    return gung_classes


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

        self.itemWidth = config.getfloat("Resizer", "Width")
        self.itemHeight = config.getfloat("Resizer", "Height")

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
            # --- When this item position is changed call the trigger signal resize_node.
            # --- This allows undo/redo of this command.
            self.scene().resize_node(self.parentItem().properties['node_id'], p,
                                     self.storedPos)
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

        painter.drawPolygon([QPoint(0, 0),
                             QPoint(-self.itemWidth, 0),
                             QPoint(0, -self.itemHeight)],
                            QtCore.Qt.OddEvenFill)

    def boundingRect(self):
        return QtCore.QRectF(-self.itemWidth, -self.itemHeight, self.itemWidth, self.itemHeight)

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
            parent_min_width = self.parentItem().properties['min_width']
            parent_min_height = self.parentItem().properties['min_height']

            if value.x() < parent_min_width:
                value.setX(parent_min_width)
                self.setX(parent_min_width)

            if value.y() < parent_min_height:
                value.setY(parent_min_height)
                self.setY(parent_min_height)
            self.parentItem().set_size(self.pos())

        return QtGui.QGraphicsItem.itemChange(self, change, value)


items = []


class GungItem(QtGui.QGraphicsItem):
    """
    Base class for all GUNG scene items. Inside the constructor it will try to obtain the unique id for this item
    that will be used later in every important operation (especially during the connection of the plugs, undo/redo,
    save/load). The utility items like resizer are not considered as a GUNG items.
    """
    element_type = "GungNode"

    def __init__(self, parent=None, scene=None, node_id=None):
        QtGui.QGraphicsItem.__init__(self, parent, scene)

        # self.self_target = self  # This keeps the reference to the object so it
        # won't get collected by garbage collector
        # later on: How idiotic this was...

        # keep this item in a list to avoid collecting it by the garbage collector
        items.append(self)

        self.id_ = None

        self.properties = dict()

        self.properties['pos_x'] = 0.0
        self.properties['pos_y'] = 0.0

        if node_id is None:
            node_id = self.scene().get_new_id()

        self.properties["node_id"] = node_id
        self.parent_ = parent

    def as_xml(self, document):
        """
        Returns this item and all its sub items as an xml element.
        """
        element = document.createElement(self.element_type)

        self.properties["posX"] = self.pos().x()

        for p in self.properties.keys():
            element.setAttribute(p, str(self.properties[p]))

        for item in self.childItems():
            if not isinstance(item, GungItem):
                continue
            item_element = item.as_xml(document)
            element.appendChild(item_element)

        return element

    def from_xml(self, xmlnode):
        for k in xmlnode.attributes.keys():
            if k not in self.properties.keys():
                continue
            self.properties[k] = type(self.properties[k])(xmlnode.attributes[k].value)

        self.setX(self.properties['pos_x'])
        self.setY(self.properties['pos_y'])

        classes = get_gung_node_classes()
        for node in xmlnode.childNodes:
            if not node.nodeType == Node.ELEMENT_NODE:
                continue
            if node.tagName not in classes.keys():
                continue
            gn = classes[node.tagName](parent=self, scene=self.scene())
            gn.from_xml(node)

    @staticmethod
    def get_color_config(section, option):
        try:
            node_color = config.get(section, option)
            r, g, b = [int(x) for x in node_color.split(",")]
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            print "Failed to get the color option", section, option
            r, g, b = (0, 0, 0,)
        return QtGui.QColor(r, g, b, )

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
            # --- inform the scene that this item has moved.
            if isinstance(self.parent_, GungGroup):
                self.parent_.update_bounding_rect()

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def setParentItem(self, parent_item):
        self.parent_ = parent_item
        QtGui.QGraphicsItem.setParentItem(self, parent_item)


class GungNode(GungItem):
    """
    Base class of the graphical node. Inherit this to get some specific look of your nodes.
    """
    element_type = "GungNode"
    resizerClass = GungNodeResizer

    def __init__(self, name="", parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.resizer = None

        self.properties['name'] = name
        self.properties['node_width'] = config.getfloat("Node", "MinimalWidth")
        self.properties['node_height'] = config.getfloat("Node", "MinimalHeight")
        self.properties['min_width'] = config.getfloat("Node", "MinimalWidth")
        self.properties['min_height'] = config.getfloat("Node", "MinimalHeight")

        self.bboxW = config.getfloat("Node", "MinimalWidth")
        self.bboxH = config.getfloat("Node", "MinimalHeight")

        self.nodeColor = self.get_color_config("Node", "NodeColor")
        self.lightGrayBrush = QtGui.QBrush(self.nodeColor)
        self.darkGrayBrush = QtGui.QBrush(QtCore.Qt.darkGray)

        self.selectedPen = QtGui.QPen(self.get_color_config("Node", "SelectedEdgeColor"))
        self.unselectedPen = QtGui.QPen(self.get_color_config("Node", "UnSelectedEdgeColor"))
        self.textPen = QtGui.QPen(self.get_color_config("Node", "TextColor"))

        self.plugFont = QtGui.QFont("Arial", 7)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

        self.draggingNode = None

        self.create_resizer()
        self.update_bbox()

        self.parent_ = parent

    def request_minimum_width(self, minimum_width):
        if minimum_width < config.getfloat("Node", "MinimalWidth"):
            minimum_width = config.getfloat("Node", "MinimalWidth")

        if self.properties['min_width'] < minimum_width:
            self.properties['min_width'] = minimum_width

        if self.properties['node_width'] < minimum_width:
            self.properties['node_width'] = minimum_width

        if self.resizer.pos().x() < minimum_width:
            self.resizer.setX(minimum_width)

    def create_resizer(self):
        """
        Adds a special type of child item that will control the size of this node.
        This is a typical behaviour of a node systems, that allows you to resize the nodes with a small widget.
        """
        self.resizer = self.resizerClass(self, self.scene())
        self.resizer.setX(self.properties['node_width'])
        self.resizer.setY(self.properties['node_height'])

    def update_bbox(self):
        self.bboxW = self.properties['node_width']
        self.bboxH = self.properties['node_height']

    def rearrange_attributes(self):
        current_height = -1
        for child_item in self.childItems():
            if not isinstance(child_item, GungAttribute):
                continue

            child_item.setX(0)
            if current_height == -1:
                current_height = 20

            child_item.setX(0)
            child_item.setY(current_height)
            current_height += child_item.properties['attr_height'] + 2

        if current_height >= 35:
            self.properties['min_height'] = current_height + 20.0
        else:
            self.properties['min_height'] = 35 + 20.0

        if self.properties['node_height'] < self.properties['min_height']:
            self.properties['node_height'] = self.properties['min_height']
            self.resizer.setY(self.properties['min_height'])

        for child_item in self.childItems():
            if not isinstance(child_item, GungAttribute):
                continue
            child_item.rearrange_plugs()

    def mousePressEvent(self, event):
        self.scene().topZ += .0001
        self.setZValue(self.scene().topZ)
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def from_xml(self, xmlnode):
        GungItem.from_xml(self, xmlnode)
        self.resizer.setX(self.properties['node_width'])
        self.resizer.setY(self.properties['node_height'])

    def set_size(self, size):
        """
        Sets an attributes in properties dict, updates bounding box and calls the rearrangement
        of all attributes. This is needed if you want to have plugs "sticked" to the right edge
        of this node.
        """
        size_x = size.x() if size.x() >= self.properties['min_width'] else self.properties['min_width']
        self.properties['node_width'] = size_x
        size_y = size.y() if size.y() >= self.properties['min_height'] else self.properties['min_height']
        self.properties['node_height'] = size_y
        self.update()

        self.prepareGeometryChange()
        self.update_bbox()

        self.rearrange_attributes()

    def paint(self, painter, option, widget=None):
        """
        Override of QGraphicsItem.paint method. Implement this in your child classes to
        make nodes with the look you want.
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # --- Distinguish the selected nodes from the unselected ones.
        if self.isSelected():
            painter.setPen(self.selectedPen)
        else:
            painter.setPen(self.unselectedPen)

        painter.setBrush(self.nodeColor)
        painter.drawRect(0, 0, self.properties['node_width'], self.properties['node_height'])

        # --- Draw name of the node
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
            :rtype: QVariant
        """
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            # --- inform the scene that this item has moved.
            self.scene().nodesHaveMoved = True

            # if isinstance(self.parent_, GungGroup):
            #     self.parent_.update_bounding_rect()

        return GungItem.itemChange(self, change, value)

    def get_all_edges(self):
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

    def get_all_plugs(self):
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
    element_type = "GungAttribute"

    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent, scene)

        self.properties['attr_height'] = config.getfloat("Attribute", "Height")

    def paint(self, painter, option, widget=None):
        pass

    def rearrange_plugs(self):
        plugs = []
        for childitem in self.childItems():
            if not isinstance(childitem, GungPlug):
                continue
            plugs.append(childitem)

        if not len(plugs):
            return

        in_plugs = []
        out_plugs = []

        for p in plugs:
            if isinstance(p, GungOutPlug):
                out_plugs.append(p)
                continue
            if isinstance(p, GungPlug):
                in_plugs.append(p)

        index = 0
        total_width = 0
        for p in in_plugs:
            w = index * p.properties['plug_width']
            p.setX(w)
            p.setY(0)
            total_width += p.properties['plug_width']
            index += 1

        parent_bounding = self.parentItem().boundingRect()
        index = 1
        for p in out_plugs:
            w = (index * p.properties['plug_width']) + 1
            p.setX(parent_bounding.width() - w)
            p.setY(0)
            total_width += p.properties['plug_width']
            index += 1

        if isinstance(self.parentItem(), GungNode):
            self.parentItem().request_minimum_width(total_width)

    def boundingRect(self):
        """
        Override this in child classes.
        """

        return QtCore.QRectF(0, 0, self.parentItem().properties['node_width'], self.properties['attr_height'])


class GungPlug(GungItem):
    element_type = "GungPlug"
    acceptsConnections = "GungOutPlug"

    def __init__(self, parent=None, scene=None):
        GungItem.__init__(self, parent=parent, scene=scene)

        self.properties['plug_width'] = 14.0
        self.properties['plug_height'] = 14.0

        self.isHighlighted = False

        plug_color = QtGui.QColor(150, 255, 150)

        self.plugPen = QtGui.QPen(plug_color.lighter())
        self.plugBrush = QtGui.QBrush(plug_color)
        self.highlightedPlugBrush = QtGui.QBrush(plug_color.lighter())

        self.edges = []

        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)

    def accepts_drop(self, plug_out):
        result = False
        if plug_out.element_type in self.acceptsConnections.split(","):
            result = True
        return result

    def mousePressEvent(self, event):
        event.accept()
        self.scene().init_dragging_edge(self.mapToScene(self.boundingRect().center()), self)

    def mouseMoveEvent(self, event):
        return GungItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.scene().dragging_ended(self.mapToScene(event.pos()))
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
        # painter.drawRect(0, 0, self.properties['plug_width'], self.properties['plug_height'])
        painter.drawEllipse(1, 1, self.properties['plug_width'] - 1, self.properties['plug_height'] - 1)

    def set_highlited(self, state):
        self.isHighlighted = state
        self.update()

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.properties['plug_width'], self.properties['plug_height'])

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
                if edge.item_to is self:
                    edge.prepareGeometryChange()
                    edge.set_to_pos(self.mapToScene(self.boundingRect().center()))
                if edge.item_from is self:
                    edge.prepareGeometryChange()
                    edge.set_from_pos(self.mapToScene(self.boundingRect().center()))

        return QtGui.QGraphicsItem.itemChange(self, change, value)


class GungInPlug(GungPlug):
    element_type = "GungInPlug"
    acceptsConnections = "GungOutPlug"

    def __init__(self, parent=None, scene=None):
        GungPlug.__init__(self, parent=parent, scene=scene)

    def mousePressEvent(self, event):
        """
        Overrides the GungPlug mousePressEvent method. If this plug has any incoming connections it will remove
        the edge placed on top of edges stack and it will start the dragging edge.
        """
        if not self.edges:
            event.accept()
            self.scene().init_dragging_edge(self.mapToScene(self.boundingRect().center()), self)
            return

        edge = self.edges.pop()
        item_from = edge.item_from
        self.scene().init_dragging_edge(item_from.mapToScene(item_from.boundingRect().center()), item_from)
        self.scene().delete_edge_call(edge_id=edge.properties['node_id'])


class GungOutPlug(GungPlug):
    element_type = "GungOutPlug"
    acceptsConnections = "GungPlug,GungInPlug"

    def __init__(self, parent=None, scene=None):
        GungPlug.__init__(self, parent=parent, scene=scene)


class GungGroup(GungItem):
    element_type = "GungGroup"

    def __init__(self, parent=None, scene=None, node_id=None):
        """
        Base class to inherit if you want to create your own groups.
        """
        GungItem.__init__(self, parent, scene)
        self.rect = QtCore.QRectF()

        self.group_color = self.get_color_config("Group", "GroupBackground")
        self.group_brush = QtGui.QBrush(self.group_color)

        try:
            self.offset = config.getfloat("Group", "GroupOffset")
        except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
            self.offset = 10

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

        # TODO: Double check if this is even needed.
        self._node_id = node_id

    def update_bounding_rect(self):
        rect = None
        if not self.childItems():  # return the last registered bounding box if the group has no children.
            return self.rect

        for item in self.childItems():  # iterate only groups and nodes
            if not item.__class__.__name__ == "GungNode" and not item.__class__.__name__ == "GungGroup":
                continue

            # --- get the bounding box of all items.
            r = item.boundingRect()
            r.translate(item.pos())
            r.adjust(-self.offset, -self.offset, self.offset, self.offset)
            if rect is None:
                rect = QtCore.QRectF(r)
                continue
            rect = rect.united(r)
        if rect is None:
            self.rect = QtCore.QRectF()
        else:
            self.rect = QtCore.QRectF(rect)
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.group_brush)
        painter.drawRect(self.rect)

    def boundingRect(self):
        return self.rect

    def mousePressEvent(self, event):
        self.scene().topZ += .0001
        self.setZValue(self.scene().topZ)
        return QtGui.QGraphicsItem.mousePressEvent(self, event)

    def itemChange(self, change, value):
        """
        Called whenever a change happens to the instance of this class like move, click, resize ect.
        In this case used to register position changes of the nodes, so that they can be reverted using the
        undo queue.

            :param change: defines a type of a change
            :param value: defines a value of a change
            :rtype: QVariant
        """
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            # --- inform the scene that this item has moved.
            self.scene().nodesHaveMoved = True

            # if isinstance(self.parent_, GungGroup):
            #     self.parent_.update_bounding_rect()

        return GungItem.itemChange(self, change, value)


class GungEdge(GungItem):
    def __init__(self, item_from_id, item_to_id, parent=None, scene=None):
        GungItem.__init__(self, None, scene)

        self.properties['item_from_id'] = item_from_id
        self.properties['item_to_id'] = item_to_id

        self.item_from = None
        self.item_to = None

        item_from = self.scene().get_item_by_id(int(item_from_id))
        item_to = self.scene().get_item_by_id(int(item_to_id))

        self.from_pos = item_from.mapToScene(item_from.boundingRect().center())
        self.to_pos = item_to.mapToScene(item_to.boundingRect().center())

        self.edge_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.setZValue(self.scene().topEdgeZ)
        self.scene().topEdgeZ += .0001

        self.bounding_rect = QtCore.QRectF()

        self._parent = parent

    def reconnect_edge(self):
        if not self.properties['item_from_id'] == -1 \
                and not self.properties['item_from_id'] == self.properties['node_id']:
            self.item_from = self.scene().get_item_by_id(int(self.properties['item_from_id']))
            if self.item_from is not None:
                self.item_from.edges.append(self)
                self.set_from_pos(self.item_from.mapToScene(self.item_from.boundingRect().center()))
        if not self.properties['item_to_id'] == -1 and not self.properties['item_to_id'] == self.properties['node_id']:
            self.item_to = self.scene().get_item_by_id(int(self.properties['item_to_id']))
            if self.item_to is not None:
                self.item_to.edges.append(self)
                self.set_to_pos(self.item_to.mapToScene(self.item_to.boundingRect().center()))
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)

    def disconnect_edge(self):
        # TODO: Make it more loose coupled. Now it's a field for errors.
        while self in self.item_from.edges:
            self.item_from.edges.remove(self)
        while self in self.item_to.edges:
            self.item_to.edges.remove(self)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, True)

    def paint(self, painter, option, widget=None):
        if self.item_from is None or self.item_to is None:
            return
        painter.setPen(self.edge_pen)
        pos_start = self.item_from.mapToScene(QtCore.QPointF()) + self.item_from.boundingRect().center()
        pos_end = self.item_to.mapToScene(QtCore.QPointF()) + self.item_to.boundingRect().center()

        knot_a = QtCore.QPointF((pos_start.x() + pos_end.x()) / 2.0, pos_start.y())
        knot_b = QtCore.QPointF((pos_start.x() + pos_end.x()) / 2.0, pos_end.y())
        path = QtGui.QPainterPath()
        path.moveTo(pos_start)
        path.cubicTo(knot_a, knot_b, pos_end)
        painter.drawPath(path)

    def set_from_pos(self, point_from):
        self.from_pos = QtCore.QPointF(point_from)

        top_left_x = min(float(self.from_pos.x()), float(self.to_pos.x()))
        top_left_y = min(float(self.from_pos.y()), float(self.to_pos.y()))

        bottom_right_x = max(float(self.from_pos.x()), float(self.to_pos.x()))
        bottom_right_y = max(float(self.from_pos.y()), float(self.to_pos.y()))
        self.bounding_rect = QtCore.QRectF(top_left_x, top_left_y, bottom_right_x - top_left_x,
                                           bottom_right_y - top_left_y)

    def set_to_pos(self, point_to):
        self.to_pos = QtCore.QPointF(point_to)

        top_left_x = min(float(self.from_pos.x()), float(self.to_pos.x()))
        top_left_y = min(float(self.from_pos.y()), float(self.to_pos.y()))

        bottom_right_x = max(float(self.from_pos.x()), float(self.to_pos.x()))
        bottom_right_y = max(float(self.from_pos.y()), float(self.to_pos.y()))
        self.bounding_rect = QtCore.QRectF(top_left_x, top_left_y, bottom_right_x - top_left_x,
                                           bottom_right_y - top_left_y)

    def boundingRect(self, *args, **kwargs):
        return self.bounding_rect
