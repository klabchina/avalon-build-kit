# -*- coding: utf-8 -*-
import logging
import os
import apk_utils
from PIL import Image
from PIL import ImageChops

__author__ = 'Kevin Sun <sun-w@klab.com>'

def exists(path):
    return os.path.exists(path)

def copy_speical_icon(sourcepath, output):
    source_img = Image.open(sourcepath)
    icon_name = apk_utils.get_iconname_in_manifest(output)
    drawablepaths = ['drawable','drawable-hdpi', 'drawable-ldpi', 'drawable-mdpi', 'drawable-xhdpi','drawable-xxhdpi','drawable-xxxhdpi','drawable-hdpi-v4', 'drawable-ldpi-v4', 'drawable-mdpi-v4', 'drawable-xhdpi-v4','drawable-xxhdpi-v4','drawable-xxxhdpi-v4']
    for draw in drawablepaths:
        fin_out_path = output + "/res/" + draw
        tmp_img = source_img.copy()
        #print(fin_out_path)
        #print(exists(fin_out_path))
        if exists(fin_out_path):
            if 'drawable-hdpi' in draw:
                tmp_img.thumbnail((72, 72))
            elif 'drawable-ldpi' in draw:
                tmp_img.thumbnail((36, 36))
            elif 'drawable-mdpi' in draw:
                tmp_img.thumbnail((48, 48))
            elif 'drawable-xhdpi' in draw:
                tmp_img.thumbnail((96, 96))
            elif 'drawable-xxhdpi' in draw:
                tmp_img.thumbnail((144, 144))
            else:
                tmp_img.thumbnail((192, 192))

            tmp_img.save(fin_out_path + "/%s.png" % icon_name, "PNG")

def addimgconer(conerpath, sourcepath, pos, output):
    coner_img = Image.open(conerpath)
    coner_size = coner_img.size
    source_img = Image.open(sourcepath)
    source_size = source_img.size

    maskLayer = Image.new('RGBA', source_size, (0,0,0,0))


    if pos == 'tl':
        box = (0, 0)
    elif pos == 'tr':
        box = (source_size[0] - coner_size[0], 0)
    elif pos == 'bl':
        box = (0, source_size[1] - coner_size[1])
    else:
        box = (source_size[0] - coner_size[0], source_size[1] - coner_size[1])

    maskLayer.paste(coner_img, box)
    output_img = Image.composite(maskLayer, source_img, maskLayer)

    icon_name = apk_utils.get_iconname_in_manifest(output)
    drawablepaths = ['drawable','drawable-hdpi', 'drawable-ldpi', 'drawable-mdpi', 'drawable-xhdpi','drawable-xxhdpi','drawable-xxxhdpi','drawable-hdpi-v4', 'drawable-ldpi-v4', 'drawable-mdpi-v4', 'drawable-xhdpi-v4','drawable-xxhdpi-v4','drawable-xxxhdpi-v4']
    for draw in drawablepaths:
        fin_out_path = output + "/res/" + draw
        tmp_img = output_img.copy()
        #print(fin_out_path)
        #print(exists(fin_out_path))
        if exists(fin_out_path):
            if 'drawable-hdpi' in draw:
                tmp_img.thumbnail((72, 72))
            elif 'drawable-ldpi' in draw:
                tmp_img.thumbnail((36, 36))
            elif 'drawable-mdpi' in draw:
                tmp_img.thumbnail((48, 48))
            elif 'drawable-xhdpi' in draw:
                tmp_img.thumbnail((96, 96))
            elif 'drawable-xxhdpi' in draw:
                tmp_img.thumbnail((144, 144))
            else:
                tmp_img.thumbnail((192, 192))

            tmp_img.save(fin_out_path + "/%s.png" % icon_name, "PNG")

