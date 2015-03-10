from PySide.QtGui import QGraphicsScene
from gungnode import GungItem

class GungScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.topZ = 0.0000

    def getNewId(self):
        index = 0
        currentIds = []
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if not "nodeId" in item.properties.keys():
                continue
            
            currentIds.append(item.properties["nodeId"])

        while index in currentIds:
            index += 1

        return index

    def getNodeById(self, id_):
        for item in self.items():
            if not isinstance(item, GungItem):
                continue
            if item.properties["nodeId"] == id_:
                return item
        return None