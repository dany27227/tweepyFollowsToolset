import os

import tweepy as tw
import multiprocess as mp

from utils import authKeys, followsIO
from utils.highscore import highscore

# SETTINGS
CORES = 16
POSITIONS = 125
LIST_MODE = False


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def crunch(payload):
    loadedUsers = []
    hs = highscore(positions=POSITIONS)

    loadMode = 'usr'

    for pair in payload:

        if not loadedUsers.__contains__(pair[0]):
            array1 = followsIO.loadFollows(mode=loadMode, name=pair[0])
            loadedUsers.append(pair[0])
            len1 = len(array1)
        if len1 == 0:
            continue

        array2 = followsIO.loadFollows(mode=loadMode, name=pair[1])
        len2 = len(array2)
        if len2 == 0:
            continue

        matches = array1.intersection(array2)
        lenm = len(matches)

        avgper = (lenm / (len1 + len2 - lenm)) * 100

        hs.update(f'{pair[0]}/{pair[1]}', avgper)

    return hs


if __name__ == '__main__':

    def main():

        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

        totalHighScore = highscore(positions=500)
        userList = ['AOC', 'Diddy']
        listIDs = ['1633574894221787145', '1633575361966489607', '1633575582645493761', '1633574252698910724']

        if LIST_MODE:
            userList = []
            for listID in listIDs:

                for member in tw.Cursor(api.get_list_members, list_id=listID).items():
                    userList.append(member.screen_name)

        # userList.remove('YtThumbnails')

        for mainUser in userList:
            existingLists = []
            mainHighScore = highscore(positions=POSITIONS)

            for filename in sorted(os.listdir("usr/")):
                if filename.endswith(".txt"):
                    username = os.path.splitext(filename)[0]
                    if username != mainUser:
                        existingLists.append((mainUser, username))

            print('Finished loading!...', mainUser, len(existingLists))

            # Main Processing

            pool = mp.Pool(processes=CORES)

            splittedLists = split(existingLists, CORES)

            crunchedScores = pool.map(crunch, splittedLists)
            for hscore in crunchedScores:

                for name, score in sorted(hscore.highscores.items(), key=lambda x: x[1], reverse=True):
                    mainHighScore.update(name, score)

            outputFile = 'results/' + mainUser + '.txt'

            with open(outputFile, "w", encoding="utf-8") as text_file:
                text_file.write(str(mainHighScore))

            for name, score in sorted(mainHighScore.highscores.items(), key=lambda x: x[1], reverse=True):
                totalHighScore.update(name, score)

        with open('results/TOTAL.txt', "w", encoding="utf-8") as text_file:
            text_file.write(str(totalHighScore))


    main()
