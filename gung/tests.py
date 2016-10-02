import unittest
# try:
#     from PySide.QtGui import QWidget
#     from PySide.QtGui import QVBoxLayout
#     from PySide.QtGui import QApplication
# except ImportError:
#     from PySide2.QtWidgets import QApplication
#     from PySide2.QtWidgets import QWidget
#     from PySide2.QtWidgets import QVBoxLayout
from .qt.qt_widgets import QApplication
from .qt.qt_widgets import QVBoxLayout
from .qt.qt_widgets import QWidget


from gung.gungview import GungGraphicsView
from gung.gungscene import GungScene
from gung.gungnode import GungNode, GungPlug, GungAttribute


class TestSequenceFunctions(unittest.TestCase):
    app = QApplication([])

    def setUp(self):
        
        self.w = QWidget()
    
        wlyt = QVBoxLayout()
        self.w.setLayout(wlyt)
        
        self.view = GungGraphicsView(self.w)
        wlyt.addWidget(self.view)
        self.w.show()
    
    def test_create_scene(self):
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
                a.rearrange_plugs()
            node.rearrange_attributes()
        self.assert_(len(scene.items()) != 0, "Failed to create the scene nodes!")
        
        gungnodes = []
        for i in scene.items():
            if isinstance(i, GungNode):
                gungnodes.append(i)
                
        self.assert_(len(gungnodes) == 10, "Wrong number of created nodes!")
        
    def test_save_load_xml(self):
        """
        Checks if scene serialization works fine.
        """
        scene = GungScene(self.view)
        
        nodes = []
        for i in range(1):
            node = GungNode("test%i" % i, None, scene)
            node.setX(i * 105)
            for _ in range(5):
                a = GungAttribute(node, scene)
                GungPlug(a, scene)
                a.rearrange_plugs()
            node.rearrange_attributes()
            nodes.append(node)
        
        scenexml = scene.as_xml()
        
        scene_b = GungScene(self.view)
        
        scene_b.from_xml(scenexml.toxml())
        self.assert_(scene_b.as_xml().toxml() == scenexml.toxml(), "Scene serialization failed!")

    def test_get_node_by_id(self):
        scene = GungScene(self.view)
        node = GungNode("test%i", None, scene)
        self.assert_(scene.get_item_by_id(0) == node, "Failed to get the node by Id")
        node_b = GungNode("test%i", None, scene)
        self.assert_(scene.get_item_by_id(1) == node_b, "Failed to get the second node by Id")
    
    def tearDown(self):
        self.w.close()
        self.app.quit()

if __name__ == '__main__':
    unittest.main()
