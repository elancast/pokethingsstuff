import datetime
from dateutil import tz
import json
import requests

OAUTH_URI = 'https://api.twitter.com/oauth2/token'
TWITTER_URI = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

LIMIT = 20
SCREEN_NAME = 'nycpokespawn'

BAD_POKEMON = ['Vaporeon', 'Jolteon', 'Flareon', 'Chansey', 'Porygon']
GOOD_ZIPS = ['10028', '10128', '10075']

############################################################################
# Twitter API stuffs
############################################################################

def get_auth():
  r = requests.post(
    OAUTH_URI,
    headers={
      'Authorization': 'Basic ' + get_secret(),
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      },
    data={'grant_type': 'client_credentials'}
    )
  return json.loads(r.content)['access_token']

def get_secret():
  f = open('.secret', 'r')
  s = f.read().strip()
  f.close()
  return s

def get_recent_tweets():
  bearer = get_auth()
  r = requests.get(
    TWITTER_URI,
    params={'screen_name': SCREEN_NAME, 'count': LIMIT},
    headers={'Authorization': 'Bearer ' + bearer},
    )
  tweets_data = json.loads(r.content)
  return map(
    lambda data: (data['text'], get_tweet_time(data)),
    tweets_data,
    )

def get_tweet_time(data):
  dt = datetime.datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
  return dt.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

############################################################################
# Pokemon we care about
############################################################################

def is_good_tweet(text, dt):
  return '#PokemonGo' in text \
      and is_within_time(dt, text) \
      and has_text(text, GOOD_ZIPS) \
      and not has_text(text, BAD_POKEMON)

def has_text(text, arr):
  for x in arr:
    if x in text:
      return True
  return False

def is_within_time(dt, text):
  return dt_with_timezone(datetime.datetime.now()) < get_pokemon_dt(dt, text)

def get_pokemon_dt(dt, text):
  start = text.find('until ') + len('until ')
  end = text.find('.', start)
  time_str = text[start : end]

  tdy_dt = combine_date_and_time(dt, time_str)
  tmr_dt = tdy_dt + datetime.timedelta(days=1)

  tdy_dist = tdy_dt - dt
  tmr_dist = tmr_dt - dt
  zero = datetime.timedelta()
  return tdy_dt if tdy_dist < tmr_dist and tdy_dist >= zero else tmr_dt

def combine_date_and_time(date, time_str):
  fmt = '%m/%d/%Y'
  date_str = datetime.datetime.strftime(date, fmt)
  dt = datetime.datetime.strptime(date_str + ' ' + time_str, fmt + ' %I:%M:%S %p')
  return dt_with_timezone(dt)

def dt_with_timezone(dt):
  return dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzlocal())

############################################################################
# "main"
############################################################################

tweets = get_recent_tweets()
for (tweet, dt) in tweets:
  if is_good_tweet(tweet, dt):
    # OMG!
    print tweet
