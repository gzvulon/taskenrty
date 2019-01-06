import cv2
import queue
from threading import Thread
import logging
from pathlib import Path


def resize_img(desired_size, im):
    ## opencv has copyMakeBorder() method which is handy for making borders
    old_size = im.shape[:2] # old_size is in (height, width) format
    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])

    # new_size should be in (width, height) format
    im = cv2.resize(im, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,
        value=color)
    return new_im

def resize_pad(desired_size, im_pth, dst_pth):
    ## opencv has copyMakeBorder() method which is handy for making borders
    im = cv2.imread(im_pth)
    new_im = resize_img(desired_size, im)
    cv2.imwrite(dst_pth, new_im)


class Resizer:
    def __init__(self, start_q, dest_p, done_q=None, desired_size=256):
        self.dest_p = Path(dest_p)
        self._start_q = start_q
        self._done_q = done_q
        self._proc_q = queue.Queue()
        self._save_q = queue.Queue()
        self._finished = False
        self.desired_size = desired_size

    def _loader(self):
        while True:
            im_pth = item = self._start_q.get()
            if item == '__exit__':
                self._proc_q.put('__exit__')
                break
            im = cv2.imread(im_pth)
            assert im is not None, im_pth
            # print(f"Resize:load {im_pth}")
            item = (im, im_pth)
            self._proc_q.put(item)

    def _proccessor(self):
        print('started _proccessor')
        while True:
            item = self._proc_q.get()
            if item == '__exit__':
                self._save_q.put('__exit__')
                break
            im, im_pth = item
            new_im = resize_img(self.desired_size, im)
            # print(f"Resize:proc {im_pth}")
            ritem = (new_im, im_pth)
            self._save_q.put(ritem)

    def _saver(self):
        while True:
            item = self._save_q.get()

            if item == '__exit__':
                self._save_q.put('__exit__')
                break
            new_im, im_pth = item

            dst_name = str(im_pth).replace('/','@')
            dest_path = str(self.dest_p / dst_name)

            cv2.imwrite(dest_path, new_im)
            print(f"Resize:save {dest_path}")

            if self._done_q:
                self._done_q.put(im)

    def start(self):
        logging.info("staring threads")
        # self._lt = Thread(target=self._loader)
        self._pt = Thread(target=self._proccessor)
        self._st = Thread(target=self._saver)

        for t in [self._pt, self._st]:
            t.start()

        self._loader()

        for t in [self._pt, self._st]:
            t.join()
#
# DEF_DEST = '/Users/ivanne/mldb/thumbs'
# # fiter = iter_files(
# #     root_dir='/Users/ivanne/mlg_index/',
# #     pattern='*.jpg.json')
# DEF_FITER = ('/Users/ivanne/mlg_index/', '*.jpg.json')
#
#
# def make_thumbs_old(dest=DEF_DEST, fiter=DEF_FITER):
#     desc_p = Path(dest)
#     desc_p.mkdir(parents=True, exist_ok=True)
#     for fpath in fiter:
#         resize_func(fpath, desc_p)
