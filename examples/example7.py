def getKeys(fn):
    a = {}
    with open(f"{fn}.json") as f:
        a = json.load(f)
    return a.keys()