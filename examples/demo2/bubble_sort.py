def bubble_sort(arr):
    """
    冒泡排序算法
    时间复杂度: O(n^2)
    空间复杂度: O(1)
    """
    n = len(arr)
    # 外层循环控制遍历次数
    for i in range(n):
        # 标记是否发生交换，用于优化
        swapped = False
        # 内层循环进行相邻元素比较
        # 每次遍历后，最大的元素会"冒泡"到末尾，所以范围逐渐减小
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # 交换相邻元素
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # 如果没有发生交换，说明数组已经有序，提前退出
        if not swapped:
            break
    return arr


if __name__ == "__main__":
    # 测试冒泡排序
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_array}")
    sorted_array = bubble_sort(test_array.copy())
    print(f"排序后数组: {sorted_array}")

    # 测试已经有序的数组
    sorted_test = [1, 2, 3, 4, 5]
    print(f"\n已排序数组: {sorted_test}")
    result = bubble_sort(sorted_test.copy())
    print(f"排序后数组: {result}")

    # 测试包含重复元素的数组
    duplicate_test = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    print(f"\n含重复元素数组: {duplicate_test}")
    result = bubble_sort(duplicate_test.copy())
    print(f"排序后数组: {result}")
