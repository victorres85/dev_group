import os
from settings import NEO4J_PASSWORD, NEO4J_USERNAME, NEO4J_HOST, PROTOCOL
from neo4j import GraphDatabase, BoltDriver

URI = f"{PROTOCOL}://{NEO4J_HOST}"
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

neo4j_driver =  GraphDatabase.driver(URI, auth=AUTH)
