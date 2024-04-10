class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def display(self):
        print("\nLinked List:")
        current = self.head
        while current:
            print(current.data, end="->")
            current = current.next
        print("Null")

    def insert_at_begin(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def insert_at_position(self, data, position):
        if position == 0:
            self.insert_at_begin(data)
            return
        current = self.head
        for _ in range(position - 1):
            if current is None:
                print("Invalid Position")
                return
            current = current.next
        if current is None:
            print("Invalid Position")
            return
        new_node = Node(data)
        new_node.next = current.next
        current.next = new_node

    def delete_at_begin(self):
        if self.head is None:
            print("List is empty")
            return
        self.head = self.head.next

    def delete_at_end(self):
        if self.head is None:
            print("List is empty")
            return
        if self.head.next is None:
            self.head = None
            return
        second_last = self.head
        while second_last.next.next:
            second_last = second_last.next
        second_last.next = None

    def delete_at_position(self, position):
        if position == 0:
            if self.head is None:
                print("List is empty")
                return
            self.head = self.head.next
            return
        current = self.head
        for _ in range(position - 1):
            if current is None:
                print("Invalid Position")
                return
            current = current.next
        if current is None or current.next is None:
            print("Invalid Position")
            return
        current.next = current.next.next

    def search(self, data):
        current = self.head
        position = 0
        while current:
            if current.data == data:
                print(f"Element {data} found at position {position}")
                return
            current = current.next
            position += 1
        print(f"Element {data} not found in list")

    def countof(self):
        current = self.head
        c = 0
        while current:
            c += 1
            current = current.next
        print("No of Nodes", c)

linked_list = LinkedList()
print("\n\t Linked List Basic Operations")
print("\t ")
while True:
    print("\n1. Insert at Beginning")
    print("2. Insert at End")
    print("3. Insert at position")
    print("4. Delete at Beginning")
    print("5. Delete at End")
    print("6. Delete at position")
    print("7. Search")
    print("8. Display")
    print("9. Count of Nodes")
    print("10. Exit\n")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        data = int(input("Enter data to insert at the Beginning: "))
        linked_list.insert_at_begin(data)
        linked_list.display()
    elif choice == 2:
        data = int(input("Enter data to insert at the End: "))
        linked_list.insert_at_end(data)
        linked_list.display()
    elif choice == 3:
        data = int(input("Enter data to insert: "))
        position = int(input("Enter position to insert: "))
        linked_list.insert_at_position(data, position)
        linked_list.display()
    elif choice == 4:
        linked_list.delete_at_begin()
        linked_list.display()
    elif choice == 5:
        linked_list.delete_at_end()
        linked_list.display()
    elif choice == 6:
        position = int(input("Enter position to delete: "))
        linked_list.delete_at_position(position)
        linked_list.display()
    elif choice == 7:
        data = int(input("Enter data to search: "))
        linked_list.search(data)
    elif choice == 8:
        linked_list.display()
    elif choice == 9:
        linked_list.countof()
    elif choice == 10:
        break
    else:
        print("Invalid Choice")
