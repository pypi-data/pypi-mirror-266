def asc_desc(n):
    if n > 0 :
        print(n, end = "")
        asc_desc(n-1)
        print(n,end = "")

n = int(input("Enter the Natural Number:"))
print("The Ascending and Descending order are:")
asc_desc(n)
