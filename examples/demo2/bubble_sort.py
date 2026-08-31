def bubble_sort(arr):
    """
    冒泡排序算法
    时间复杂度: O(n^2)
    空间复杂度: O(1)
    """
    n = len(arr)
    # 外层循环控制遍历次数
    for i in range(n):
        # 标记本轮是否发生交换
        swapped = False
        # 内层循环进行相邻元素比较
        # 每轮结束后，最大的元素会"冒泡"到末尾
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # 交换相邻元素
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # 如果本轮没有发生交换，说明数组已有序，提前退出
        if not swapped:
            break
    return arr


if __name__ == "__main__":
    # 测试示例
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_array}")
    sorted_array = bubble_sort(test_array.copy())
    print(f"排序后数组: {sorted_array}")

    # 测试已排序数组
    already_sorted = [1, 2, 3, 4, 5]
    print(f"\n已排序数组: {already_sorted}")
    print(f"排序后数组: {bubble_sort(already_sorted.copy())}")

    # 测试逆序数组
    reverse_array = [5, 4, 3, 2, 1]
    print(f"\n逆序数组: {reverse_array}")
    print(f"排序后数组: {bubble_sort(reverse_array.copy())}")
