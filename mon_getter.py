import datetime
import time

import mysql.connector
import numpy as np
import pandas as pd
import tweepy
from dateutil import parser
from sqlalchemy import *
from twilio.rest import Client

pd.options.mode.chained_assignment = None  # suppress warnings about copy of slice


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def calculate_initial_compass_bearing(point_a, point_b):
    if (type(point_a) != tuple) or (type(point_b) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = np.radians(point_a[0])
    lat2 = np.radians(point_b[0])

    diffLong = np.radians(point_b[1] - point_a[1])

    x = np.sin(diffLong) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1)
                                       * np.cos(lat2) * np.cos(diffLong))

    initial_bearing = np.arctan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180 to + 180 which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def writemin(last_tweet):
    conn = mysql.connector.Connect(user=user, password=pw, host=host, database=db)
    cursor = conn.cursor()
    print last_tweet
    q = 'INSERT INTO arfenarf_pokemon.last_tweet VALUES ({tweetno},(CURRENT_TIMESTAMP))'.format(tweetno=last_tweet)
    cursor.execute(q)
    conn.commit()
    conn.close()


def readmin():
    conn = mysql.connector.Connect(user=user, password=pw, host=host, database=db)
    cursor = conn.cursor()
    q = 'SELECT latest_tweet_number FROM arfenarf_pokemon.last_tweet ORDER BY updated DESC LIMIT 1'
    cursor.execute(q)
    m = cursor.fetchone()[0]
    conn.close()
    return m


def get_filters():
    engine = create_engine('mysql+mysqlconnector://{}:{}@{}/{}'.format(user, pw, host, db))
    enconn = engine.connect()
    q = '''
        SELECT
          people.person_id,
          person_name,
          lat,
          lon,
          phone,
          pokemon_name,
          max_dist_km,
          min_iv_pct,
          pokedex.pokemon_num
        FROM arfenarf_pokemon.poke_filters
          LEFT JOIN arfenarf_pokemon.people ON arfenarf_pokemon.poke_filters.person_id = arfenarf_pokemon.people.person_id
          LEFT JOIN arfenarf_pokemon.user_locations ON arfenarf_pokemon.people.location_id = arfenarf_pokemon.user_locations.location_id
          LEFT JOIN arfenarf_pokemon.pokedex ON arfenarf_pokemon.poke_filters.pokemon_id = arfenarf_pokemon.pokedex.pokedex_id;
    '''
    f = pd.read_sql_query(q, engine)
    enconn.close()
    return f

def parse_tweet_json():
    global tweets
    tweets = pd.DataFrame()
    for tweet in a2_tweets:
        # try:
        twt = pd.Series()
        twt.name = tweet.id
        twt['text'] = tweet.text
        twt['url'] = tweet.entities['urls'][0]['expanded_url']
        strang = tweet.text.split(' ')
        twt['poke_name'] = strang[0]
        twt['endtime'] = parser.parse(strang[2])
        twt['endtime'] = pd.to_datetime(twt['endtime'])
        if (rightnow.hour == 23) and (twt['endtime'].hour == 0):
            twt['endtime'] = twt['endtime'] + datetime.timedelta(days=1)
        print twt['poke_name'], twt['endtime']
        if len(strang) < 14:
            twt['iv'] = 0
        else:
            twt['iv'] = float(strang[7].rstrip('%'))
        latlon = twt['url'].split('=')[1].split(',')
        twt['lat'] = float(latlon[0])
        twt['lon'] = float(latlon[1])
        twt['close'] = " ".join(strang[-5:])
        print twt
        tweets = tweets.append(twt)
        # except:
        #     print("ERROR: " + str(tweet.id))
        #    pass

    if len(tweets) > 0:
        tweets = tweets[tweets['endtime'] > rightnow]
        if len(tweets) > 0:
            writemin(tweets.index.values.max())
            filter_mons()


def filter_mons():
    for index, row in filters.iterrows():
        keepers = tweets.loc[(tweets['poke_name'] == row['pokemon_name']) & \
                             (tweets['iv'] >= row['min_iv_pct']) & \
                             (tweets['endtime'] > rightnow)]
        # TODO Add ability to shut down for a period of time
        keepers['person_lat'] = row['lat']
        keepers['person_lon'] = row['lon']
        keepers['distance_km'] = haversine(keepers['person_lon'], keepers['person_lat'], keepers['lon'],
                                           keepers['lat'])
        keepers = keepers.loc[keepers['distance_km'] <= row['max_dist_km']]

        if len(keepers) > 0:
            keepers['bearing'] = calculate_initial_compass_bearing((keepers['person_lat'], keepers['person_lon']),
                                                                   (keepers['lat'], keepers['lon']))
            for keeperindex, keeperrow in keepers.iterrows():
                # modified while Josh fixes the IV scanning
                # message = 'Hey, {}, there is a {:0.0f}% {} {:0.1f} km, {:0.0f} degrees from you until {:%-I:%M %p}. {}' \
                #     .format(row['person_name'], keeperrow['iv'], keeperrow['poke_name'], keeperrow['km'],
                #             keeperrow['bearing'], keeperrow['endtime'], keeperrow['url'])
                message = 'Hey, {}, there is a {} {:0.1f} km, {:0.0f} degrees from you until {:%-I:%M %p}. {}' \
                    .format(row['person_name'], keeperrow['poke_name'], keeperrow['distance_km'],
                            keeperrow['bearing'], keeperrow['endtime'], keeperrow['url'])
                print message
                send_sms(message, row['phone'])


def send_sms(body, tophone):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    phonestring = "+1" + str(tophone)
    message = client.messages.create(
        body=body,  # Message body
        to=phonestring,
        from_="+17345489682")
    print message.sid
    return message.sid


## Setup
## TODO set this up to be read from elsewhere

# twitter
consumer_key = 'rlZxnTU2fSNi67pqLjzv2yKMA'
consumer_secret = 'hEsNI7KiIjN99DUKLX912Yddxdockm7hIzxaf5lhTRnEyu5YnI'
access_token = '17069809-CIXsnhB4KapZZ48PXTzw5KoHStgxS2BfnyHVi5UCY'
access_token_secret = 'hoXOrQtWQslU7TMO8uLgJ2czOlXWEXLh4dCjOFBgjLh5n'
joshSpam = 811392081390342145

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# twilio
ACCOUNT_SID = 'ACb9affdbc738e9f8e2c7a6ad54da4cb08'
AUTH_TOKEN = 'e3b93d1c200c0ccd330b4565425d1fa9'

# database
# conn = mysql.connector.connect(user='pokeuser', password = 'poke-poker', host='127.0.0.1',database = 'pokemon')
# c = conn.cursor()
user = 'arfenarf_pokeuse'
pw = '2szTpHMthKN.'
db = 'arfenarf_pokemon'
host = 'kateweber.com'

# here we go
try:
    while True:
        rightnow = datetime.datetime.now()
        print rightnow

        filters = get_filters()

        mintweet = readmin()

        a2_tweets = api.user_timeline(joshSpam, count=500, since_id=mintweet)

        # get them all
        # a2_tweets = api.user_timeline(joshSpam)
        parse_tweet_json()

        time.sleep(60)

except KeyboardInterrupt:
    pass
