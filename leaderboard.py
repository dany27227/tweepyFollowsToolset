import os
import tweepy as tw
from collections import Counter

from utils import authKeys, followsIO, idConvert

if __name__ == '__main__':

    def main():
        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)
        leaderboardRun(api, user=['JordanPeele'])
        # leaderboardRun(api)


def leaderboardRun(api, user='', listID='', output=30, listLevelTwo=False):  # If not given a user/list will add up all profiles

    lists = []
    x = 0

    if listID != '':
        listMembers = []
        for member in tw.Cursor(api.get_list_members, list_id=listID).items():
            listMembers.append(member.id)
        totalLoads = len(listMembers)

        for member in listMembers:
            flist = followsIO.loadFollows(mode='ids', name=member)
            totalLoads += len(flist)
            for entry in flist:
                lists.append(entry)
                if listLevelTwo:
                    flistL2 = followsIO.loadFollows(mode='ids', name=entry)
                    for entryL2 in flistL2:
                        lists.append(entryL2)
                    if len(flistL2) > 0:
                        x = x + 1
            if len(flist) > 0:
                x = x + 1
        print(str(x) + '/' + str(totalLoads) + ' Found')

    elif user != '':
        userList = followsIO.loadFollows(mode='usr', name=user)
        for uid in userList:
            try:
                flist = followsIO.loadFollows(mode='ids', name=uid)
                for entry in flist:
                    lists.append(entry)
                if len(flist) > 0:
                    x = x + 1
            except:
                continue
        print(str(user)+': '+str(x)+'/'+str(len(userList))+' Found')

    else:
        for filename in os.listdir("usr/"):
            if filename.endswith(".txt"):
                flist = followsIO.loadFollows(mode='usr', name=os.path.splitext(filename)[0])
                for entry in flist:
                    lists.append(entry)
                    continue
                x += 1
            else:
                continue

    print('Total aggregated follows: ' + str(len(lists)))

    counts = Counter(lists).most_common(output)

    for entry in counts:
        percentage = f'{(entry[1] / x):.2%}'
        print(idConvert.convert(api, entry[0]) + ': ' + str(entry[1]) + ' / ' + percentage)


main()