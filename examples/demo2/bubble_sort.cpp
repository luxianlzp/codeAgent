#include <iostream>
#include <vector>

// 冒泡排序（带优化：若一轮无交换则提前结束）
void bubbleSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        bool swapped = false;
        for (int j = 0; j < n - 1 - i; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        // 如果这一轮没有发生交换，说明已经有序
        if (!swapped) break;
    }
}

void printArray(const std::vector<int>& arr) {
    for (int num : arr) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
}

int main() {
    std::vector<int> arr = {64, 34, 25, 12, 22, 11, 90};

    std::cout << "原始数组: ";
    printArray(arr);

    bubbleSort(arr);

    std::cout << "排序后数组: ";
    printArray(arr);

    return 0;
}
