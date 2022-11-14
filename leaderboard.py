import os
import tweepy as tw
import pickle
from collections import Counter

from utils import authKeys, followsIO

if __name__ == '__main__':

    def main():
        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)
        leaderboardRun(api, user='leighalexander')


def leaderboardRun(api, user='', listID=''):

    lists = []
    x = 0

    if listID != '':
        listMembers = []
        for member in tw.Cursor(api.get_list_members, list_id=listID).items():
            listMembers.append(member.id)
        for member in listMembers:
            try:
                flist = followsIO.loadFollows(mode='ids', file=member)
                for entry in flist:
                    lists.append(entry)
                if len(flist) > 0:
                    x = x + 1
            except:
                continue
        print(str(x) + '/' + str(len(listMembers)) + ' Found')
    elif user != '':
        userList = followsIO.loadFollows(mode='usr', file=user)
        for uid in userList:
            try:
                flist = followsIO.loadFollows(mode='ids', file=uid)
                for entry in flist:
                    lists.append(entry)
                if len(flist) > 0:
                    x = x + 1
            except:
                continue
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

    counts = Counter(lists).most_common(20)

    for entry in counts:
        try:
            id = entry[0]
            user = api.get_user(user_id=id)
            print(user.screen_name+': '+str(entry[1]))
        except tw.TweepyException as e:
            print(e)

main()