from PySide.QtGui import QGraphicsScene


class GungScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.topZ = 0.0000