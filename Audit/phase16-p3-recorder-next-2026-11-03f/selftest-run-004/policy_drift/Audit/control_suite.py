import pathlib, unittest
class Control(unittest.TestCase):
    def test_control(self):
        pathlib.Path('policy.ms').write_text('mutated policy', encoding='utf8')
unittest.main()
