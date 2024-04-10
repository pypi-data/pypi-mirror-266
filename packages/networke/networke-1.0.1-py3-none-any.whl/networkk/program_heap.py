import heapq
from binarytree import build

class PriorityQueue:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []
    def insert(self,value):
        heapq.heappush(self.min_heap,value)
        heapq.heappush(self.max_heap,-value)
    def dequeue_min(self):
        if not self.isempty():
            min_val = heapq.heappop(self.min_heap)
            self.max_heap.remove(-min_val)
            heapq.heapify(self.max_heap)
            return min_val
    def dequeue_max(self):
        if not self.isempty():
            max_val = -heapq.heappop(self.max_heap)
            self.min_heap.remove(max_val)
            heapq.heapify(self.min_heap)
            return max_val
    def peek_min(self):
        if not self.isempty():
            return self.min_heap[0]
    def peek_max(self):
        if not self.isempty():
            return -self.max_heap[0]
    def display_min(self):
        if not self.isempty():
            tree = build(self.min_heap)
            print("Min Heap Tree")
            print(tree)
        else:
            print("Min heap tree is empty")
    def display_max(self):
        if not self.isempty():
            tree = build([-val for val in self.max_heap])
            print("Max Heap Tree")
            print(tree)
        else:
            print("Max heap tree is empty")
    def isempty(self):
        return len(self.min_heap) == 0
    def size_min(self):
        return len(self.min_heap)
    def size_max(self):
        return len(self.max_heap)
def main():
    pq = PriorityQueue()
    print("Priority Queue using Heap")
    print("\n1. Enqueue the element")
    print("2. Dequeue from Min heap")
    print("3. Dequeue from Max heap")
    print("4. Peek the min heap and max heap")
    print("5. Display the Min heap")
    print("6. Display the Max heap")
    print("7. Check if empty")
    print("8. Size of Min heap")
    print("9. Size of Max heap")
    print("10. Exit")

    while True:
        choice = int(input("Enter your choice:"))
        if choice == 1:
            value = int(input("Enter the element to enqueue"))
            pq.insert(value)
            print(f"Enqueue element {value}")
        elif choice == 2:
            min_val = pq.dequeue_min()
            if min_val is not None:
                print(f"Dequeued Element:",min_val)
            else:
                print("Min heap is empty")
        elif choice == 3:
            max_val = pq.dequeue_max()
            if max_val is not None:
                print(f"Dequeued Element:",max_val)
            else:
                print("Min heap is empty")
        elif choice == 4:
            min_val = pq.peek_min()
            max_val = pq.peek_max()
            print("The Min heap  Front element:",min_val)
            print("The Max heap  Front element:",max_val)
        elif choice == 5:
            pq.display_min()
        elif choice == 6:
            pq.display_max()
        elif choice == 7:
            if pq.isempty():
                print("Queue is empty")
            else:
                print("Queue is not empty")
        elif choice == 8:
            print("Size of Min heap:",pq.size_min())
        elif choice == 9:
            print("Size of Max heap:",pq.size_max())
        elif choice == 10:
            break
if __name__ == "__main__":
    main()
            
            
        
    
