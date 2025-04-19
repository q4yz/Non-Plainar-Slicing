import unittest
from NonPlainarSlicing.gcode_utilities.gcode_object import GcodeObject

class MyTestCase(unittest.TestCase):
    def test_something(self):
        path = r'C:\Daten\Test-Slicer\Gcode_IN\CFFFP_out - Kopie.gcode'

        g = GcodeObject(path)

        #self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
