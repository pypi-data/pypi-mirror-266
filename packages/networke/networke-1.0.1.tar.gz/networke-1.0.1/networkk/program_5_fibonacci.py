def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

n = int(input("Enter the number to get fibonaaci:"))
print(f"The fibonacci number for the given {n} is :")
for i in range(n):
    print(fib(i), end = "")
