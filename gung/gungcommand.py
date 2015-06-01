from PySide.QtGui import QUndoCommand
from gungnode import GungEdge
from gungnode import GungGroup


class GungMoveCommand(QUndoCommand):
    def __init__(self, scene):
        """
        This dictionary has to hold the id's as the keys and positions as values.
        i.e.
        {
        10 : [0,0,250,100]
        }
        This means that node with id of 10 has been moved from position 0, 0 to position 250, 100
        """
        QUndoCommand.__init__(self)
        self.nodes = {}
        self.scene = scene

    def undo(self, *args, **kwargs):
        for n in self.nodes.keys():
            gung_node = self.scene.get_item_by_id(n)
            gung_node.setX(self.nodes[n][0])
            gung_node.setY(self.nodes[n][1])
            gung_node.properties['pos_x'] = self.nodes[n][0]
            gung_node.properties['pos_y'] = self.nodes[n][1]
        self.scene.nodesHaveMoved = False

    def redo(self, *args, **kwargs):
        for n in self.nodes.keys():
            gung_node = self.scene.get_item_by_id(n)
            gung_node.setX(self.nodes[n][2])
            gung_node.setY(self.nodes[n][3])
            gung_node.properties['pos_x'] = self.nodes[n][2]
            gung_node.properties['pos_y'] = self.nodes[n][3]
        self.scene.nodesHaveMoved = False


class GungDeleteItemsCommand(QUndoCommand):
    """
    Removes items provided to the constructor.
    """
    def __init__(self, scene, nodes):
        QUndoCommand.__init__(self)
        self.scene = scene
        self.nodes = [x for x in nodes]

        self.edges = []

    def undo(self, *args, **kwargs):
        for n in self.nodes:
            self.scene.addItem(n)

        for e in self.edges:
            self.scene.addItem(e)
            e.reconnect_edge()

    def redo(self, *args, **kwargs):
        edges_to_delete = []
        for n in self.nodes:
            edges_to_delete += n.get_all_edges()

        for edge in edges_to_delete:
            edge.disconnect_edge()
        self.edges = edges_to_delete

        for e in edges_to_delete:
            self.scene.removeItem(e)

        for item in self.nodes:
            self.scene.removeItem(item)


class GungCreateEdgeCommand(QUndoCommand):
    """
    Creates an edge between two plugs provided in the constructor.
    """
    def __init__(self, scene, from_node, to_node):
        QUndoCommand.__init__(self)
        self.from_node_id = int(from_node.properties['node_id'])
        self.to_node_id = int(to_node.properties['node_id'])
        self.scene = scene
        self.created_edge_id = -1
        self.deleted_edge = None

    def undo(self, *args, **kwargs):
        self.scene.remove_edge(self.created_edge_id)

    def redo(self, *args, **kwargs):
        e = GungEdge(int(self.from_node_id), int(self.to_node_id), parent=None, scene=self.scene)
        e.reconnect_edge()
        self.created_edge_id = int(e.properties['node_id'])


class GungResizeNodeCommand(QUndoCommand):
    """
    Resizes the node.
    """
    def __init__(self, scene, node_id, width, height, previous_width, previous_height):
        QUndoCommand.__init__(self)
        self.nodeId = int(node_id)
        self.width = float(width)
        self.height = float(height)
        self.previousWidth = float(previous_width)
        self.previousHeight = float(previous_height)
        self.scene = scene

    def undo(self, *args, **kwargs):
        node = self.scene.get_item_by_id(self.nodeId)
        node.resizer.setX(self.previousWidth)
        node.resizer.setY(self.previousHeight)

    def redo(self, *args, **kwargs):
        node = self.scene.get_item_by_id(self.nodeId)
        node.resizer.setX(self.width)
        node.resizer.setY(self.height)


class GungCreateGroupCommand(QUndoCommand):
    """
    Creates the group of a gung nodes.
    """
    def __init__(self, scene, node_ids):
        QUndoCommand.__init__(self)
        self.group = None
        self.nodeIds = [int(x) for x in node_ids]  # I hope this creates a local copy of int list
        self.scene = scene

        self.group_id = -1

    def undo(self, *args, **kwargs):
        nodes = []
        for nid in self.nodeIds:
            node = self.scene.get_item_by_id(nid)
            nodes.append(node)
            node.setParentItem(None)

        group = self.scene.get_item_by_id(self.group_id)
        self.scene.removeItem(group)

    def redo(self, *args, **kwargs):
        if not len(self.nodeIds):
            return
        group = GungGroup(None, self.scene)
        for nodeId in self.nodeIds:
            node = self.scene.get_item_by_id(nodeId)
            node.setParentItem(group)

        group.update_bounding_rect()
        self.group_id = group.properties["node_id"]
