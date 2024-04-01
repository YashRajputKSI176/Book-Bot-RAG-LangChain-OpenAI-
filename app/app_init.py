from flask import Flask
import logging
from dotenv import load_dotenv
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import cassio

dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
log_level = os.environ.get("LOG_LEVEL", 'INFO')
log_path = os.environ.get("LOG_path", '/var/log/cins.log')
logging.basicConfig(format='%(asctime)s %(levelname)s: %(filename)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=log_level,
                    handlers=[logging.FileHandler(log_path), logging.StreamHandler()])

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.logger = logger
app.config['SECRET_KEY'] = '10d4cc5cf9773a2867a3a1f5a01cfb8b'
app.config['WTF_CSRF_ENABLED'] = False
# CHROMA_PATH = "chroma"
DATA_PATH = "/home/yashksi176/Documents/PYTHON/knowledge-management-system/data/"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['3.110.118.148'], port=9042, auth_provider=auth_provider)
# cluster = Cluster(['127.0.0.1'], port=9042, connect_timeout=300)
session = cluster.connect()
table_name = 'vector_data'
keyspace = "ai_space"
CASSANDRA_KEYSPACE = keyspace
cassio.init(session=session, keyspace=CASSANDRA_KEYSPACE)
