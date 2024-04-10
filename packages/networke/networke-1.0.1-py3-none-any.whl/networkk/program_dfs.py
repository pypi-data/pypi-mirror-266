class Node:
    def __init__(self,value):
        self.value = value
        self.left = None
        self.right = None
class Tree:
    def __init__(self):
        self.root = None

    def insert(self,value):
        if not self.root:
            self.root = Node(value)
            print(f"Root node inserted {value}")
            return
        queue = [self.root]
        while queue:
            current  = queue.pop(0)
            if not current.left:
                current.left = Node(value)
                print(f"Node {value} inserted as Child node of {current.value} (left)")
                break
            elif not current.right:
                current.right = Node(value)
                print(f"Node {value} inserted as Child node of {current.value} (right)")
                break
            else:
                queue.append(current.left)
                queue.append(current.right)
    def inorder(self,node):
        if node:
            self.inorder(node.left)
            print(node.value,end = "")
            self.inorder(node.right)
    def preorder(self,node):
        if node:
            print(node.value,end = "")
            self.preorder(node.left)
            self.preorder(node.right)
    def postorder(self,node):
        if node:
            self.postorder(node.left)
            self.postorder(node.right)
            print(node.value,end = "")
def main():
    tree = Tree()
    print("DFS TRAVERSAL")
    print("\n1. Insert elements")
    print("2. Inorder Traversal")
    print("3. Preorder Traversal")
    print("4. PostOrder Traversal")
    print("5. Exit")
    while True:
        choice = int(input("Enter your choice:"))
        if choice == 1:
            value = input("Enter the value to insert")
            tree.insert(value)
        elif choice == 2:
            tree.inorder(tree.root)

        elif choice == 3:
            tree.preorder(tree.root)
        elif choice == 4:
            tree.postorder(tree.root)
        elif choice == 5:
            break
        else:
            print("Invalid Choice")
if __name__ == "__main__":
    main()

