import tweepy as tw


def convert(api, userid, single=False):
    try:
        user = api.get_user(user_id=userid)
        userString = user.screen_name
        if not single:
            userString += ' / ' + user.name
        return userString
    except tw.TweepyException as e:
        return 'Error'

def getId(api, screenname):
    try:
        user = api.get_user(screen_name=screenname)
        return user.id
    except tw.TweepyException as e:
        return 'Error'
