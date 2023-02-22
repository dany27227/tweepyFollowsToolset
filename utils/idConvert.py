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
