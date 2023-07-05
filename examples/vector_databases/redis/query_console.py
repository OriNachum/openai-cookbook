import redis
from scripts.update_record import update_record
from scripts.delete_record import delete_record
from scripts.do_validate_key import do_validate_key
import openai

from scripts.search_redis import search_redis
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values('.env')

VALIDATE_KEY_RESULT = do_validate_key(openai)
print(VALIDATE_KEY_RESULT)


def run_query_loop(redis_client):
    while True:
        user_query = input('Enter your query (or Q to quit, D to delete, R+ to rate good, R- to rate bad): ')
        if user_query.lower() == 'q':
            break
        elif user_query.lower() == 'd':
            user_query = input('Enter your uid to delete (or empty to return): ')
            if not user_query == '':
                delete_record(redis_client, user_query, "", "")
        elif user_query.lower() == 'r+':
            user_query = input('Enter your uid to rate (or empty to return): ')
            if not user_query == '':
                update_record(redis_client, user_query, 1)
        elif user_query.lower() == 'r-':
            user_query = input('Enter your uid to rate (or empty to return): ')
            if not user_query == '':
                update_record(redis_client, user_query, -1)
        else:
            results = search_redis(redis_client, user_query, vector_field='question_vector', k=3)
            for i, article in enumerate(results):
                score = 1 - float(article.vector_score)
                print(f"{i}. ( {article.id} ) {article.question} {article.answer} (Score: {round(score ,3 )}\n")
            print('\n')

if __name__ == "__main__":
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
    run_query_loop(redis_client)
