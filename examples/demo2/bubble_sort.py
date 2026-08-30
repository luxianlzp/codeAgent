def bubble_sort(arr):
    """
    冒泡排序算法实现
    时间复杂度: O(n^2)
    空间复杂度: O(1)
    """
    # 创建副本，避免修改原列表
    nums = arr.copy()
    n = len(nums)
    
    for i in range(n):
        # 标记本轮是否发生交换
        swapped = False
        
        # 每轮将最大的元素"冒泡"到末尾
        for j in range(0, n - i - 1):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        
        # 如果没有发生交换，说明已经有序，提前退出
        if not swapped:
            break
    
    return nums


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [3, -1, 0, 5, -2],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [],
        [42],
    ]
    
    for case in test_cases:
        sorted_arr = bubble_sort(case)
        print(f"原数组: {case}")
        print(f"排序后: {sorted_arr}\n")
