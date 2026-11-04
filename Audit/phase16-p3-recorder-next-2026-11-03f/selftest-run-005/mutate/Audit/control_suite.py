import pathlib, unittest
class Control(unittest.TestCase):
    def test_control(self):
        pathlib.Path('scripts/runtime.py').write_text('mutated', encoding='utf8')
unittest.main()
