import tweepy as tw

from utils import authKeys, followsIO

if __name__ == '__main__':

    api = tw.API(authKeys.liveHandler())

    user1 = 'leighalexander'
    user2 = 'sidefx'

    set1 = followsIO.loadFollows(mode='usr', file=user1)

    set2 = followsIO.loadFollows(mode='usr', file=user2)

    matches = set1.intersection(set2)

    print(f'{user1}: {len(set1)}//////{user2}: {len(set2)}')
    print('')
    for match in matches:
        try:
            userID = api.get_user(user_id=match)
            print(userID.screen_name+' / '+userID.name)
        except tw.TweepyException as e:
            print('Error')
