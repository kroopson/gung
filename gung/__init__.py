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


from PySide import QtGui

from gungview import GungGraphicsView
from gungscene import GungScene
from gungnode import GungNode, GungPlug, GungAttribute, GungEdge, GungGroup


# from random import randrange


testgung_xml = """<?xml version="1.0" ?>
<GungGraph>
    <GungNode minimalHeight="74" min_width="14" name="test9" node_height="74.0" node_id="51" node_width="100.0" \
    pos_x="945.0" pos_y="0.0">
        <GungAttribute attr_height="14" node_id="52" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="53" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="54" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="55" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="55" min_width="100.0" name="test8" node_height="55.0" node_id="50" node_width="100.0" \
    pos_x="840.0" pos_y="0.0"/>
    <GungNode minimalHeight="74" min_width="14" name="test7" node_height="74.0" node_id="45" node_width="100.0" \
    pos_x="735.0" pos_y="0.0">
        <GungAttribute attr_height="14" node_id="46" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="47" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="48" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="49" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="108" min_width="14" name="test6" node_height="108.0" node_id="36" node_width="100.0" \
    pos_x="630.0" pos_y="0.0">
        <GungAttribute attr_height="14" node_id="37" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="38" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="39" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="40" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="41" pos_x="1.0" pos_y="54.0">
            <GungPlug node_id="42" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="43" pos_x="1.0" pos_y="71.0">
            <GungPlug node_id="44" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" min_width="14" name="test5" node_height="91.0" node_id="29" node_width="100.0" \
    pos_x="525.0" pos_y="130.0">
        <GungAttribute attr_height="14" node_id="30" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="31" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="32" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="33" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="34" pos_x="1.0" pos_y="54.0">
            <GungPlug node_id="35" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" min_width="14" name="test4" node_height="91.0" node_id="22" node_width="100.0" \
    pos_x="420.0" pos_y="45.0">
        <GungAttribute attr_height="14" node_id="23" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="24" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="25" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="26" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="27" pos_x="1.0" pos_y="54.0">
            <GungPlug node_id="28" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" min_width="14" name="test3" node_height="91.0" node_id="15" node_width="100.0" \
    pos_x="315.0" pos_y="50.0">
        <GungAttribute attr_height="14" node_id="16" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="17" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="18" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="19" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="20" pos_x="1.0" pos_y="54.0">
            <GungOutPlug node_id="21" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="55" min_width="100.0" name="test2" node_height="55.0" node_id="14" node_width="100.0" \
    pos_x="210.0" pos_y="150.0"/>
    <GungNode minimalHeight="91" min_width="14" name="test1" node_height="91.0" node_id="7" node_width="100.0" \
    pos_x="105.0" pos_y="10.0">
        <GungAttribute attr_height="14" node_id="8" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="9" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="10" pos_x="1.0" pos_y="37.0">
            <GungPlug node_id="11" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="12" pos_x="1.0" pos_y="54.0">
            <GungPlug node_id="13" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
    <GungNode minimalHeight="91" min_width="14" name="test0" node_height="91.0" node_id="0" node_width="100.0" pos_x=\
    "0.0" pos_y="0.0">
        <GungAttribute attr_height="14" node_id="1" pos_x="1.0" pos_y="20.0">
            <GungPlug node_id="2" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="3" pos_x="1.0" pos_y="37.0">
            <GungOutPlug node_id="4" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
        <GungAttribute attr_height="14" node_id="5" pos_x="1.0" pos_y="54.0">
            <GungOutPlug node_id="6" plug_height="14" plug_width="14" pos_x="0.0" pos_y="0.0"/>
        </GungAttribute>
    </GungNode>
</GungGraph>
"""

testgung_xml_b = """<?xml version="1.0" ?>
<GungGraph>
    <GungNode minimalHeight="74" min_width="14" name="test9" node_height="74.0" node_id="51" node_width="100.0" pos_x=\
"945.0" pos_y="0.0">
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

    # but = QtGui.QPushButton("Print out graph", w)
    # but.clicked.connect(scene.print_graph)
    # wlyt.addWidget(but)
    
    scene.from_xml(testgung_xml_b)
#     for i in range(10):
#         node = GungNode("test%i" % i, None, scene)
#         node.setX(i * 105)
#         #a = GungAttribute(node, scene)
#         for p in range(int(randrange(0, 5))):
#             a = GungAttribute(node, scene)
#             #for p in range(int(randrange(0, 15))):
#             plug = GungPlug(a, scene)
#             a.rearrange_plugs()
#         node.rearrange_attributes()
     
#     e = GungEdge(scene=scene)
#     e.properties['itemFromId'] = 19
#     e.properties['itemToId'] = 33
#     e.reconnect_edge()
    w.show()
    
    # xml = scene.as_xml()
    # print xml.toprettyxml("    ")
    print "Started"
    app.exec_()
    sys.exit(0)
