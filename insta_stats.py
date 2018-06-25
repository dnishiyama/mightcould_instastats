import urllib.request, json, random, time, sys
from collections import defaultdict
from datetime import datetime, timedelta

ownerText = 'owner'
shortcodeText = 'shortcode'
timeText = 'taken_at_timestamp'

def getInstagramPosts(startTime, endTime = False, tag='mightcoulddrawtoday'):   # Need start time to say if the post if eligible 
    # Next page: https://www.instagram.com/explore/tags/mightcoulddrawtoday/?__a=1&max_id='endcursor'
    # graphql -> hashtag -> edge_hashtag_to_media ->page_info -> end_cursor
    
    raw_posts = [] #Array to hold all posts
    current_posts = []
    count = None
    end_point = ''
    step = 0

    print("Grabbing posts from online...")
    while True:
        try: 
            step += 1
            url = 'https://www.instagram.com/explore/tags/' + tag + '/?__a=1'
            if end_point: url += '&max_id=' + end_point

            print("Step: " + str(step), end='\r')

            #Get the data from the site
            raw_json = json.loads(urllib.request.urlopen(url).read().decode())

            count = raw_json['graphql']['hashtag']['edge_hashtag_to_media']['count']

            raw_posts += raw_json['graphql']['hashtag']['edge_hashtag_to_media']['edges']

            #Get the end_point, i.e. the next set of images
            end_point = raw_json['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            if not end_point: break #break if this is there isn't another endpoint
        except Exception as e:
            print(e)
            delay = 60
            print("Sleeping", delay, "seconds")
            time.sleep(60)
    print('Complete')
    
    print('Processing posts...')
    for post in raw_posts:
        if post['node'][timeText] >= startTime:
            if endTime == False or post['node'][timeText] < endTime:
                owner = post['node'][ownerText]['id']
                shortcode = post['node'][shortcodeText]
                current_posts.append({ownerText:owner, shortcodeText:shortcode})
    # print(json.dumps(all_posts,indent=2))
    total_posts=count
    
    print('Listed number of posts:', total_posts)
    print('Total captured posts:', len(raw_posts))
    print('Current captured posts:', len(current_posts))
    
    return current_posts, total_posts

def getOwnerPosts(owner, posts):
    owner_str = str(owner)
    return [post[shortcodeText] for post in posts if post[ownerText] in owner_str]

def getOwnerFrequencies(_dict, key):
    returnDict = defaultdict(int)
    for d in _dict:
        returnDict[d[key]] += 1
    return returnDict

def getEligibleOwners(owner_freq_dict, min_posts=7):
    eligible_owners = []
    for owner_id in owner_freq_dict:
        if owner_freq_dict[owner_id] >= min_posts:
            eligible_owners.append(owner_id)
    return eligible_owners

def main(tag = None, min_posts = None):
    end_date = f"{datetime.now().month}/{datetime.now().day}"
    end_date = input(f"Enter end date (first day to exclude--usually a Monday) [{end_date}]") or end_date
    end_datetime = datetime(datetime.now().year, *(int(a) for a in end_date.split('/')))
    end_time = time.mktime(end_datetime.timetuple())

    start_datetime = end_datetime - timedelta(days=7)
    start_date = f"{start_datetime.month}/{start_datetime.day}"
    start_date = input(f"Enter start date (first Monday) [{start_date}]") or start_date
    start_datetime = datetime(start_datetime.year, *(int(a) for a in start_date.split('/')))
    start_time = time.mktime(start_datetime.timetuple())
    all_posts, total_posts = getInstagramPosts(start_time, end_time)

    # Make dictionary of owners frequencies
    owner_freq_dict = getOwnerFrequencies(all_posts, ownerText)

    # Make list of eligible owners
    eligible_owners = getEligibleOwners(owner_freq_dict, min_posts=7)

    # Get the winner
    winner = random.choice(eligible_owners)

    # Get the winner's posts
    winner_posts = getOwnerPosts(winner, all_posts)

    print('Artists sharing this week: ', len(owner_freq_dict))
    print('Total posts shared this week:', len(all_posts))
    print('Total posts shared all time:', total_posts)
    print('Artists that completed the challenge:', len(eligible_owners))
    print('Winner:', winner)
    print('posts:')
    for post in winner_posts:
        print ('https://www.instagram.com/p/' + post + '/')

if __name__ == "__main__":
    args = sys.argv[1:]
    
    min_posts = args[1] if len(args) >= 2 else None
    tag = args[0] if len(args) >= 1 else None
    main(tag, min_posts)
