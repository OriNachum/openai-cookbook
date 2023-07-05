import redis

def delete_record(redis_client: redis.Redis, questionId: str, delete_reason: str, delete_owner: str):
    questionId_bytes = questionId.encode('utf-8')
    record = redis_client.hget(questionId_bytes, b"id")
    if record is not None:
        # record = eval(record)
        # record["delete_reason"] = delete_reason
        # record["delete_owner"] = delete_owner
        redis_client.delete(questionId_bytes)
    else:
        raise Exception("Record not found")
