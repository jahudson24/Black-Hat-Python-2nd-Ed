# For Linux
# apt-get install libopencv-dev python3-opencv python3-numpy python3-scipy
#  wget http://eclecti.cc/files/2008/03/haarcascade_frontalface_alt.xml
# Copy the wget file to the specified TRAIN directory.
# To be run after recapper.py has run.

import cv2
import os

ROOT = '/root/Desktop/pictures'
FACES = '/root/Desktop/faces'
TRAIN = '/root/Desktop/training'

def detect(srcdir=ROOT, tgtir=FACES, train_dir=TRAIN)
    for fname in os.listdir(srcdir):
        if not fname.upper().endswith('.JPG'):
            continue
        fullname = os.path.join(srcdir, fname)
        newname = os.path.join(tgtir, fname)
        img = cv2.imread(fullname)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')
        cascade = cv2.CascadeClassifier(training)
        rects = cascade.detectMultiScale(gray, 1.3, 5)
        try:
            if rects.any():
                print("Got a face")
                rects[:, 2:] += rects[:, :2]
        except AttributeError:
            print(f'No faces found in {fname}.')
            continue
        # Highlight the faces in the image
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
            cv2.imwrite(newname, img)

if name == '__main__':
    detect()
