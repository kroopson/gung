from PySide import QtGui, QtCore
from PySide.QtGui import QGraphicsScene, QGraphicsItem, QUndoStack
from PySide.QtCore import Signal, Slot, QPointF, QRectF

from gungcommand import GungCreateGroupCommand, GungCreateEdgeCommand, GungDeleteItemsCommand, GungMoveCommand
from gungcommand import GungResizeNodeCommand
from gungnode import GungItem, GungPlug, GungNode, GungEdge, GungGroup, get_gung_node_classes
import xml.dom.minidom as xmldom
from xml.dom import Node


class GungScene(QGraphicsScene):
    draggingStarted = Signal(int)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        
        self.topZ = 0.0000
        self.topEdgeZ = 1.0000
        self.isDragging = False
        self.dragFrom = None
        self.draggingEdge = GungDragEdge(scene=self)
        self.nodesHaveMoved = False
        self.undoStack = QUndoStack(self)
        
        self.highlighted_plugs = []
        self.removedItems = []

    def get_new_id(self):
        index = 0
        current_ids = []
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if 'node_id' not in item.properties.keys():
                continue
            
            current_ids.append(item.properties['node_id'])

        while index in current_ids:
            index += 1

        return index

    def get_item_by_id(self, id_):
        """
        Returns the GungItem with provided id
        :param id_:
        :return:
        :rtype: GungItem or GungNode or GungPlug or GungEdge
        """
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if item.properties['node_id'] == id_:
                return item
        return None

    def as_xml(self):
        """
        Returns self as an xml document.
        """
        impl = xmldom.getDOMImplementation()
        doc = impl.createDocument(None, "GungGraph", None)

        for node in self.items():
            
            if isinstance(node, GungNode):
                if not node.parentItem() is None:
                    continue
                
                xmlnode = node.as_xml(doc)
                doc.documentElement.appendChild(xmlnode)
                # sc = node.scene()  # I don't know why it's corrupted without it...
                node.scene()
        return doc
    
    def from_xml(self, xmlstring):
        """
        Parses XML string and fills the current scene with the nodes. The scene MUST be empty since
        this method sets the node id's that are loaded to the values stored in an xml.
        """
        dom = xmldom.parseString(xmlstring)
        
        classes = get_gung_node_classes()
         
        for node in dom.documentElement.childNodes:
            if not node.nodeType == Node.ELEMENT_NODE:
                continue
            if node.tagName not in classes.keys():
                continue
            gn = classes[node.tagName](parent=None, scene=self)
            gn.from_xml(node)

        for i in self.items():
            if not isinstance(i, GungEdge):
                continue
            i.reconnect_edge()

    def init_dragging_edge(self, drag_start, drag_end):
        """
        Starts the dragging and sets the start position of a dragged edge.
        :param drag_start: QPointF
        :param drag_end: GungItem
        :return:
        """
        self.isDragging = True
        self.draggingEdge.post_start = drag_start
        self.draggingEdge.pos_end = drag_start
        self.dragFrom = drag_end
        self.draggingEdge.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.draggingEdge.update()
        self.parent().setCursor(QtCore.Qt.ClosedHandCursor)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.MidButton:
            return QGraphicsScene.mouseMoveEvent(self, event)
        if event.buttons() == QtCore.Qt.RightButton:
            return QGraphicsScene.mouseMoveEvent(self, event)

        highlited_plug = None
        if self.isDragging:
            self.update_dragging_edge(event.scenePos())

            plug = self.get_plug_at_point(event.scenePos())

            if plug is not None:
                if plug.accepts_drop(self.dragFrom):
                    plug.set_highlited(True)
                    highlited_plug = plug
                    self.highlighted_plugs.append(plug)
                else:
                    self.parent().setCursor(QtCore.Qt.ForbiddenCursor)
            else:
                self.parent().setCursor(QtCore.Qt.ClosedHandCursor)
        else:
            self.parent().unsetCursor()

        templist = []
        for item in self.highlighted_plugs:
            if item is highlited_plug:
                templist.append(item)
                continue
            item.set_highlited(False)

        self.highlighted_plugs = templist

        return QGraphicsScene.mouseMoveEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        if self.nodesHaveMoved:
            self.check_if_nodes_moved()
            self.nodesHaveMoved = False
            
        for item in self.highlighted_plugs:
            item.set_highlited(False)
        self.highlighted_plugs = []
        
        return QGraphicsScene.mouseReleaseEvent(self, event)

    def check_if_nodes_moved(self):
        """
        Iterate all the nodes to see if they positions changed in comparison to the
        position values that they have stored in properties dictionary
        """
        
        nodes_that_have_moved = []
        for item in self.items():
            if not isinstance(item, (GungNode, GungGroup)):
                continue
            p = item.pos()
            if p.x() != item.properties['pos_x'] or p.y() != item.properties['pos_y']:
                nodes_that_have_moved.append(item)
        # --- if no nodes have moved return
        if not len(nodes_that_have_moved):
            return

        undo = GungMoveCommand(self)
        for node in nodes_that_have_moved:
            nodepos = node.pos()
            undo.nodes[int(node.properties['node_id'])] = [
                float(node.properties['pos_x']),
                float(node.properties['pos_y']),
                float(nodepos.x()),
                float(nodepos.y())
            ]

            # --- keep current position in the values of a dictionary so that this node will not be collected as moved
            # --- next time when scene checks if some nodes have moved.
            node.properties['pos_x'] = float(nodepos.x())
            node.properties['pos_y'] = float(nodepos.y())

        self.undoStack.push(undo)
        self.nodesHaveMoved = False
        
    def get_plug_at_point(self, pos):
        """
        Iterate all the items that occlude with the point passed as pos and see if there is a GungPlug among them.
        If not then return None
        :param pos: QPoint
        :rtype: GungPlug or None
        """
        hititems = self.items(pos)
        if not len(hititems):
            return
        hititem = None
        for hi in hititems:
            if isinstance(hi, GungPlug):
                hititem = hi
                break
            
        return hititem

    def dragging_ended(self, pos):
        # --- it the scene is not in "dragging" state then it means that
        # --- no action is necessary here
        if not self.isDragging:
            return
        
        # --- stop displaying the utility edge
        self.hide_dragging_edge()
        
        hititem = self.get_plug_at_point(pos)
        
        # --- stop if no plug is found
        if hititem is None:
            return
        
        # --- top if there is no item from which the dragging started
        if self.dragFrom is None:
            return
        
        # --- quit if the dragging ended on the same item
        if self.dragFrom is hititem:
            return
        
        # --- check if the in-plug actually accepts connections from the GungPlug held in self.dragFrom
        if not hititem.accepts_drop(self.dragFrom):
            return
        
        # --- check it maybe there is already a connection between those plugs
        for edge in self.dragFrom.edges:
            if edge is None:
                continue
            if hititem in [edge.itemFrom, edge.itemTo]:
                return
        for edge in hititem.edges:
            if edge is None:
                continue
            if self.dragFrom in [edge.itemFrom, edge.itemTo]:
                return
        
        # --- finally create an edge

        command = GungCreateEdgeCommand(self, self.dragFrom, hititem)
        self.undoStack.push(command)
        
    def remove_edge(self, edge_id):
        created_edge = self.get_item_by_id(edge_id)
        if created_edge is None:
            return
        created_edge.disconnect_edge()
        created_edge.prepareGeometryChange()        
        self.removeItem(created_edge)
        
    def update_dragging_edge(self, pos):
        self.draggingEdge.pos_end = pos
        self.draggingEdge.update_position()

    def hide_dragging_edge(self):
        self.isDragging = False
        self.draggingEdge.post_start = None
        self.draggingEdge.pos_end = None
        self.draggingEdge.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, True)
        self.draggingEdge.update()
        self.update()
        self.parent().unsetCursor()

    def resize_node(self, node_id, size, previous_size):
        c = GungResizeNodeCommand(self, node_id, size.x(), size.y(), previous_size.x(), previous_size.y())
        self.undoStack.push(c)

    @Slot()
    def delete_called(self):
        sel = self.selectedItems()
        nodes = []
        for item in sel:
            if isinstance(item, GungNode):
                nodes.append(item)
        if len(nodes):
            command = GungDeleteItemsCommand(self, nodes)
            self.undoStack.push(command)

    @Slot()
    def redo_called(self):
        self.undoStack.redo()

    @Slot()
    def undo_called(self):
        self.undoStack.undo()

    @Slot()
    def create_group_called(self):
        sel = self.selectedItems()
        nodes = []
        for item in sel:
            if isinstance(item, GungNode):
                nodes.append(item)
        if len(nodes):
            command = GungCreateGroupCommand(self, [node.properties['node_id'] for node in nodes])
            self.undoStack.push(command)

    @Slot()
    def print_graph(self):
        for item in self.items():
            print item


class GungDragEdge(QGraphicsItem):
    """
    Graphics item that is responsible for displaying the rubber band edge (used to visually
    create connections).
    """
    def __init__(self, scene=None):
        QGraphicsItem.__init__(self, None, scene)

        self.edge_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.setZValue(2.000)

        self.post_start = None
        self.pos_end = None

    def paint(self, painter, option, widget=None):
        if not self.scene().isDragging:
            return

        painter.setPen(self.edge_pen)

        if self.post_start is None or self.pos_end is None:
            return

        currentpos = self.mapToScene(QPointF())

        painter.drawLine(self.post_start - currentpos, self.pos_end - currentpos)

    def update_position(self):
        if self.post_start is None or self.pos_end is None:
            return

        top_left_x = min(self.post_start.x(), self.pos_end.x())
        top_left_y = min(self.post_start.y(), self.pos_end.y())

        self.setPos(QPointF(top_left_x, top_left_y))
        self.update()

    def boundingRect(self, *args, **kwargs):
        if not self.scene().isDragging:
            return QRectF()

        if self.post_start is None or self.pos_end is None:
            return QRectF()

        top_left_x = min(self.post_start.x(), self.pos_end.x())
        top_left_y = min(self.post_start.y(), self.pos_end.y())

        bottom_right_x = max(self.post_start.x(), self.pos_end.x())
        bottom_right_y = max(self.post_start.y(), self.pos_end.y())

        return QRectF(0, 0, bottom_right_x - top_left_x, bottom_right_y - top_left_y)

    def mouseReleaseEvent(self, *args, **kwargs):
        return QGraphicsItem.mouseReleaseEvent(self, *args, **kwargs)
