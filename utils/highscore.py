import tweepy as tw
from utils import authKeys, idConvert

class highscore:
    api = tw.API(authKeys.liveHandler(), wait_on_rate_limit=True)

    def __init__(self, positions=50):
        self.highscores = {}
        self.positions = positions

    def update(self, name, score):
        self.highscores[name] = score
        self.highscores = {n: s for n, s in self.highscores.items()
                           if s in sorted(self.highscores.values(), reverse=True)[:self.positions]}

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
            if id.isnumeric():
                try:
                    names.append(idConvert.convert(self.api, id, single=True))
                except:
                    names.append('not found')
            else:
                names.append(id)

        return names
