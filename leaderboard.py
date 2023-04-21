import os
import tweepy as tw
from collections import Counter

from utils import authKeys, followsIO, idConvert

if __name__ == '__main__':

    def main():
        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)
        # leaderboardRun(api, listID=199358900)
        # leaderboardRun(api)
        leaderboardRun(api, users=['DanTheFilmmaker'], levelTwo=True)

def leaderboardRun(api, users=[], listID='', levelOne=True, levelTwo=False):  # If not given a user/list will add up all profiles

    lists = Counter()
    loads = 0
    totalLoads = 0

    if listID != '':
        for member in tw.Cursor(api.get_list_members, list_id=listID).items():
            users.append(member.id)
        loadMode = 'ids'

    elif users != '':
        if type(users).__name__ == 'list':
            loadMode = 'usr'

    else:
        for filename in os.listdir("usr/"):
            if filename.endswith(".txt"):
                users.append(filename)
        loadMode = 'usr'

    for name in users:
        try:
            userList = followsIO.loadFollows(mode=loadMode, name=name)
        except:
            continue
        loads += 1

        for uid in userList:
            lists.update({uid: 1})

        if levelOne:
            for uid in userList:
                try:
                    flist = followsIO.loadFollows(mode='ids', name=uid)
                except:
                    continue
                loads += 1

                for entry in flist:
                    lists.update({entry: 1})

                if levelTwo:
                    for entry in flist:
                        try:
                            flistL2 = followsIO.loadFollows(mode='ids', name=entry)
                        except:
                            continue
                        loads += 1

                        for entryL2 in flistL2:
                            lists.update({entryL2: 1})

                    totalLoads += len(flist)
            totalLoads += len(userList)
    totalLoads += len(users)

    print(str(loads) + '/' + str(totalLoads) + ' Found')

    print('Total aggregated follows: ' + str(sum(lists.values())))

    for entry in lists.most_common(34):
        percentage = f'{(entry[1] / loads):.2%}'
        print(idConvert.convert(api, entry[0]) + ': ' + str(entry[1]) + ' / ' + percentage)

main()
