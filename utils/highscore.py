import tweepy as tw
from utils import authKeys

class highscore:
    api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

    def __init__(self):
        self.highscores = {}

    def update(self, name, score):
        self.highscores[name] = score
        self.highscores = {n: s for n, s in self.highscores.items()
                           if s in sorted(self.highscores.values(), reverse=True)[:30]}

    def __str__(self):
        return '\n'.join(
            f'{self.getNames(name)}: {score}'
            for name, score in
            sorted(self.highscores.items(), key=lambda x: x[1], reverse=True)
        ) or 'No highscores!'

    def getNames(self, pair):
        ids = pair.split('/')
        names = []

        for id in ids:
            try:
                user = self.api.get_user(user_id=id)
                screenname = user.screen_name
                names.append(screenname)
            except:
                names.append('not found')

        return names
