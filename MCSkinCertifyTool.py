import os
import sys
import cv2
import numpy
import random
import tkinter as tk
import tkinter.filedialog as dialog

positionList = [
    [0, 4],
    [0, 24],
    [0, 28],
    [0, 32],
    [0, 36],
    [0, 56],
    [0, 60],
    [4, 0],
    [4, 4],
    [4, 24],
    [4, 28],
    [4, 32],
    [4, 36],
    [4, 56],
    [4, 60],
    [16, 0],
    [16, 12],
    [16, 16],
    [16, 36],
    [16, 40],
    [16, 52],
    [16, 56],
    [16, 60],
    [20, 56],
    [20, 60],
    [24, 56],
    [24, 60],
    [28, 56],
    [28, 60],
    [32, 0],
    [32, 12],
    [32, 16],
    [32, 36],
    [32, 40],
    [32, 52],
    [32, 56],
    [32, 60],
    [36, 56],
    [36, 60],
    [40, 56],
    [40, 60],
    [44, 56],
    [44, 60],
    [48, 0],
    [48, 12],
    [48, 16],
    [48, 28],
    [48, 32],
    [48, 44],
    [48, 48],
    [48, 60]
]
WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 255]


def getpath():
    options = {}
    options['defaultextension'] = '.txt'
    options['filetypes'] = [('All Files', '.*'),
                            ('Portable Network Graphic Format', '.png')]
    options['initialdir'] = os.path.abspath(sys.argv[0])
    options['initialfile'] = '*.png'
    options['parent'] = None
    options['title'] = 'Choose a Minecraft Skin'
    return dialog.askopenfilename(**options)


def createCertification():
    while True:
        # Enter character name
        charaName = input(
            'Please enter character name (Skip for Default):\n')
        if charaName == '' or charaName == '\n':
            charaName = 'Default'

        # Enter author name
        author = input('Please enter author name (Skip for Default):\n')
        if author == '' or author == '\n':
            author = 'Default'

        # Combine each part together
        info = 'CharaName: ' + charaName + '\nAuthor: ' + author

        cont = info.encode('UTF-8')
        # Legal info
        if len(cont) < 52:
            break

        # Illegal info
        else:
            print('Over length: Please make ' +
                  str(len(info) - 51) + ' character shorter.\n')
            input('Press enter to continue...')

    return [info, len(cont)]


def encode(info: str):

    inf = info.encode('UTF-8')
    length = len(inf)
    imgBlock = numpy.zeros((51, 4, 4, 4), numpy.uint8)

    # Generate every block
    for i in range(51):

        # Case 1: in the length
        if i < length:

            # Part 1: Serial number
            for j in range(8):

                # Process bytes into picture
                if ((i >> (7 - j)) & 1) == 1:
                    imgBlock[i, j & 3, j >> 2] = WHITE
                else:
                    imgBlock[i, j & 3, j >> 2] = BLACK

            # Get value of info character
            temp = inf[i]

            # Part 2: Contents
            for j in range(8):

                # Process bytes into picture
                if ((temp >> (7 - j)) & 1) == 1:
                    imgBlock[i, j & 3, 2 + (j >> 2)] = WHITE
                else:
                    imgBlock[i, j & 3, 2 + (j >> 2)] = BLACK

        # Case 2: out of range
        else:

            # Construct default view
            for j in range(16):
                if (random.randint(0, 1)) == 1:
                    imgBlock[i, j & 3, j >> 2] = WHITE
                else:
                    imgBlock[i, j & 3, j >> 2] = BLACK

            imgBlock[i, 0, 0] = WHITE

    imgBlock = imgBlock.tolist()
    random.shuffle(imgBlock)
    imgBlock = numpy.array(imgBlock)

    return imgBlock


def decode(img):

    value = 0
    place = 0
    length = 0
    validate = 0

    for i in range(2):
        for j in range(4):
            validate <<= 1
            [b, g, r, a] = img[j, i]
            if int(b) + int(g) + int(r) >= 384:
                validate += 1

    if validate != 0b01011010:
        print('v')
        return None

    for i in range(2):
        for j in range(4):
            length <<= 1
            [b, g, r, a] = img[j, 2 + i]
            if int(b) + int(g) + int(r) >= 384:
                length += 1

    if length >= 52:
        print('l')
        return None

    info = numpy.zeros(length).tolist()  # ''.rjust(length, ' ').encode()

    for i in range(51):

        [height, width] = positionList[i]

        [b, g, r, a] = img[height, width]
        if int(b) + int(g) + int(r) >= 384:
            continue

        place = value = 0

        for j in range(2):
            for k in range(4):
                place <<= 1
                [b, g, r, a] = img[height + k, width + j]
                if int(b) + int(g) + int(r) >= 384:
                    place += 1

        if place >= length:
            print([width, height])
            print(i)
            print(place)
            return None

        for j in range(2):
            for k in range(4):
                value <<= 1
                [b, g, r, a] = img[height + k, width + 2 + j]
                if int(b) + int(g) + int(r) >= 384:
                    value += 1

        info[place] = value & 0xFF

    info = bytes(info).decode('UTF-8')

    return info


def MCSkinDetect(img):
    # Get parameters
    length = len(img.shape)
    if length < 3:
        return False
    [height, width, channel] = img.shape

    # Detect if the parameters are legal
    if height != 64 or width != 64 or channel < 4:
        return False
    else:
        return True


def MCSkinAvailable(img):

    if not MCSkinDetect(img):
        return False

    for i in range(16):
        if img[i & 3, i >> 2, 3] != 0:
            return False

    return True


def addCertification(img, encodedInfo, length):

    # Step 1: fill in length info
    for i in range(8):
        if (((i & 3) ^ (i >> 2)) & 1) == 1:
            img[i & 3, i >> 2] = WHITE
        else:
            img[i & 3, i >> 2] = BLACK

    for i in range(8):
        if ((length >> (7 - i)) & 1) == 1:
            img[i & 3, 2 + (i >> 2)] = WHITE
        else:
            img[i & 3, 2 + (i >> 2)] = BLACK

    # Step 2: fill in information
    for i in range(51):
        [height, width] = positionList[i]
        for j in range(4):
            for k in range(4):
                img[height + j, width + k] = encodedInfo[i, j, k]

    return img


def readCertification(img):

    info = decode(img)
    if info is None:
        return 'Invalid!'
    else:
        return info


def add():
    while True:
        filepath = getpath()
        # filepath = input('Please input file path: ')

        [rootdir, filename] = os.path.split(filepath)
        pwd = os.getcwd()
        if rootdir:
            os.chdir(rootdir)
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        os.chdir(pwd)

        if not img is None:
            if MCSkinDetect(img):
                if MCSkinAvailable(img):
                    break
                else:
                    input('This image has already been certified!!\n' +
                          'Press enter to continue...')
            else:
                input('This image is not a Minecreft Skin!\n' +
                      'Press enter to continue...')
        else:
            input('Path Invalid!\nPress enter to continue...')

    [info, length] = createCertification()
    encodedInfo = encode(info)

    output = addCertification(img, encodedInfo, length)

    outputPath = filepath.rstrip('g').rstrip(
        'n').rstrip('p').rstrip('.') + '_output.png'
    [rootdir, filename] = os.path.split(outputPath)
    if rootdir:
        os.chdir(rootdir)
    img = cv2.imwrite(filename, img)
    os.chdir(pwd)

    input('Complete!\nPress enter to continue...')


def read():
    while True:
        filepath = getpath()
        # filepath = input('Please input file path: ')

        [rootdir, filename] = os.path.split(filepath)
        pwd = os.getcwd()
        if rootdir:
            os.chdir(rootdir)
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        os.chdir(pwd)

        if not img is None:
            if MCSkinDetect(img):
                if not MCSkinAvailable(img):
                    break
                else:
                    input('This image has not been certified!!\n' +
                          'Press enter to continue...')
            else:
                input('This image is not a Minecreft Skin!\n' +
                      'Press enter to continue...')
        else:
            input('Path Invalid!\nPress enter to continue...')
    pass

    print('The certification is:\n' + readCertification(img))
    input('Press enter to continue...')


if __name__ == "__main__":
    print('Welcome to Minecraft Skin Certification Application!')

    root = tk.Tk()
    root.withdraw()
    while True:
        s = input('Please select operation:\n' +
                  '1. Add certification\n' +
                  '2. View certification\n' +
                  'Others. Quit\n' +
                  'Please enter to choose...\n\n' +
                  'Your Choice: ')

        if s.startswith('1'):
            add()
        else:
            if s.startswith('2'):
                read()
            else:
                break
