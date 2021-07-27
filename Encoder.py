import cv2
import numpy as np
import getopt
import sys
import os
from includes import *


def encode_component_dc(hist, encoder, sample_x, sample_y):
    w, h = hist.shape
    mcu_w, mcu_h = w // (8 * sample_x), w // (8 * sample_y)
    last_dc_coeff = 0
    code = []
    for i in mcu_h:
        for j in mcu_w:
            for y in sample_y:
                for x in sample_x:
                    dc_coeff = hist[(i * sample_y + y) * 8, (j * sample_x + x) * 8]
                    delta = dc_coeff - last_dc_coeff
                    last_dc_coeff = dc_coeff
                    catagory = MSB(abs(delta))
                    code.append(encoder[catagory])
                    if catagory >= 1:
                        code.append('0' if delta > 0 else '1')
                    if catagory > 1:
                        code.append(int2string(abs(delta)^(1<<catagory), catagory - 1))
    return string2bytes(''.join(code))


def encode_component_ac(hist, encoder, sample_x, sample_y):
    w, h = hist.shape
    mcu_w, mcu_h = w // (8 * sample_x), w // (8 * sample_y)
    code = []
    for i in mcu_h:
        for j in mcu_w:
            for y in sample_y:
                for x in sample_x:
                    # TODO
                    pass


def encode(in_file: str, out_file: str, k: float):
    out_file = 'abc'
    image = np.array(cv2.imread(in_file))
    # print(image.shape)
    # exit(0)
    ori_shape = image.shape
    assert ori_shape[2] == 3
    target_shape = (ori_shape[0] + 15) // 16 * 16, (ori_shape[1] + 15) // 16 * 16, 3
    image = np.append(image, np.zeros((target_shape[0] - ori_shape[0], ori_shape[1], ori_shape[2])), axis=0)
    image = np.append(image, np.zeros((target_shape[0], target_shape[1] - ori_shape[1], 3)), axis=1)
    bitmap = (image.reshape((-1, 3)) @ RGB2YCbCr.T + np.array([0, 128, 128], dtype=np.float32)).reshape(image.shape)
    Y = bitmap[:, :, 0]
    Cb_ = bitmap[:, :, 1]
    Cr_ = bitmap[:, :, 2]
    dshape = tuple(i // 2 for i in Cb_.shape)
    Cb = np.ndarray(dshape, dtype=np.float32)
    Cr = np.ndarray(dshape, dtype=np.float32)
    cv2.pyrDown(Cb_, Cb, dshape)
    cv2.pyrDown(Cb_, Cb, dshape)
    out = open(out_file, 'wb')
    # SOI
    out.write(b'\xff\xd8')

    # APP0
    out.write(b'\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01')
    out.write(b'\x00\x78\x00\x78\x00\x00')

    # DQT
    out.write(b'\xff\xdb\x00')
    for x in DQT_l:
        for y in x:
            item = max(round(y * k), 255)
            out.write(item.to_bytes(1, byteorder='big'))
    out.write(b'\xff\xdb\x01')
    for x in DQT_c:
        for y in x:
            item = max(round(y * k), 255)
            out.write(item.to_bytes(1, byteorder='big'))

    # SOF0
    h, w = bitmap.shape[:2]
    out.write(bytes.fromhex("ffc0 0011 08") + h.to_bytes(2, byteorder='big') + w.to_bytes(2, byteorder='big') + b'\x03')
    out.write(bytes.fromhex("012200 021101 031101"))

    # DHT
    out.write(bytes.fromhex("ffc4 001f 00"))
    out.write(DHT_l_dc)
    out.write(bytes.fromhex("ffc4 005b 10"))
    out.write(DHT_l_ac)
    out.write(bytes.fromhex("ffc4 001f 01"))
    out.write(DHT_c_dc)
    out.write(bytes.fromhex("ffc4 005b 11"))
    out.write(DHT_l_ac)

    # SOS
    out.write(bytes.fromhex("ffda 000c 03 0100 0211 0311 0000 00"))

    # encoding DHT
    for i in range(h // 16):
        for j in range(w // 16):
            for index in range(4):
                x, y = index >> 1, index & 1

    # EOI
    out.write(b'\xff\xd9')
    out.close()


def main():
    opts, args = getopt.getopt(sys.argv[1:], "o:")
    if not args:
        print("Usage: python Encoder.py [-o <filename>] image_file")
        exit(0)
    in_file = args[0]
    out_file = f"{os.path.splitext(in_file)[0]}.jpg"
    k = 1
    for opt, value in opts:
        if opt == '-o':
            out_file = value
        elif opt == '-k':
            k = int(value)
    encode(in_file, out_file, k)


if __name__ == '__main__':
    main()
