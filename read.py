with open("exm.jpg", 'rb') as fin:
    for i in range(1, 3000):
        print(fin.read(2).hex(), end=" ")
        if i % 5 == 0:
            print()