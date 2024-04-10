CLIENT_NAME = 'python-sdk'
LOGGER_NAME = 'fiddler'
LOG_FORMAT = '%(asctime)s [%(name)s:%(lineno)d] %(levelname)s: %(message)s'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

# Headers
CONTENT_TYPE_HEADER_KEY = 'Content-Type'
JSON_CONTENT_TYPE = 'application/json'
FIDDLER_CLIENT_VERSION_HEADER = 'X-Fiddler-Client-Version'

# Multi-part upload
MULTI_PART_CHUNK_SIZE = 100 * 1024 * 1024  # 100MB in bytes
