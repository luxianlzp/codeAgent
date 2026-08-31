import unittest
from bubble_sort import bubble_sort


class TestBubbleSort(unittest.TestCase):
    """测试冒泡排序函数"""

    def test_normal_array(self):
        """测试普通无序数组"""
        arr = [64, 34, 25, 12, 22, 11, 90]
        expected = [11, 12, 22, 25, 34, 64, 90]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_already_sorted(self):
        """测试已排序数组"""
        arr = [1, 2, 3, 4, 5]
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_reverse_sorted(self):
        """测试逆序数组"""
        arr = [5, 4, 3, 2, 1]
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_empty_array(self):
        """测试空数组"""
        arr = []
        expected = []
        self.assertEqual(bubble_sort(arr), expected)

    def test_single_element(self):
        """测试单元素数组"""
        arr = [42]
        expected = [42]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_duplicate_elements(self):
        """测试包含重复元素的数组"""
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        expected = [1, 1, 2, 3, 4, 5, 5, 6, 9]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_negative_numbers(self):
        """测试包含负数的数组"""
        arr = [-3, -1, -7, 0, 2, -5]
        expected = [-7, -5, -3, -1, 0, 2]
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_in_place_sort(self):
        """测试原地排序（函数返回的引用是否与传入的一致）"""
        arr = [3, 1, 2]
        result = bubble_sort(arr)
        self.assertIs(result, arr)
        self.assertEqual(arr, [1, 2, 3])

    def test_large_random_array(self):
        """测试大规模随机数组，与 Python 内置排序对比"""
        import random
        random.seed(0)
        arr = [random.randint(-1000, 1000) for _ in range(200)]
        expected = sorted(arr)
        self.assertEqual(bubble_sort(arr.copy()), expected)

    def test_all_same_elements(self):
        """测试所有元素相同的数组"""
        arr = [7, 7, 7, 7, 7]
        expected = [7, 7, 7, 7, 7]
        self.assertEqual(bubble_sort(arr.copy()), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
