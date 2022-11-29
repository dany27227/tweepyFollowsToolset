import tweepy as tw

from utils import authKeys, followsIO

if __name__ == '__main__':

    api = tw.API(authKeys.liveHandler())

    users = ['DanTheFilmmaker', 'kendricklamar']

    for x in range(len(users) - 1):
        if x == 0:
            set1 = followsIO.loadFollows(mode='usr', name=users[x])
            set2 = followsIO.loadFollows(mode='usr', name=users[x+1])

            matches = set1.intersection(set2)
            headerString = f'{users[x]}: {len(set1)}//////{users[x+1]}: {len(set2)}//////'
        else:
            newSet = followsIO.loadFollows(mode='usr', name=users[x+1])

            matches = matches.intersection(newSet)
            headerString += f'{users[x+1]}: {len(newSet)}//////'

    print(headerString)
    print('')
    print('Matches: ' + str(len(matches)))
    for match in matches:
        try:
            userID = api.get_user(user_id=match)
            print(userID.screen_name+' / '+userID.name)
        except tw.TweepyException as e:
            print('Error')
