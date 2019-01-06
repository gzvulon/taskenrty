from pymongo import MongoClient
import pprint

client = MongoClient('mongodb://localhost:27017/')
db = client.test_database
collection = db.test_collection
import datetime
post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}
posts = db.posts
post_id = posts.insert_one(post).inserted_id
print(post_id)

from tasks.config_base import SmartField, ModelBase

class Post(ModelBase):
    author = SmartField()
    text = SmartField()
    tags = SmartField()
    date = SmartField()

np = Post()
np.author = "bla"
np.text = "tra"
np.tags = ["mongodb", "python", "pymongo"]
np.date = datetime.datetime.utcnow()
post_id = posts.insert_one(np).inserted_id
print(post_id)

pprint.pprint(list(Post.from_iter(posts.find())))
