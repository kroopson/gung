from PySide import QtGui, QtCore

from gungview import GungGraphicsView
from gungscene import GungScene
from gungnode import GungNode, GungPlug

from random import randrange


if __name__ == "__main__":
    from PySide.QtGui import QApplication
    import sys
    app = QApplication([])
    
    w = QtGui.QWidget()
    
    wlyt = QtGui.QVBoxLayout()
    w.setLayout(wlyt)
    
    view = GungGraphicsView(w)
    wlyt.addWidget(view)
    
    scene = GungScene(view)
    view.setScene(scene)
    
    
    for i in range(10):
        node = GungNode("test%i" % i, None, scene)
        node.setX(i * 105)
        for p in range(int(randrange(0,5))):
            plug = GungPlug(node, scene)
        node.rearrangePlugs()
    w.show()
    app.exec_()
    sys.exit(0)
