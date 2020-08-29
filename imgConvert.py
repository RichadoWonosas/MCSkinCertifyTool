# -*- coding: UTF-8 -*-

import cv2
import numpy

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]

s = input('Please enter content:\n')

s = s.encode('UTF-8')

length = len(s)
print(length)
img = numpy.zeros((4, length << 2, 3), numpy.uint8)

for i in range(length):

    for j in range(8):
        if ((i >> (7 ^ j)) & 1) == 1:
            img[j & 3, (i << 2) + (j >> 2)] = WHITE
        else:
            img[j & 3, (i << 2) + (j >> 2)] = BLACK

    # temp = ord(s[i])
    temp = s[i]

    for j in range(8):
        if ((temp >> (7 - j)) & 1) == 1:
            img[j & 3, (i << 2) + 2 + (j >> 2)] = WHITE
        else:
            img[j & 3, (i << 2) + 2 + (j >> 2)] = BLACK

cv2.imwrite('E:\\Coding\\python\\img\\trial.png', img)
