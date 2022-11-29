import pickle

def loadFollows(mode, name):

    if type(name).__name__ == 'list':
        newSet = set()
        for file in name:
            newSet = newSet.union(load(mode=mode, file=file))
    else:
        newSet = load(mode, name)

    return newSet

def load(mode, file):

    try:
        file = open(f'{mode}/{file}.txt', 'rb')
    except:
        file = []
    try:
        loaded = pickle.load(file)
    except:
        loaded = []
    loadedSet = set(loaded)

    return loadedSet

def writeFollows(mode, file, content):

    file = open(f'{mode}/{file}.txt', 'wb')
    pickle.dump(content, file)
    file.close()
