class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)
        print(f"Pushed element: {item}, Stack: {self.items}")

    def pop(self):
        if self.isEmpty():
            raise Exception("Stack is empty")
        item = self.items.pop()
        print(f"Popped element: {item}, Stack: {self.items}")
        return item

    def peek(self):
        if self.isEmpty():
            raise Exception("Stack is empty")
        return self.items[-1]


def precedence(op):
    if op == "+" or op == "-":
        return 1
    elif op == "*" or op == "/":
        return 2
    else:
        return 0


def infix_to_postfix(expression):
    stack = Stack()
    postfix = ""
    i = 0
    while i < len(expression):
        if expression[i].isdigit():
            num = ""
            while i < len(expression) and expression[i].isdigit():
                num += expression[i]
                i += 1
            postfix += num
            postfix += " "
            continue
        elif expression[i] == '(':
            stack.push(expression[i])
        elif expression[i] == ')':
            while not stack.isEmpty() and stack.peek() != '(':
                postfix += stack.pop()
                postfix += " "
            stack.pop()
        else:
            while not stack.isEmpty() and precedence(stack.peek()) >= precedence(expression[i]):
                postfix += stack.pop()
                postfix += " "
            stack.push(expression[i])
        i += 1

    while not stack.isEmpty():
        postfix += stack.pop()
        postfix += " "

    return postfix


def evaluate_postfix(expression):
    stack = Stack()
    tokens = expression.split()
    for token in tokens:
        if token.isdigit():
            stack.push(int(token))
        else:
            val2 = stack.pop()
            val1 = stack.pop()
            result = eval(f"{val1}{token}{val2}")
            stack.push(result)

    return stack.pop()


expression = input("Enter an arithmetic expression: ")
postfix = infix_to_postfix(expression)
result = evaluate_postfix(postfix)
print(f"The result of the expression is: {result}")
