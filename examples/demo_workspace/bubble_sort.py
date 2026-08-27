def bubble_sort(arr):
    """
    冒泡排序算法
    时间复杂度: O(n^2)
    空间复杂度: O(1)
    """
    # 复制列表，避免修改原列表
    nums = arr.copy()
    n = len(nums)
    
    # 外层循环控制遍历次数
    for i in range(n):
        # 标记本轮是否发生交换
        swapped = False
        
        # 内层循环进行相邻元素比较和交换
        # 每轮结束后，最大的元素会"冒泡"到末尾
        for j in range(0, n - i - 1):
            if nums[j] > nums[j + 1]:
                # 交换相邻元素
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        
        # 如果本轮没有发生交换，说明已经有序，提前退出
        if not swapped:
            break
    
    return nums


if __name__ == "__main__":
    # 测试冒泡排序
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_array}")
    
    sorted_array = bubble_sort(test_array)
    print(f"排序后数组: {sorted_array}")
    
    # 验证原数组未被修改
    print(f"原数组保持不变: {test_array}")
