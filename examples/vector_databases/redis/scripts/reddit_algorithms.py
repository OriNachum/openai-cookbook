import math
import time
from datetime import datetime

def calculate_hot_score(upvotes, downvotes, post_time):
    score = upvotes - downvotes
    order = log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else -1 if score < 0 else 0
    seconds = post_time - 1134028003
    return round(order + sign * seconds / 45000, 7)

def calculate_best_score(upvotes, downvotes):
    n = upvotes + downvotes
    if n == 0:
        return 0
    z = 1.96 # for 95% confidence
    p = float(upvotes) / n
    left = p + 1/(2*n)*z*z
    right = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    under = 1 + 1/n*z*z
    return (left - right) / under

# Example usage:

# posts = [
#     {'upvotes': 10, 'downvotes': 4, 'time_since_post_in_hours': 2},
#     {'upvotes': 5, 'downvotes': 1, 'time_since_post_in_hours': 0.5},
#     # add more posts/comments here
# ]

# for post in posts:
#     post_time = time.mktime(datetime.now().timetuple()) - post['time_since_post_in_hours']*60*60
#     hot_score = calculate_hot_score(post['upvotes'], post['downvotes'], post_time)
#     best_score = calculate_best_score(post['upvotes'], post['downvotes'])
#     print(f"Hot Score: {hot_score}, Best Score: {best_score}")
