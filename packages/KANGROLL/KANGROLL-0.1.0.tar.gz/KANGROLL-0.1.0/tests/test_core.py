import unittest
from kangroll import KangRollSet

class TestKangRollSet(unittest.TestCase):
    def test_union(self):
        set1 = KangRollSet([1, 2, 3])
        set2 = KangRollSet([3, 4, 5])
        self.assertEqual(set1.union(set2).elements, [1, 2, 3, 4, 5])

if __name__ == '__main__':
    unittest.main()
