import unittest
from PySide import QtGui

from gungview import GungGraphicsView
from gungscene import GungScene
from gungnode import GungNode, GungPlug, GungAttribute
from PySide.QtGui import QApplication


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


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        
        self.app = QApplication([])
        self.w = QtGui.QWidget()
    
        wlyt = QtGui.QVBoxLayout()
        self.w.setLayout(wlyt)
        
        self.view = GungGraphicsView(self.w)
        wlyt.addWidget(self.view)
        self.w.show()
    
    def testCreateScene(self):
        """
        Ba
        """
        scene = GungScene(self.view)
        for i in range(10):
            node = GungNode("test%i" % i, None, scene)
            node.setX(i * 105)
            for _ in range(3):
                a = GungAttribute(node, scene)
                GungPlug(a, scene)
                a.rearrangePlugs()
            node.rearrangeAttributes()
        self.assert_(len(scene.items()) != 0, "Failed to create the scene nodes!")
        
        gungnodes = []
        for i in scene.items():
            if isinstance(i, GungNode):
                gungnodes.append(i)
                
        self.assert_(len(gungnodes) == 10, "Wrong number of created nodes!")
    
    def tearDown(self):
        self.w.close()
        self.app.quit()

if __name__ == '__main__':
    unittest.main()