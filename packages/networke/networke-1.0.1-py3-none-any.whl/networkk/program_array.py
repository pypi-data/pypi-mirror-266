def input_array(length):
    arr = []
    for i in range(length):
        element = int(input(f"Enter the element {i+1}:"))
        arr.append(element)
    return arr

def insert_at(arr,element,index):
    if index < 0 or index > len(arr):
        print("Invalid Index")
        return arr
    else:
        new_arr = []
        for i in range(len(arr)+1):
            if i == index:
                new_arr.append(element)
            if i < len(arr):
                new_arr.append(arr[i])
        return new_arr
def delete_at(arr,index):
    if index < 0 or index >= len(arr):
        print("Invalid Index")
        return arr
    else:
        new_arr = []
        for i in range(len(arr)):
            if i != index:
                new_arr.append(arr[i])
        return new_arr
def search(arr,ele):
    for i in range(len(arr)):
        if arr[i] == ele:
            return i
    return -1
def update_at(arr,element,index):
    if index < 0 or index > len(arr):
        print("Invalid Index")
        return arr
    else:
        new_arr = []
        for i in range(len(arr)):
            if i != index:
                new_arr.append(arr[i])
            else:
                new_arr.append(element)
        return new_arr
def traverse(arr):
    for i in range(len(arr)):
        print(arr[i],end= "")


def main():
    n = int(input("Enter the array limit:"))
    array = input_array(n)
    print(array)
    while True:
        print("\n1. Insert an element")
        print("2. Delete an element")
        print("3. Search an element")
        print("4. Update an element")
        print("5. Traverse an element")
        print("6. Exit")
        choice = int(input("Enter your choice:"))
        if choice == 1:
            element = int(input("Enter the element to insert:"))
            index = int(input("Enter the index to insert the element:"))
            array = insert_at(array,element,index)
            print(array)
        elif choice == 2:
            index = int(input("Enter the index to delete an element:"))
            array = delete_at(array,index)
            print(array)
        elif choice == 3:
            element = int(input("Enter the element ot search:"))
            index = search(array,element)
            if index != -1:
                print(f"Element found at location {index}")
            else:
                print("Element not found")
        elif choice == 4:
            element = int(input("Enter the new element:"))
            index = int(input("Enter the index to insert the element:"))
            array = update_at(array,element,index)
            print(array)
        elif choice == 5:
            traverse(array)
        elif choice == 6:
            break
        else:
            print("Invalid Choice")
if __name__ == "__main__":
    main()
    
    
    
    
