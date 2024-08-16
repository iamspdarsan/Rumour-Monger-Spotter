import tweepy
from credential import (access_token, access_token_secret, consumer_key,
                        consumer_secret)

# X API authorization using consumer key and consumer secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret,access_token,access_token_secret)
api = tweepy.API(auth)

def scrap(link):  
    #Extract Tweet ID
    tweetid=link[link.find('status/')+len('status/'):link.find('?')]
    
    tweet=api.get_status(tweetid)
    #print(tweet.user)
    print("\nUser ID - ",tweet.user.screen_name)#user_id
    print("Tweet content - ",tweet.text)
    
    try:
        #Extract first tag only
        tag=tweet.entities['hashtags'][0]['text']
    except IndexError:
        tag=0
    finally:
        print("Hashtag: ",tag)
    
        
    try:
        userloc=tweet.user.location
    except:
        userloc = 0
    finally:
        print("User profile location is ",userloc)

    try:
        tweetloc=tweet.place.name
    except:
        tweetloc = 0
    finally:
        print("User state is ",tweetloc)#place_dist_state

    print("Tweet posted on ",tweet.created_at)#tweet_posted_at
    print("Tweet link - ",link)

    result={
        'userid':tweet.user.screen_name,
        'username':tweet.user.name,
        'userloc':userloc,
        'createdat':tweet.created_at,
        'tweetloc':tweetloc,
        'content':tweet.text,
        'tag':tag,
    }
    return result