import pickle

def loadFollows(mode, file):

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