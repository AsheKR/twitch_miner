import json

from actor.twitch import mine

if __name__ == "__main__":
    mine(json.dumps(raw_channels), json.dumps(raw_cookies))
