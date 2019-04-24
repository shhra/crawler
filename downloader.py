from threading import Thread
from sys import exit
import argparse
import os
import logging
import requests


class ThreadWithReturn(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None

    def run(self):
        target = getattr(self, '_target')
        if not target is None:
            self._return = target(*getattr(self, '_args'), **getattr(self, '_kwargs'))

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return


def init_logger(st):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(filename='./logs/error_{}.log'.format(st))
    formatter = logging.Formatter('%(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def template_url(id):
    url = 'http://www.colourlovers.com/patternPreview/{}/CCCCCC/999999/666666/333333/000000.png'.format(str(id))
    return url


def fetch_images(start, end):
    logger = init_logger(start)
    for i in range(start, end):
        if i % 1000 == 0:
            logger.info("Downloaded {} images".format(i))
        try:
            filename = str(i)+'.jpg'
            image_request = requests.get(template_url(i))
            if image_request.status_code == 200:
                with open("./templates/{}".format(filename), 'wb') as f:
                    f.write(image_request.content)
                    f.close()
        except requests.exceptions.InvalidURL:
            continue

        except:
            logger.exception("could not download image: {}".format(i))
            continue
    return 0


if __name__ == '__main__':
    path = './templates'
    if not os.path.exists(path):
        os.mkdir(path)
    aparser = argparse.ArgumentParser(description='Define ranger of parser')
    aparser.add_argument('--start', metavar='-S', type=int, default=1, help='Start iterator')
    aparser.add_argument('--end', metavar='-E', type=int, default=500, help='End iterator')
    args = aparser.parse_args()

    d = 10000

    download_thread_1 = ThreadWithReturn(name='downloader_{}'.format(args.start),
                                         target=fetch_images,
                                         args=(args.start, args.start + d))
    download_thread_2 = ThreadWithReturn(name='downloader_{}'.format(args.start + d),
                                         target=fetch_images,
                                         args=(args.start + d, args.start + 2 * d))
    download_thread_3 = ThreadWithReturn(name='downloader_{}'.format(args.start + 2 * d),
                                         target=fetch_images,
                                         args=(args.start + 2 * d, args.start + 3 * d))

    print(" Starting thread at {}".format(args.start))

    download_thread_1.start()
    download_thread_2.start()
    download_thread_3.start()

    out  = download_thread_1.join()
    out2 = download_thread_2.join()
    out3 = download_thread_3.join()

    if out == out2 == out3 == 0:
        print("Successful")
        exit(0)
    else:
        exit(-1073741819)

