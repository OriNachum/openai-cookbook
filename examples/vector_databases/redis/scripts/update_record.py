import redis

def update_record(redis_client: redis.Redis, question: str, vote: int, vote_reason: str = ""):
    record = redis_client.hget("records", question)
    if record is not None:
        record = eval(record)
        record["vote"] = vote
        record["vote_reason"] = vote_reason
        redis_client.hset("records", question, str(record))
    else:
        raise Exception("Record not found")