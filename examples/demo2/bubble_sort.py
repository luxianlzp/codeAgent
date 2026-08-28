def bubble_sort(arr):
    """
    冒泡排序算法
    时间复杂度: O(n^2)
    空间复杂度: O(1)
    """
    n = len(arr)
    # 外层循环控制遍历次数
    for i in range(n):
        # 内层循环进行相邻元素比较和交换
        # 每次遍历后，最大的元素会"冒泡"到末尾
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # 交换相邻元素
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def bubble_sort_optimized(arr):
    """
    优化版冒泡排序
    如果某一轮没有发生交换，说明数组已经有序，提前退出
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # 如果没有发生交换，提前结束
        if not swapped:
            break
    return arr


if __name__ == "__main__":
    # 测试数据
    test_data = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_data}")
    
    sorted_data = bubble_sort(test_data.copy())
    print(f"排序结果: {sorted_data}")
    
    # 测试优化版本（近乎有序的数组）
    nearly_sorted = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    print(f"\n近乎有序数组: {nearly_sorted}")
    sorted_optimized = bubble_sort_optimized(nearly_sorted.copy())
    print(f"优化排序结果: {sorted_optimized}")
