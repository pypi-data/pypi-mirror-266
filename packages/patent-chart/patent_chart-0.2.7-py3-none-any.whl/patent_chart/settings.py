import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'careful-redis')
# TODO: should be renamed to ELASTIC_URL
ELASTIC_HOST = f"http://{os.environ.get('ELASTIC_HOST','careful-elastic')}:9200"

REDIS_OPENAI_RATE_LIMIT_LOCK_KEY = os.environ.get('REDIS_OPENAI_RATE_LIMIT_LOCK__KEY', 'openai_rate_limit_lock')

REDIS_OPENAI_RATE_LIMIT_LAST_FILL_TIME_KEY = os.environ.get('REDIS_OPENAI_RATE_LIMIT_LAST_FILL_TIME_KEY', 'openai_rate_limit_last_fill_time')

REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY = os.environ.get('REDIS_OPENAI_RATE_LIMIT_TOKENS_KEY', 'openai_rate_limit_tokens')