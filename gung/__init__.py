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
from gungnode import GungNode, GungPlug, GungAttribute, GungEdge


from random import randrange



testgung_xml = """<?xml version="1.0" ?>
<GungGraph>
    <GungNode minimalHeight="74" minimalWidth="14" name="test9" nodeHeight="74.0" nodeId="51" nodeWidth="100.0" posX="945.0" posY="0.0">
        <GungAttribute attrHeight="15" nodeId="52" posX="1.0" posY="20.0">
            <GungPlug nodeId="53" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="54" posX="1.0" posY="37.0">
            <GungPlug nodeId="55" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="55" minimalWidth="0.0" name="test8" nodeHeight="55.0" nodeId="50" nodeWidth="100.0" posX="840.0" posY="0.0"/>
    <GungNode minimalHeight="74" minimalWidth="14" name="test7" nodeHeight="74.0" nodeId="45" nodeWidth="100.0" posX="735.0" posY="0.0">
        <GungAttribute attrHeight="15" nodeId="46" posX="1.0" posY="20.0">
            <GungPlug nodeId="47" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="48" posX="1.0" posY="37.0">
            <GungPlug nodeId="49" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="108" minimalWidth="14" name="test6" nodeHeight="108.0" nodeId="36" nodeWidth="100.0" posX="630.0" posY="0.0">
        <GungAttribute attrHeight="15" nodeId="37" posX="1.0" posY="20.0">
            <GungPlug nodeId="38" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="39" posX="1.0" posY="37.0">
            <GungPlug nodeId="40" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="41" posX="1.0" posY="54.0">
            <GungPlug nodeId="42" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="43" posX="1.0" posY="71.0">
            <GungPlug nodeId="44" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" minimalWidth="14" name="test5" nodeHeight="91.0" nodeId="29" nodeWidth="100.0" posX="525.0" posY="130.0">
        <GungAttribute attrHeight="15" nodeId="30" posX="1.0" posY="20.0">
            <GungPlug nodeId="31" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="32" posX="1.0" posY="37.0">
            <GungPlug nodeId="33" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="34" posX="1.0" posY="54.0">
            <GungPlug nodeId="35" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" minimalWidth="14" name="test4" nodeHeight="91.0" nodeId="22" nodeWidth="100.0" posX="420.0" posY="45.0">
        <GungAttribute attrHeight="15" nodeId="23" posX="1.0" posY="20.0">
            <GungPlug nodeId="24" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="25" posX="1.0" posY="37.0">
            <GungPlug nodeId="26" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="27" posX="1.0" posY="54.0">
            <GungPlug nodeId="28" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" minimalWidth="14" name="test3" nodeHeight="91.0" nodeId="15" nodeWidth="100.0" posX="315.0" posY="50.0">
        <GungAttribute attrHeight="15" nodeId="16" posX="1.0" posY="20.0">
            <GungPlug nodeId="17" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="18" posX="1.0" posY="37.0">
            <GungPlug nodeId="19" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="20" posX="1.0" posY="54.0">
            <GungPlug nodeId="21" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="55" minimalWidth="0.0" name="test2" nodeHeight="55.0" nodeId="14" nodeWidth="100.0" posX="210.0" posY="150.0"/>
    <GungNode minimalHeight="91" minimalWidth="14" name="test1" nodeHeight="91.0" nodeId="7" nodeWidth="100.0" posX="105.0" posY="10.0">
        <GungAttribute attrHeight="15" nodeId="8" posX="1.0" posY="20.0">
            <GungPlug nodeId="9" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="10" posX="1.0" posY="37.0">
            <GungPlug nodeId="11" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="12" posX="1.0" posY="54.0">
            <GungPlug nodeId="13" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" minimalWidth="14" name="test0" nodeHeight="91.0" nodeId="0" nodeWidth="100.0" posX="0.0" posY="0.0">
        <GungAttribute attrHeight="15" nodeId="1" posX="1.0" posY="20.0">
            <GungPlug nodeId="2" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="3" posX="1.0" posY="37.0">
            <GungPlug nodeId="4" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
        <GungAttribute attrHeight="15" nodeId="5" posX="1.0" posY="54.0">
            <GungPlug nodeId="6" plugHeight="14" plugWidth="14" posX="0.0" posY="0.0"/>
        </GungAttribute>
    </GungNode>
</GungGraph>
"""

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
    
    scene.fromXml(testgung_xml)
#     for i in range(10):
#         node = GungNode("test%i" % i, None, scene)
#         node.setX(i * 105)
#         #a = GungAttribute(node, scene)
#         for p in range(int(randrange(0, 5))):
#             a = GungAttribute(node, scene)
#             #for p in range(int(randrange(0, 15))):
#             plug = GungPlug(a, scene)
#             a.rearrangePlugs()
#         node.rearrangeAttributes()
     
    e = GungEdge(scene=scene)
    e.properties['itemFromId'] = 19
    e.properties['itemToId'] = 33
    e.reconnectEdge()
    w.show()
    
    xml = scene.asXml()
    print xml.toprettyxml("    ")
    
    app.exec_()
    sys.exit(0)
