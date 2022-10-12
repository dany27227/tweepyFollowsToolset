import os
import tweepy as tw
import pickle
from collections import Counter

from utils import authKeys, followsIO

if __name__ == '__main__':

    def main():
        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)
        leaderboardRun(api)


def leaderboardRun(api, user=''):

    lists = []
    x = 0

    if user != '':
        userList = followsIO.loadFollows(mode='usr', file=user)
        for uid in userList:
            try:
                flist = followsIO.loadFollows(mode='ids', file=uid)
                for entry in flist:
                    lists.append(entry)
                    continue
                x = x + 1
            except:
                x = x
        print(str(x)+'/'+str(len(userList))+' Found')

    else:
        for filename in os.listdir("usr/"):
            if filename.endswith(".txt"):
                flist = followsIO.loadFollows(mode='usr', file=os.path.splitext(filename)[0])
                for entry in flist:
                    lists.append(entry)
                    continue
            else:
                continue

    print('Total aggregated follows: ' + str(len(lists)))

    counts = Counter(lists).most_common(50)

    for entry in counts:
        try:
            id = entry[0]
            user = api.get_user(user_id=id)
            print(user.screen_name+': '+str(entry[1]))
        except tw.TweepyException as e:
            print(e)

main()