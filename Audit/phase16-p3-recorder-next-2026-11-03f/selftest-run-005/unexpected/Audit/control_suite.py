import pathlib, unittest
class Control(unittest.TestCase):
    @unittest.expectedFailure
    def test_control(self):
        self.assertEqual(2 + 2, 4)
unittest.main()
