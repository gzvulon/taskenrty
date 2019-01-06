# from pathlib import Path
from refstore.ufs import ufs, UniPath
from pathlib import Path
import fire
import fnmatch
import platform

SKIP = ['roeix', 'roeix']
from config_base import SmartField, ModelBase
from bson.objectid import ObjectId

class FileRef(ModelBase):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if self.get('hostname', None) is None:
            self.hostname = platform.node()

    tag = SmartField()
    uri = SmartField()
    ref_uri = SmartField()
    hostname = SmartField()

# def iter_files(path='/Users/ivanne', pattern='*.jpg'):
#     pp = UniPath(path)
#     for file in pp.rglob(pattern):
#         try:
#             s = str(file)
#             yield s
#         except:
#             pass

def iter_files(root_dir='/Users/ivanne/Documents', pattern='*.jpg'):
    import os
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            if fnmatch.fnmatch(path, pattern):
                yield path


def index_files(file_iter=None, dest='/Users/ivanne/mlg_index'):
    dest_p = Path(dest)
    dest_p.mkdir(exist_ok=True, parents=True)
    file_iter = file_iter or iter_files()
    count = 0
    suffix = '.json'
    for fpath in file_iter:
        count += 1
        print(count, fpath)
        if fpath.startswith('/'):
            fpath = fpath[1:]
        ref_path = dest_p / (fpath + suffix)
        file_ref_content = FileRef(uri=f"file:///{ref_path}", ref_uri=f"{ref_path}")
        UniPath(ref_path).any_write(file_ref_content)
        print(f"written to  {ref_path}")
    print(f"found {count} files")


def iter_index():
    fiter = iter_files(root_dir='/Users/ivanne/mlg_index/',
                       pattern='*.jpg.json')
    for fpath in fiter:
        print("fpath")

def iter_mongo():
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mydb
    collection = db.jpg_coll
    frefs = db.file_refs
    # pprint.pprint(list()
    for fref in frefs.find():
        yield fref['uri']
    # yield from Post.from_iter(posts.find())

def show(finder='jpg', method=print):
    if finder == 'jpg':
        fiter = iter_files()
        # params = dict(
        #     root_dir='/Users/ivanne/Documents',
        #     pattern='*.jpg')
    elif finder == 'mongo':
        fiter = iter_mongo()

    else:
        fiter = iter_files(
            root_dir = '/Users/ivanne/mlg_index/',
            pattern='*.jpg.json')
    # fiter = iter_files(*params)
    for fpath in fiter:
        method(fpath)


def index_to_mongo():
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mydb
    collection = db.jpg_coll
    frefs = db.file_refs

    fiter = iter_files(
        root_dir = '/Users/ivanne/mlg_index/',
        pattern='*.jpg.json')
    # fiter = iter_files(*params)
    for fpath in fiter:
        ref_content = FileRef.from_json(fpath)
        # ref_content['_id'] = ObjectId(ref_content.uri),
        rid = frefs.insert_one(ref_content).inserted_id
        print(rid)

# python myindex.py index_files  1.24s user 0.45s system 76% cpu 2.200 total
# python myindex.py index_files  1.25s user 0.41s system 78% cpu 2.107 total
# python myindex.py show png  0.29s user 0.07s system 70% cpu 0.524 total
# python myindex.py show  1.05s user 0.36s system 95% cpu 1.481 total

if __name__ == "__main__":
    # df = {
    #     index_files.__name__: index_files
    # }
    fire.Fire()