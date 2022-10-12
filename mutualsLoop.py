import os
import tweepy as tw
import itertools as it
import multiprocess as mp
from collections import Counter

from utils import authKeys, followsIO, ncr

# SETTINGS
CORES = 8
PROG_PERCENT = 10
MIN_AVGPER = 0.15
MIN_LENGTH = 4
MIN_RATIO = 0.33333333
USER_MODE = True
LIVE_LOADED = False
LIST_MODE = False

def crunch(payload):

    existingLists = []
    loadedUsers = []
    counter = Counter()

    if USER_MODE or LIST_MODE:
        loadMode = 'ids'
    else:
        loadMode = 'usr'

    for pair in payload:

        if not loadedUsers.__contains__(pair[0]):
            array1 = followsIO.loadFollows(mode=loadMode, file=pair[0])
            loadedUsers.append(pair[0])

        array2 = followsIO.loadFollows(mode=loadMode, file=pair[1])

        len1 = len(array1)
        len2 = len(array2)

        if len1 == 0 or len2 == 0:
            counter.update({'empty': 1})
            continue
        if len1 > len2:
            try:
                ratio = len2 / len1
            except:
                ratio = 0
        else:
            try:
                ratio = len1 / len2
            except:
                ratio = 0

        if len1 > MIN_LENGTH and len2 > MIN_LENGTH and ratio > MIN_RATIO:
            matches = array1.intersection(array2)
            lenm = len(matches)
            try:
                per1 = lenm / len1
            except:
                per1 = 0
            try:
                per2 = lenm / len2
            except:
                per2 = 0

            avgper = (per1 + per2) / 2

            if avgper > MIN_AVGPER:
                if not any([LIST_MODE, USER_MODE]):
                    print(f'{pair[0]}: {len1}//////{pair[1]}: {len2}')
                    print(f'matches: {lenm}', f'avgper: {avgper:.0%}', f'ratio: {ratio}')
                    print('')
                counter.update({pair[0]: 1})
                counter.update({pair[1]: 1})
    return counter

if __name__ == '__main__':

    def main():

        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

        existingLists = []
        loadedUsers = []
        set1 = []
        mainCounter = Counter()

        if USER_MODE:
            userList = ['sidefx']
        elif LIST_MODE:
            listID = '199358900'
            userList = ['DUMMY_USER']
        else:  # Runs on all available profiles
            userList = ['DUMMY_USER']
            for filename in os.listdir("usr/"):
                if filename.endswith(".txt"):
                    existingLists.append(filename)

        for username in userList:

            if LIVE_LOADED:
                for cursor in tw.Cursor(api.get_friend_ids, screen_name=username).pages():
                    print('main: ' + username + ' / ' + str(len(cursor)))
                    existingLists += cursor
            elif LIST_MODE:
                existingLists = []
                for member in tw.Cursor(api.get_list_members, list_id=listID).items():
                    existingLists.append(member.id)
            elif USER_MODE:
                existingLists = followsIO.loadFollows(mode='usr', file=username)
                print(username, len(existingLists))

            # Main Processing
            if CORES > 1:
                pool = mp.Pool(processes=CORES)
            combos = []
            coreCombos = []
            totalCombos = ncr.ncr(len(existingLists), 2)
            BATCH_SIZE = min(totalCombos // (PROG_PERCENT * CORES), 200000)
            completedCombos = 0

            for user, user2 in it.combinations(existingLists, 2):
                coreCombos.append((user, user2))

                if len(coreCombos) == BATCH_SIZE:
                    combos.append(coreCombos)
                    coreCombos = []
                    if len(combos) == CORES:
                        if CORES == 1:
                            newCounts = crunch(combos[0])
                            mainCounter.update(newCounts)
                        else:
                            newCounts = pool.map(crunch, combos)
                            for count in newCounts:
                                mainCounter.update(count)

                        completedCombos += BATCH_SIZE * CORES
                        print(f'{completedCombos / totalCombos:.2%}')
                        combos = []

            # Last remainder run
            combos.append(coreCombos)
            if CORES == 1:
                newCounts = crunch(combos[0])
                mainCounter.update(newCounts)
            else:
                newCounts = pool.map(crunch, combos)
                for count in newCounts:
                    mainCounter.update(count)

            for userid, repCount in mainCounter.most_common(11):
                try:
                    user = api.get_user(user_id=userid)
                    screenname = user.screen_name
                    formattedCount = screenname + ' ' + str(repCount)
                except tw.TweepyException as e:
                    missRatio = repCount / totalCombos
                    missPourcent = f'{missRatio:.2%}'
                    formattedCount = userid + ' ' + missPourcent
                print(formattedCount)

            print('')
            existingLists = []
            mainCounter.clear()

    main()


