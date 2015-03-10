"""
The MIT License (MIT)

Copyright (c) 2015 Michal Krupa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


from PySide import QtGui, QtCore

from gungview import GungGraphicsView
from gungscene import GungScene
from gungnode import GungNode, GungPlug, GungAttribute

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
        #a = GungAttribute(node, scene)
        for p in range(int(randrange(0, 5))):
            a = GungAttribute(node, scene)
            for p in range(int(randrange(0, 15))):
                plug = GungPlug(a, scene)
            a.rearrangePlugs()
        node.rearrangeAttributes()
    w.show()
    app.exec_()
    sys.exit(0)
