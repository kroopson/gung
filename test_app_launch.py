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

This module holds a very basic example of a working GUNG based graph window.
"""

from PySide import QtGui

from gung.gungview import GungGraphicsView
from gung.gungscene import GungScene


testgung_xml = """<?xml version="1.0" ?>
<GungGraph>
	<GungNode attributes_offset="20.0" min_height="88.0" min_width="100.0" name="test4" node_height="91.0" node_id="22" node_width="100.0" posX="409.0" pos_x="409.0" pos_y="86.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="23" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="24" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="25" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="26" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="27" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungInPlug node_id="28" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="88.0" min_width="100.0" name="test3" node_height="91.0" node_id="15" node_width="100.0" posX="558.0" pos_x="558.0" pos_y="-28.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="16" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="17" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="18" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="19" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="20" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungOutPlug node_id="21" plug_height="14.0" plug_width="14.0" posX="0.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="104.0" min_width="100.0" name="test6" node_height="108.0" node_id="36" node_width="100.0" posX="687.0" pos_x="687.0" pos_y="134.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="37" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="38" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="39" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="40" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="41" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungInPlug node_id="42" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="43" posX="0.0" pos_x="1.0" pos_y="71.0">
			<GungInPlug node_id="44" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="88.0" min_width="100.0" name="test0" node_height="91.0" node_id="0" node_width="100.0" posX="149.0" pos_x="149.0" pos_y="25.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="1" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="2" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="3" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungOutPlug node_id="4" plug_height="14.0" plug_width="14.0" posX="0.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="5" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungOutPlug node_id="6" plug_height="14.0" plug_width="14.0" posX="0.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="88.0" min_width="100.0" name="test1" node_height="91.0" node_id="7" node_width="100.0" posX="35.0" pos_x="35.0" pos_y="49.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="8" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="9" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="10" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="11" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="12" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungInPlug node_id="13" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="72.0" min_width="100.0" name="test9" node_height="74.0" node_id="51" node_width="100.0" posX="945.0" pos_x="945.0" pos_y="0.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="52" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="53" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="54" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="55" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="55.0" min_width="100.0" name="test8" node_height="55.0" node_id="50" node_width="100.0" posX="840.0" pos_x="840.0" pos_y="0.0"/>
	<GungNode attributes_offset="20.0" min_height="72.0" min_width="100.0" name="test7" node_height="74.0" node_id="45" node_width="100.0" posX="735.0" pos_x="735.0" pos_y="0.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="46" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="47" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="48" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="49" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="88.0" min_width="100.0" name="test5" node_height="91.0" node_id="29" node_width="100.0" posX="525.0" pos_x="525.0" pos_y="130.0">
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="30" posX="0.0" pos_x="1.0" pos_y="20.0">
			<GungInPlug node_id="31" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="32" posX="0.0" pos_x="1.0" pos_y="37.0">
			<GungInPlug node_id="33" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
		<GungAttribute attr_height="14.0" edge_offset="0.0" inverted="True" node_id="34" posX="0.0" pos_x="1.0" pos_y="54.0">
			<GungInPlug node_id="35" plug_height="14.0" plug_width="14.0" posX="85.0" pos_x="0.0" pos_y="0.0"/>
		</GungAttribute>
	</GungNode>
	<GungNode attributes_offset="20.0" min_height="55.0" min_width="100.0" name="test2" node_height="55.0" node_id="14" node_width="100.0" posX="210.0" pos_x="210.0" pos_y="150.0"/>
	<GungEdge item_from_id="24" item_to_id="21" node_id="59" posX="0.0" pos_x="0.0" pos_y="0.0"/>
	<GungEdge item_from_id="2" item_to_id="21" node_id="58" posX="0.0" pos_x="0.0" pos_y="0.0"/>
	<GungEdge item_from_id="6" item_to_id="11" node_id="56" posX="0.0" pos_x="0.0" pos_y="0.0"/>
	<GungEdge item_from_id="4" item_to_id="9" node_id="57" posX="0.0" pos_x="0.0" pos_y="0.0"/>
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

    scene.from_xml(testgung_xml)
    w.show()

    print "Started"
    app.exec_()
    sys.exit(0)
