import datetime
import sqlite3
import time

import numpy as np
import pandas as pd
import tweepy
from dateutil import parser
from sqlalchemy import create_engine
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


def calculate_initial_compass_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = np.radians(pointA[0])
    lat2 = np.radians(pointB[0])

    diffLong = np.radians(pointB[1] - pointA[1])

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


def writemin(min, cursor, connection):
    q = 'INSERT INTO pokemon_last_tweet VALUES (NULL,{tweetno},(CURRENT_TIMESTAMP))' \
        .format(tweetno=min)
    cursor.execute(q)
    connection.commit()


def readmin(cursor):
    q = 'SELECT latest_tweet_number FROM pokemon_last_tweet ORDER BY updated DESC'
    cursor.execute(q)
    m = int(cursor.fetchone()[0])
    return (m)


def get_filters(dbpath):
    disk_engine = create_engine('sqlite:///' + dbpath)
    q = '''
        SELECT
          person_filter_id AS person_id,
          person_name,
          lat,
          lon,
          person_phone,
          pokemon_name,
          distance_metres,
          min_iv_pct,
          pokemon_number
        FROM pokemon_pokefilter
          LEFT JOIN pokemon_person ON pokemon_pokefilter.person_filter_id = pokemon_person.id
          LEFT JOIN pokemon_location ON pokemon_person.person_location_id = pokemon_location.id
          LEFT JOIN pokemon_pokedex ON pokemon_pokefilter.poke_filter_id = pokemon_pokedex.id;
    '''
    filters = pd.read_sql_query(q, disk_engine)
    return filters


def parse_tweet_json():
    global tweets
    for tweet in a2_tweets:
        twt = pd.Series()
        twt.name = tweet.id
        twt['text'] = tweet.text
        twt['url'] = tweet.entities['urls'][0]['expanded_url']
        strang = tweet.text.split(' ')
        twt['poke_name'] = strang[0]
        twt['endtime'] = parser.parse(strang[2]).time()
        # twt['iv'] = float(strang[5].rstrip('%'))
        latlon = twt['url'].split('=')[1].split(',')
        twt['lat'] = float(latlon[0])
        twt['lon'] = float(latlon[1])
        twt['close'] = " ".join(strang[-5:])
        tweets = tweets.append(twt)

    if len(tweets) > 0:
        tweets = tweets[tweets['endtime'] > rightnow]
        writemin(tweets.index.values.max(), cursor=c, connection=conn)
        if len(tweets) > 0:
            filter_mons()


def filter_mons():
    for index, row in filters.iterrows():
        keepers = tweets.loc[(tweets['poke_name'] == row['pokemon_name']) & \
                             # (tweets['iv'] >= row['min_iv_pct']) & \
                             # filter hidden for the time being b/c Josh IV changes
                             (tweets['endtime'] > rightnow)]
        keepers['person_lat'] = row['lat']
        keepers['person_lon'] = row['lon']
        keepers['distance_m'] = haversine(keepers['person_lon'], keepers['person_lat'], keepers['lon'],
                                          keepers['lat']) * 1000
        keepers = keepers.loc[keepers['distance_m'] <= row['distance_metres']]

        if len(keepers) > 0:
            keepers['bearing'] = calculate_initial_compass_bearing((keepers['person_lat'], keepers['person_lon']),
                                                                   (keepers['lat'], keepers['lon']))
            keepers['km'] = keepers['distance_m'] / 1000
            for keeperindex, keeperrow in keepers.iterrows():
                # modified while Josh fixes the IV scanning
                # message = 'Hey, {}, there is a {:0.0f}% {} {:0.1f} km, {:0.0f} degrees from you until {:%-I:%M %p}. {}' \
                #     .format(row['person_name'], keeperrow['iv'], keeperrow['poke_name'], keeperrow['km'],
                #             keeperrow['bearing'], keeperrow['endtime'], keeperrow['url'])
                message = 'Hey, {}, there is a {} {:0.1f} km, {:0.0f} degrees from you until {:%-I:%M %p}. {}' \
                    .format(row['person_name'], keeperrow['poke_name'], keeperrow['km'],
                            keeperrow['bearing'], keeperrow['endtime'], keeperrow['url'])
                print message
                # sendSMS(message, row['person_phone'])


def sendSMS(body, tophone):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    phonestring = "+1" + str(tophone)
    message = client.messages.create(
        body=body,  # Message body
        to=phonestring,
        from_="+17345489682")
    print message.sid
    return message.sid


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
path_to_db = '../pokesite/db.sqlite3'

# here we go
try:
    while True:
        rightnow = datetime.datetime.time(datetime.datetime.now())
        print rightnow

        filters = get_filters(path_to_db)
        conn = sqlite3.connect(path_to_db)
        c = conn.cursor()

        mintweet = readmin(c)

        tweets = pd.DataFrame()
        a2_tweets = api.user_timeline(joshSpam, count=500, since_id=mintweet)

        # get them all
        # a2_tweets = api.user_timeline(joshSpam)
        parse_tweet_json()

        time.sleep(60)

except KeyboardInterrupt:
    conn.close()
    pass
