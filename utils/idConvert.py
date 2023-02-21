import tweepy as tw
from utils import authKeys

def convert(api, userid):
    try:
        user = api.get_user(user_id=userid)
        userString = user.screen_name + ' / ' + user.name
        return userString
    except tw.TweepyException as e:
        return 'Error'