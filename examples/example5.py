def largestElemInFile(file: str):
    with open(file) as fp:
        line = fp.read()

    inp = line.split()
    inp = [int(i) for i in line]

    inp.sort(reverse=True)
    return inp[0]