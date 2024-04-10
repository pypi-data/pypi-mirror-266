class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def isEmpty(self):
        if not self.head:
            print("List is empty")
        else:
            print("List is not empty")

    def insert_at_beginning(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        print(f"Element {data} inserted at the beginning")

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
            new_node.prev = current
        print(f"Element {data} inserted at the end")

    def insert_at_middle(self, data, position):
        if position < 0 or position > self.count():
            print("Invalid position")
            return
        elif position == 0:
            self.insert_at_beginning(data)
        else:
            new_node = Node(data)
            current = self.head
            count = 1
            while count < position  and current:
                current = current.next
                count += 1
            if current is None:
                print("Position out of range")
            else:
                new_node.next = current.next
                if current.next:
                    current.next.prev = new_node
                current.next = new_node
                new_node.prev = current
            print(f"Element {data} inserted at position {position}")

    def delete_at_beginning(self):
        if self.head is None:
            print("List is empty")
            return
        else:
            temp = self.head
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            del temp
            print("Element deleted from the beginning")

    def delete_at_end(self):
        if self.head is None:
            print("List is empty")
            return
        else:
            current = self.head
            while current.next:
                current = current.next
            if current.prev:
                current.prev.next = None
            else:
                self.head = None
            del current
            print("Element deleted from the end")

    def delete_at_middle(self, position):
        if self.head is None:
            print("List is empty")
            return
        elif position <  0 or position > self.count()-1:
            print("Invalid position")
            return
        elif position == 0:
            self.delete_at_beginning()
        else:
            current = self.head
            count = 0
            while count < position and current:
                current = current.next
                count += 1
            if current is None:
                print("Position out of range")
                return
            if current.next:
                current.prev.next = current.next
                current.next.prev = current.prev
            else:
                current.prev.next = None
            del current
            print(f"Element deleted from position {position}")

    def traverse(self):
        current = self.head
        while current:
            print()
            self.display()
            print("1. Traverse Next")
            print("2. Traverse Previous")
            print("3. Exit")
            print("Current node:", current.data)
            choice = int(input("Enter your choice: "))

            if choice == 1:
                if current.next:
                    current = current.next
                else:
                    print("There is no next node")

            elif choice == 2:
                if current.prev:
                    current = current.prev
                else:
                    print("There is no previous node")

            elif choice == 3:
                break

            else:
                print("Invalid choice")

    def search(self, data):
        current = self.head
        position = 0
        while current:
            if current.data == data:
                print(f"{data} found in the list {position}")
                return True
            current = current.next
            position += 1
        print(f"{data} not found in the list")
        return False

    def display(self):
        current = self.head
        while current:
            print(f"{current.data} <-> ", end="")
            current = current.next
        print("Null")

    def count(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count


print("\t Implement Doubly Linked List ADT")
dll = DoublyLinkedList()


print("\n1. Insert at beginning")
print("2. Insert at end")
print("3. Insert at position")
print("4. Delete at beginning")
print("5. Delete at end")
print("6. Delete at position")
print("7. IsEmpty")
print("8. Search")
print("9. Display")
print("10. Count")
print("11. Traverse")
print("12. Exit")

while True:
    choice = int(input("\nEnter your choice: "))
    if choice == 1:
        data = int(input("Enter data to insert at beginning: "))
        dll.insert_at_beginning(data)
        dll.display()
    elif choice == 2:
        data = int(input("Enter data to insert at end: "))
        dll.insert_at_end(data)
        dll.display()
    elif choice == 3:
        data = int(input("Enter data to insert: "))
        position = int(input("Enter position to insert at: "))
        dll.insert_at_middle(data, position)
        dll.display()
    elif choice == 4:
        dll.delete_at_beginning()
        dll.display()
    elif choice == 5:
        dll.delete_at_end()
        dll.display()
    elif choice == 6:
        position = int(input("Enter position to delete from: "))
        dll.delete_at_middle(position)
        dll.display()
    elif choice == 7:
        dll.isEmpty()
    elif choice == 8:
        data = int(input("Enter data to search: "))
        dll.search(data)
    elif choice == 9:
        dll.display()
    elif choice == 10:
        count = dll.count()
        print("Number of nodes in the list:", count)
    elif choice == 11:
        dll.traverse()
    elif choice == 12:
            break
    else:
        print("Invalid choice. Please try again.")
