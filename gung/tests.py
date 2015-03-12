import unittest
from PySide import QtGui

from gungview import GungGraphicsView
from gungscene import GungScene
from gungnode import GungNode, GungPlug, GungAttribute
from PySide.QtGui import QApplication



class TestSequenceFunctions(unittest.TestCase):
    app =QApplication([]) 

    def setUp(self):
        
        self.w = QtGui.QWidget()
    
        wlyt = QtGui.QVBoxLayout()
        self.w.setLayout(wlyt)
        
        self.view = GungGraphicsView(self.w)
        wlyt.addWidget(self.view)
        self.w.show()
    
    def testCreateScene(self):
        """
        Checks if scene creation works fine.
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
        
    def testSaveLoadXML(self):
        """
        Checks if scene serialization works fine.
        """
        scene = GungScene(self.view)
        for i in range(1):
            node = GungNode("test%i" % i, None, scene)
            node.setX(i * 105)
            for _ in range(5):
                a = GungAttribute(node, scene)
                GungPlug(a, scene)
                a.rearrangePlugs()
            node.rearrangeAttributes()
        
        gungnodes = []
        for i in scene.items():
            if isinstance(i, GungNode):
                gungnodes.append(i)
        
        scenexml = scene.asXml()
        
        sceneB = GungScene(self.view)
        
        sceneB.fromXml(scenexml.toxml())
        self.assert_(sceneB.asXml().toxml() == scenexml.toxml(), "Scene serialization failed!")
    
    def tearDown(self):
        self.w.close()
        self.app.quit()

if __name__ == '__main__':
    unittest.main()