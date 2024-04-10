def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)
n = int(input("Enter the element to get fibonacci series:"))
print("Fibonacci Series\n")
for i in range(n):
    print(fib(i),end=" ")
