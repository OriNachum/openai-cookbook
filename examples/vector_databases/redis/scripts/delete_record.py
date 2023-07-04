import redis

def delete_record(redis_client: redis.Redis, question: str, delete_reason: str, delete_owner: str):
    record = redis_client.hget("records", question)
    if record is not None:
        record = eval(record)
        record["delete_reason"] = delete_reason
        record["delete_owner"] = delete_owner
        redis_client.hdel("records", question)
    else:
        raise Exception("Record not found")
