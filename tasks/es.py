#connect to our cluster
from elasticsearch import Elasticsearch
import requests
import json


es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
i = 1
r = requests.get('http://swapi.co/api/people/'+ str(i))
es.index(index='sw', doc_type='people', id=i, body=json.loads(r.content))
