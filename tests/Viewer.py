### Example Unit Test (tests/Viewer.py):
```python
import unittest
from NonPlainarSlicing.Viewer import Viewer

class TestViewer(unittest.TestCase):

    def setUp(self):
        self.viewer = Viewer()

    def test_initialization(self):
        self.assertIsNotNone(self.viewer.root)
        self.assertEqual(self.viewer.root.title(), "MY Slicer")

if __name__ == '__main__':
    unittest.main()