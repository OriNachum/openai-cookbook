import redis
import json

def update_record(redis_client: redis.Redis, questionId: str, vote: int, vote_reason: str = ""):
    questionId_bytes = questionId.encode('utf-8')
    id = redis_client.hget(questionId_bytes, b"id")
    if id is not None:
        old_upvotes = redis_client.hget(questionId_bytes, b"upvotes") or 0
        old_downvotes = redis_client.hget(questionId_bytes, b"downvotes") or 0

        new_upvotes = old_upvotes
        new_downvotes = old_downvotes
        if (vote < 0):
            new_downvotes = new_downvotes + 1
        if (vote > 0):
            new_downvotes = new_downvotes + 1
        
        redis_client.hset(questionId_bytes, b"upvotes", new_upvotes)
        redis_client.hset(questionId_bytes, b"downvotes", new_downvotes)

    else:
        raise Exception("Record not found")