def quicksort(arr,left,right):
    if left < right:
        partition_pos = partition(arr,left,right)
        print_step(arr,partition_pos,left,right)
        quicksort(arr,left,partition_pos -1)
        quicksort(arr,partition_pos + 1,right)
def partition(arr,left,right):
    i = left
    j = right - 1
    pivot = arr[right]
    while i < j:
        while i < right and arr[i] < pivot:
            i += 1
        while j > left and arr[j] >= pivot:
            j -= 1
        if i < j:
            arr[i], arr[j] = arr[j], arr[i]
    if arr[i] > pivot:
        arr[i], arr[right] = arr[right], arr[i]
    return i
def print_step(arr,pivot_index,left,right):
    pivot = arr[pivot_index]
    print(f"Pivot : {pivot}, Left: {arr[left:pivot_index]}, Right:{arr[pivot_index+1:right+1]}")

n = int(input("Enter the upper limit:"))
arr = []
for i in range(n):
    element = int(input("Enter the elements:"))
    arr.append(element)
print("Initital array:", arr)
quicksort(arr,0,len(arr)-1)
print("Sorted Array:",arr)
        
