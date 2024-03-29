import os
import time
import math

import tweepy as tw
import itertools as it
import more_itertools as mit
import multiprocess as mp
from collections import Counter
import progressbar
import pickle

from utils import authKeys, followsIO, ncr, idConvert
from utils.highscore import highscore

# SETTINGS
CORES = 2
MIN_AVGPER = 13.75
USER_MODE = True
LIVE_LOADED = False
LIST_MODE = False


def createWorkers(index, fullIterator, totalCombos):
    SUB_CORES = 8

    nestedPool = mp.Pool(processes=SUB_CORES)

    sizeOfChunk = 5000
    splitCombinations = mit.ichunked(fullIterator, sizeOfChunk)

    counter = Counter()
    hs = highscore()
    ownHs = highscore()

    indices = []
    for i in range(index, math.ceil(totalCombos / sizeOfChunk), CORES):
        indices.append(i)

    finalPackage = []
    completedCombos = 0
    pbar = progressbar.ProgressBar(maxval=int(totalCombos / CORES))
    pbar.start()
    x = 0
    for chunk in splitCombinations:
        if indices.__contains__(x):
            if len(finalPackage) <= (SUB_CORES - 1):
                finalPackage.append(chunk)
                if len(finalPackage) == SUB_CORES:
                    for count in nestedPool.imap_unordered(crunch, finalPackage):
                        counter.update(count[0])

                        for name, score in count[1].highscores.items():
                            hs.update(name, score)
                        for name, score in count[2].highscores.items():
                            ownHs.update(name, score)

                    completedCombos += sizeOfChunk * SUB_CORES
                    pbar.update(min(completedCombos, (int(totalCombos / CORES))))
                    finalPackage = []

        x += 1

    # Last Remainder Run
    for count in nestedPool.imap_unordered(crunch, finalPackage):
        counter.update(count[0])

        for name, score in count[1].highscores.items():
            hs.update(name, score)
        for name, score in count[2].highscores.items():
            ownHs.update(name, score)

    print(time.strftime("%H:%M:%S", time.gmtime(pbar.seconds_elapsed)))
    pbar.finish()

    file1 = open(f'results/counters/{index}.txt', 'wb')
    pickle.dump(counter, file1)
    file1.close()

    file2 = open(f'results/scores/{index}.txt', 'wb')
    pickle.dump(hs, file2)
    file2.close()

    file3 = open(f'results/ownscores/{index}.txt', 'wb')
    pickle.dump(ownHs, file3)
    file3.close()


def crunch(payload):
    from utils import excludes

    loadedUsers = []
    counter = Counter()
    hs = highscore()
    ownHs = highscore()

    if USER_MODE or LIST_MODE:
        loadMode = 'ids'
    else:
        loadMode = 'usr'

    for pair in payload:

        if excludes.excludedPairs.__contains__(pair):
            continue

        if not loadedUsers.__contains__(pair[0]):
            array1 = followsIO.loadFollows(mode=loadMode, name=pair[0])
            loadedUsers.append(pair[0])
            len1 = len(array1)
        if len1 == 0:
            counter.update({'empty': 1})
            continue

        array2 = followsIO.loadFollows(mode=loadMode, name=pair[1])
        len2 = len(array2)
        if len2 == 0:
            counter.update({'empty': 1})
            continue

        matches = array1.intersection(array2)
        lenm = len(matches)

        avgper = (lenm / (len1 + len2 - lenm)) * 100

        if avgper > MIN_AVGPER:
            counter.update({pair[0]: 1})
            counter.update({pair[1]: 1})

        hs.update(f'{pair[0]}/{pair[1]}', avgper)

        if 18824696 in pair:
            ownHs.update(f'{pair[0]}/{pair[1]}', avgper)

    return counter, hs, ownHs


if __name__ == '__main__':

    def main():

        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

        existingLists = []
        mainCounter = Counter()
        mainHighScore = highscore()
        mainOwnScore = highscore()

        if USER_MODE:  # Nested array will combine lists
            userList = [['DanTheFilmmaker']]
        elif LIST_MODE:
            userList = ['DUMMY_USER']
            listID = '199358900'
        else:  # Runs on all available profiles
            userList = ['DUMMY_USER']
            for filename in sorted(os.listdir("usr/")):
                if filename.endswith(".txt"):
                    username = os.path.splitext(filename)[0]
                    existingLists.append(username)

        print('Finished loading!...', len(existingLists))

        for username in userList:

            if LIVE_LOADED:
                for cursor in tw.Cursor(api.get_friend_ids, screen_name=username).pages():
                    print('main: ' + str(username) + ' / ' + str(len(cursor)))
                    existingLists += cursor
            elif LIST_MODE:
                for member in tw.Cursor(api.get_list_members, list_id=listID).items():
                    existingLists.append(member.id)
            elif USER_MODE:
                existingLists = followsIO.loadFollows(mode='usr', name=username)
                print(username, len(existingLists))

            # Main Processing
            totalCombos = ncr.ncr(len(existingLists), 2)
            print('Total Combinations: ' + str(totalCombos))

            fullCombinations = it.combinations(existingLists, 2)

            jobs = []
            for x in range(CORES):
                p = mp.Process(target=createWorkers, args=(x, fullCombinations, totalCombos,))
                jobs.append(p)
                p.start()

            for job in jobs:
                job.join()

            for r in range(CORES):
                file1 = open(f'results/counters/{r}.txt', 'rb')
                loadedCounter = pickle.load(file1)
                mainCounter.update(loadedCounter)

                file2 = open(f'results/scores/{r}.txt', 'rb')
                loadedScore = pickle.load(file2)
                for name, score in loadedScore.highscores.items():
                    mainHighScore.update(name, score)

                file3 = open(f'results/ownscores/{r}.txt', 'rb')
                loadedScore2 = pickle.load(file3)
                for name, score in loadedScore2.highscores.items():
                    mainOwnScore.update(name, score)

            with open("mainhs.txt", "w", encoding="utf-8") as text_file:
                text_file.write(str(mainHighScore))
            with open("ownhs.txt", "w", encoding="utf-8") as text_file:
                text_file.write(str(mainOwnScore))
                
            for userid, repCount in mainCounter.most_common(50):
                if userid == 'empty':
                    missRatio = repCount / totalCombos
                    missPercent = f'{missRatio:.2%}'
                    formattedCount = 'Empty Pairs // ' + str(missPercent)
                else:
                    if USER_MODE or LIST_MODE:
                        formattedCount = idConvert.convert(api, userid) + ' // ' + str(repCount)
                    else:
                        formattedCount = userid + ' // ' + str(repCount)

                print(formattedCount)

            print('')
            existingLists = []
            mainCounter.clear()
            mainHighScore = highscore()


    main()
