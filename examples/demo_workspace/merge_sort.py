def merge_sort(arr):
    """
    归并排序算法
    时间复杂度: O(n log n)
    空间复杂度: O(n)
    """
    # 复制列表，避免修改原列表
    nums = arr.copy()
    _merge_sort_helper(nums, 0, len(nums) - 1)
    return nums


def _merge_sort_helper(nums, left, right):
    """
    递归辅助函数，对 nums[left:right+1] 进行归并排序
    """
    if left < right:
        mid = (left + right) // 2
        # 分：递归排序左半部分和右半部分
        _merge_sort_helper(nums, left, mid)
        _merge_sort_helper(nums, mid + 1, right)
        # 治：合并两个有序子数组
        _merge(nums, left, mid, right)


def _merge(nums, left, mid, right):
    """
    合并两个有序子数组：nums[left:mid+1] 和 nums[mid+1:right+1]
    """
    # 创建临时数组存储两个子数组
    left_part = nums[left:mid + 1]
    right_part = nums[mid + 1:right + 1]

    i = j = 0
    k = left

    # 比较两个子数组的元素，将较小的放入原数组
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            nums[k] = left_part[i]
            i += 1
        else:
            nums[k] = right_part[j]
            j += 1
        k += 1

    # 将剩余的元素放入原数组
    while i < len(left_part):
        nums[k] = left_part[i]
        i += 1
        k += 1

    while j < len(right_part):
        nums[k] = right_part[j]
        j += 1
        k += 1


if __name__ == "__main__":
    # 测试归并排序
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_array}")

    sorted_array = merge_sort(test_array)
    print(f"排序后数组: {sorted_array}")

    # 验证原数组未被修改
    print(f"原数组保持不变: {test_array}")
    print()

    # 额外测试
    print("额外测试:")
    print(f"空数组: {merge_sort([])}")
    print(f"单元素: {merge_sort([42])}")
    print(f"已排序: {merge_sort([1, 2, 3, 4, 5])}")
    print(f"逆序: {merge_sort([5, 4, 3, 2, 1])}")
    print(f"含重复: {merge_sort([3, 1, 4, 1, 5, 9, 2, 6])}")
