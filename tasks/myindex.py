# from pathlib import Path
from refstore.ufs import ufs, UniPath
from pathlib import Path
import fire
import fnmatch
import platform
import humanize
import datetime
SKIP = ['roeix', 'roeix']
from config_base import SmartField, ModelBase
from bson.objectid import ObjectId
import logging

class FileRef(ModelBase):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if self.get('hostname', None) is None:
            self.hostname = platform.node()

    tag = SmartField()
    uri: str = SmartField()
    ref_uri = SmartField()
    hostname = SmartField()
    # props = SmartField()

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
    import time
    dest_p = Path(dest)
    dest_p.mkdir(exist_ok=True, parents=True)
    file_iter = file_iter or iter_files()
    count = 0
    suffix = '.json'
    start = time.time()
    for fpath in file_iter:
        count += 1
        print(count, fpath)
        if fpath.startswith('/'):
            fpath = fpath[1:]
        ref_path = dest_p / (fpath + suffix)
        file_ref_content = FileRef(uri=f"file:///{fpath}", ref_uri=f"{ref_path}")
        UniPath(ref_path).any_write(file_ref_content)
        print(f"written to  {ref_path}")
    end = time.time()
    # hm = humanize.naturaldelta(datetime.timedelta(seconds=end -start ))
    print(f"processed {count} files in {end -start}")


def iter_index():
    fiter = iter_files(root_dir='/Users/ivanne/mlg_index/',
                       pattern='*.jpg.json')
    for fpath in fiter:
        print("fpath")

def iter_mongo_objs():
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mydb
    collection = db.jpg_coll
    frefs = db.file_refs
    # pprint.pprint(list()
    for fref in frefs.find():
        yield fref

def iter_mongo():
    for fref in iter_mongo_objs():
        yield fref['uri']

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
        # rid = frefs.update_one(ref_content).inserted_id
        rid = frefs.find_one_and_update({"uri": ref_content['uri']},
                                    {"$set": ref_content},
                                    upsert=True)
        print(rid)

# python myindex.py index_files  1.24s user 0.45s system 76% cpu 2.200 total
# python myindex.py index_files  1.25s user 0.41s system 78% cpu 2.107 total
# python myindex.py show png  0.29s user 0.07s system 70% cpu 0.524 total
# python myindex.py show  1.05s user 0.36s system 95% cpu 1.481 total




class FileProps(ModelBase):
    size = SmartField()

class Props(ModelBase):
    file: FileProps = SmartField()

def _update_props(doc, frefs):
    import os
    fr = FileRef(doc)
    uri = fr.uri.split('file://')[1]
    size = os.path.getsize(uri)
    props = Props(file=FileProps(size=size))
    frefs.find_one_and_update({"_id": doc['_id']},
                                     {"$set": {"props": props}})
    print (humanize.naturalsize(size))

def old_mongo_update():
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mydb
    collection = db.jpg_coll
    frefs = db.file_refs
    for doc in iter_mongo_objs():
        _update_props(doc, frefs)



from mongoengine import *

_hostname = platform.node()

connect('project1', host=f'mongodb://localhost/{_hostname}')

class FileRefDoc(DynamicDocument):
    tag = StringField()
    uri: str = StringField(primary_key=True, required=True)
    ref_uri = StringField()
    hostname = StringField()



def engine_to_mongo():
    fiter = iter_files(
        root_dir = '/Users/ivanne/mlg_index/',
        pattern='*.jpg.json')

    for fpath in fiter:
         fref_content = FileRef.from_json(fpath)
         doc = FileRefDoc(**fref_content)
         doc.save()

class FileInfoDoc(DynamicDocument):
    uri: str = StringField(primary_key=True, required=True)
    size = IntField()

    def update_file_size(self):
        size = Path(self.safe_uri).stat().st_size
        return size

    img_exif_iso = IntField()
    img_exif_ts = DateTimeField()
    img_exif_model = StringField()

    def update_exif(self):
        r = _get_exif(self.safe_uri)
        self.img_exif_ts = r['DateTime']
        try:
            self.img_exif_iso = r['ISOSpeedRatings']
        except Exception as ex:
            logging.warning(ex)
        try:
            self.img_exif_model = r['Model']
        except Exception as ex:
            logging.warning(ex)

    img_width = IntField()
    img_height = IntField()

    def update_image_size(self):
        from PIL import Image
        with Image.open(self.safe_uri) as img:
            self.img_width, self.height = img.size

    @property
    def safe_uri(self):
        uri = self.uri
        if uri.startswith('file://'):
            uri = uri[len('file://'):]
        return uri

def is_image_path(path):
    EXTENTIONS = ['jpg', 'png', 'bmp']
    ext = path.split('.')[-1]
    if ext.lower() in EXTENTIONS:
        return True
    return False

def get_path(uri):
    if uri.startswith('file://'):
        uri = uri[len('file://'):]
    return uri

def update_file_info():
    for obj in FileRefDoc.objects():
        fref: FileRefDoc = obj
        uri = get_path(fref.uri)
        file_info = FileInfoDoc(uri=fref.uri)
        file_info.size = get_file_size(uri)
        w, h = get_image_size(uri)
        file_info.img_width = w
        file_info.img_height = h
        file_info.save()


from PIL import Image
from PIL.ExifTags import TAGS
dfn='/Users/ivanne/Documents/personal/mobile2018-03-27--after-st-petersburg/DCIM/100MEDIA/IMAG0329.jpg'
def _get_exif(fn=dfn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded != 'MakerNote':
            ret[decoded] = value

    return ret
DEFAULT_STAGES = [
        'file_size',
        'image_size',
        'exif']


def _updater(file_info: FileInfoDoc, stages=DEFAULT_STAGES):
    from collections import Counter
    errors = Counter()
    for stage in stages:
        try:
            getattr(file_info, 'update_' + stage)()
        except Exception as ex:
            errors[stage] +=1
            print(f"Execption: {ex}")
    return errors


def update_file_info():
    count = 0
    errors = 0
    for obj in FileInfoDoc.objects():
        count +=1
        file_info: FileInfoDoc = obj
        try:
            file_info.update_file_size()
            file_info.update_image_size()
            file_info.update_exif()
            file_info.save()
        except Exception as ex:
            errors +=1
            print(f"Execption: {ex}")
    print(f"Proceessed {count}. OK: {count - errors}. FAILED: {errors}")


def update_info(stages=DEFAULT_STAGES):
    from collections import Counter
    count = 0
    errors_d = Counter()
    for obj in FileInfoDoc.objects():
        count +=1
        file_info: FileInfoDoc = obj
        err = _updater(file_info, stages=stages)
        errors_d.update(err)
    errors = max(errors_d.values())
    print(f"Proceessed {count}. OK: {count - errors}. FAILED: {errors}")
    print(f"Errors {errors_d}")



if __name__ == "__main__":
    # df = {
    #     index_files.__name__: index_files
    # }
    logging.basicConfig(level=logging.INFO)
    fire.Fire()


