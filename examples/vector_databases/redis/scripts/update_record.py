import redis
import json

def update_record(redis_client: redis.Redis, questionId: str, vote: int, vote_reason: str = ""):
    questionId_bytes = questionId.encode('utf-8')
    id = redis_client.hget(questionId_bytes, b"id")
    if id is not None:
        old_vote = redis_client.hget(questionId_bytes, b"vote") or 0
        old_vote_reason = redis_client.hget(questionId_bytes, b"vote_reason") or ""

        new_vote = old_vote + vote
        new_vote_reason = old_vote_reason + "; " + vote_reason
        
        redis_client.hset(questionId_bytes, b"vote", new_vote)
        redis_client.hset(questionId_bytes, b"vote_reason", new_vote_reason)
    else:
        raise Exception("Record not found")