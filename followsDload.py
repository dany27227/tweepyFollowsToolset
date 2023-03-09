import os
import time

import tweepy as tw

from utils import authKeys, followsIO, idConvert

if __name__ == '__main__':

    api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

    # SETTINGS
    GET_FOLLOW_TREE = True
    MAX_FRIENDS_COUNT = 149900
    MIN_DIFFERENCE = 12
    DIFF_CHECK = False
    LIST_MODE = False

    userList = ['AOC', 'Diddy', 'KingJames']
    listIDs = ['1633574894221787145', '1633575361966489607', '1633575582645493761', '1633574252698910724']

    if LIST_MODE:
        userList = []
        for listID in listIDs:

            for member in tw.Cursor(api.get_list_members, list_id=listID).items():
                userList.append(member.screen_name)

    for user in userList:

        x = 0

        existingLists = []
        for filename in os.listdir('usr/'):
            if filename.endswith('.txt'):
                existingLists.append(filename)

        existingIDLists = []
        for filename in os.listdir('ids/'):
            if filename.endswith('.txt'):
                existingIDLists.append(filename)

        follows = []

        try:
            follow_user = api.get_user(screen_name=user)
            friends_count = follow_user.friends_count
            userID = follow_user.id
        except tw.TweepyException as e:
            userID = user
            print(user + ': user ID not found')

        if not existingLists.__contains__(user + '.txt'):
            for cursor in tw.Cursor(api.get_friend_ids, screen_name=user).pages():
                print('main: ' + user + ' / ' + str(len(cursor)))
                follows += cursor

            followsIO.writeFollows('usr', user, follows)
            followsIO.writeFollows('ids', userID, follows)
        else:
            follows = followsIO.loadFollows(mode='usr', name=user)

            if abs(friends_count - len(follows)) > MIN_DIFFERENCE:
                follows = []
                for cursor in tw.Cursor(api.get_friend_ids, screen_name=user).pages():
                    print('main: ' + user + ' / ' + str(len(cursor)))
                    follows += cursor

                followsIO.writeFollows('usr', user, follows)
                followsIO.writeFollows('ids', userID, follows)

        if GET_FOLLOW_TREE:
            for follow in follows:

                exists = existingIDLists.__contains__(str(follow) + '.txt')

                if not DIFF_CHECK:
                    if exists:
                        x = x + 1
                        continue

                try:
                    follow_user = api.get_user(user_id=follow)
                    friends_count = follow_user.friends_count
                    username = follow_user.name
                    screen_name = follow_user.screen_name
                except tw.TweepyException as e:
                    print(e)

                if friends_count < MAX_FRIENDS_COUNT:
                    if not exists:
                        follows_sub = []
                        print(screen_name + ' not found')
                        x = x + 1

                        try:
                            for cursor in tw.Cursor(api.get_friend_ids, user_id=follow).pages():
                                print(str(x) + '/' + str(len(follows)) + ' / sub: ' + username + '//' + user + ' ' + str(len(cursor)))
                                follows_sub += cursor
                        except tw.TweepyException as e:
                            print(e)

                        followsIO.writeFollows('usr', screen_name, follows_sub)
                        followsIO.writeFollows('ids', follow, follows_sub)

                    else:
                        sub_follows = followsIO.loadFollows(mode='ids', name=follow)
                        x = x + 1

                        if abs(friends_count - len(sub_follows)) > MIN_DIFFERENCE:
                            follows_sub = []
                            print(screen_name + ': recaching')

                            try:
                                for cursor in tw.Cursor(api.get_friend_ids, user_id=follow).pages():
                                    print(str(x) + '/' + str(len(follows)) + ' / sub: ' + username + '//' + user + ' ' + str(len(cursor)))
                                    follows_sub += cursor
                            except tw.TweepyException as e:
                                print(e)

                            removed = sub_follows.difference(follows_sub)
                            added = set(follows_sub).difference(sub_follows)

                            print('______')
                            print(f'Removed: {len(removed)}')
                            if len(removed) <= (api.user_remainder / api.divider):
                                api.user_remainder = api.user_remainder - len(removed)
                                for removed_user in removed:
                                    print(idConvert.convert(api, removed_user))
                            else:
                                print('skipping removed because too many')

                            print('______')
                            print(f'Added: {len(added)}')
                            if len(added) <= (api.user_remainder / api.divider):
                                api.user_remainder = api.user_remainder - len(added)
                                for added_user in added:
                                    print(idConvert.convert(api, added_user))
                            else:
                                print('skipping added because too many')
                            print('______')

                            followsIO.writeFollows('usr', screen_name, follows_sub)
                            followsIO.writeFollows('ids', follow, follows_sub)

                else:
                    print('Skipping ' + screen_name + ': Too Many Follows!')
