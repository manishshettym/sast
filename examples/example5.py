def largestElemInList(l):
    inp = [int(i) for i in l]
    inp.sort(reverse=True)
    return inp[0]