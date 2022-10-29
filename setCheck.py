import os
import tweepy as tw

from utils import authKeys, followsIO

if __name__ == '__main__':

    def main():

        api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

        userList = ['sidefx', 'LupeFiasco', 'Thesixler']
        idList = []

        existingLists = []
        for filename in os.listdir('usr/'):
            if filename.endswith('.txt'):
                existingLists.append(os.path.splitext(filename)[0])

        for username in userList:
            user = api.get_user(screen_name=username)
            idList.append(user.id)

        idSet = set(idList)

        for followListFile in existingLists:
            userSet = followsIO.loadFollows(mode='usr', file=followListFile)

            matches = idSet.intersection(userSet)

            if len(matches) == len(idSet):
                print(followListFile)

    main()