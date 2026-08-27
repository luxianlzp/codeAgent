def quick_sort(arr):
    """快速排序主函数"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(arr, low=0, high=None):
    """原地快速排序"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quick_sort_inplace(arr, low, pi - 1)
        quick_sort_inplace(arr, pi + 1, high)
    return arr


def partition(arr, low, high):
    """分区函数"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


if __name__ == "__main__":
    # 测试
    test_arr = [64, 34, 25, 12, 22, 11, 90, 22]
    print("原始数组:", test_arr)
    print("快速排序(新数组):", quick_sort(test_arr))
    
    test_arr2 = [64, 34, 25, 12, 22, 11, 90, 22]
    quick_sort_inplace(test_arr2)
    print("快速排序(原地):", test_arr2)
