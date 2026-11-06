import unittest
from unittest.mock import Mock, patch
from atlasagent.desktop import DesktopAdapter

class DesktopTests(unittest.TestCase):
    def make_adapter(self):
        adapter = object.__new__(DesktopAdapter)
        adapter.gui = Mock()
        adapter.gui.size.return_value = (1920, 1080)
        return adapter

    def test_observe(self):
        adapter = self.make_adapter()
        adapter.gui.position.return_value = (5, 7)
        self.assertIn("1920x1080", adapter.observe())

    def test_click_valid(self):
        adapter = self.make_adapter()
        adapter.click("500,300")
        adapter.gui.click.assert_called_once_with(x=500, y=300)

    def test_click_outside(self):
        adapter = self.make_adapter()
        with self.assertRaises(ValueError):
            adapter.click("2000,300")
        adapter.gui.click.assert_not_called()

    def test_reject_non_coordinates(self):
        adapter = self.make_adapter()
        with self.assertRaises(ValueError):
            adapter.click("Submit")

    def test_type_limit(self):
        adapter = self.make_adapter()
        with self.assertRaises(ValueError):
            adapter.type("x" * 2001)
        adapter.gui.write.assert_not_called()

    def test_scroll(self):
        adapter = self.make_adapter()
        adapter.scroll("down")
        adapter.gui.scroll.assert_called_once_with(-3)

if __name__ == "__main__":
    unittest.main()
