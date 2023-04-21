import pickle

def loadFollows(mode, name):

    if type(name).__name__ == 'list':
        newSet = set()
        for file in name:
            newSet = newSet.union(load(mode=mode, file=file))
    else:
        try:
            newSet = load(mode, name)
        except:
            raise

    return newSet

def load(mode, file):

    try:
        file = open(f'{mode}/{file}.txt', 'rb')
    except:
        raise
    try:
        loaded = pickle.load(file)
        loadedSet = set(loaded)
    except:
        raise

    return loadedSet

def writeFollows(mode, file, content):

    file = open(f'{mode}/{file}.txt', 'wb')
    pickle.dump(content, file)
    file.close()
