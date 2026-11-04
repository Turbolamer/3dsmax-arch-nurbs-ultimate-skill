import pathlib, unittest
class Control(unittest.TestCase):
    def test_control(self):
        self.skipTest('deliberate skip control')
unittest.main()
