import sys
import os
import subprocess
import re
import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm
import math
"""
!!!it will clear all FRAMEPATH item first!!

FRAMEPATH: 影片分割png黨路徑
TMPPATH: style video 暫存資料夾

function call:
style_transfer(videoPath, keyframe, output, stylizer, frame=FRAMEPATH, tmp=TMPPATH):
"""
FRAMEPATH = './frame/'
TMPPATH = './styletmp/'

def del_files(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    return
def frame_name(path):
    name, _ = os.path.splitext(os.path.basename(path))
    index = re.split(r"\D", name)
    return index[-1]

def vid2frames(video,frame):
    if not os.path.exists(frame):
        os.mkdir(frame)
    else:
        del_files(frame)
    args = ['ffmpeg', '-i', video, "-start_number", "0000" , '-filter:v' ,'fps=30', frame+'%04d.png']
    out = subprocess.run(args, capture_output=True)
    if out.returncode != 0:
        print("ffmpeg returned a nonzero exit code:")
        print(out)
    
    #rename png to correct decimal
    n = getFrameCount(frame)
    formatn = int(math.log10(n)+1)
    
    del_files(frame)
    args = ['ffmpeg', '-i', video, "-start_number", "0000" , '-filter:v' ,'fps=30', frame+'%0'+str(formatn)+'d.png']
    out = subprocess.run(args, capture_output=True)
    return

def getFrameCount(frame):
    return len(os.listdir(frame))

def moveNonBlended(parent, key, direction):
    cur = parent+key+'/'
    if direction == 1:
        #images before first keyframe
        for root, dirs, files in os.walk(cur):
            for f in files:
                i, ext = f.split('.')
                if i < key and ext == 'png':
                    shutil.move(cur+f, parent+f)
    elif direction == -1:
        #images before first keyframe
        for root, dirs, files in os.walk(cur):
            for f in files:
                i, ext = f.split('.')
                if i > key and ext == 'png':
                    shutil.move(cur+f, parent+f)
    else:
        print("value error\n")
    return
           
def style_transfer(videoPath, keyframe, output, stylizer, ebsynth, frame, tmp, logfile):
    """
    input:
        videoPath:影片檔案位置
        keyframe:KFs資料夾
        output:output檔案 (資料夾要存在)
        stylizer:stylizing video 資料夾
        frame:暫存Frame位置
        tmp:stylizing video 暫存存放位置 
            deleted when done
    """
    #file syntax check
    if keyframe[-1] != '/': keyframe+='/'
    if tmp[-1] != '/': tmp+='/'
    if frame[-1] != '/': frame+='/'
    for dir in [frame, tmp]:
        if not os.path.exists(dir):
            os.mkdir(dir)
        else:
            del_files(dir)

    vid2frames(videoPath,frame)
    
    n = getFrameCount(frame)
    formatn = int(math.log10(n)+1)
    ##reformat keyframes
    keys = os.listdir(keyframe)
    
    lastkf = 0
    for kf in keys:
        index = int(frame_name(keyframe+kf))
        if index !=0:
            formati = int(math.log10(index)+1)
        else:
            formati = 1
        #get last keyframe
        new_format = '0'*(formatn-formati)+str(index)
        new_name = new_format+'.'+kf.split('.')[-1]
        if index > lastkf:
            lastkf = index
        os.rename(keyframe+kf,keyframe+new_name)

    styleArgs = [stylizer, "--binary", ebsynth,  frame, tmp, keyframe, str(0), str(n-1)]
    #styleArgs = ['./Stylization',  frame, tmp, keyframe]
    #./stylization input output keyframe
    # out = subprocess.run(styleArgs, capture_output=True)
    # if out.returncode != 0:
    #     print("Ebsynth returned a nonzero exit code:")
    #     print(out)
    with open(logfile, "w") as outfile:
        outfile.write('status:timefornap\n')
        outfile.write("inputFrames:"+str(n)+'\n')
        outfile.write("lastKey:"+str(lastkf)+'\n')

    with open(logfile, "a") as outfile:
        subprocess.run(styleArgs, stdout=outfile)
    #png to mp4
    with open(logfile, "a") as outfile:
        outfile.write('status:ebsynth_done\n')
    keys = [f.split('.')[0] for f in os.listdir(keyframe)]
    keys.sort()
    # for kf in keys:
    #     subprocess.check_output('rm '+tmp+'*' + kf+'.png', shell=True)
    if len(keys) == 1:
        args = ['ffmpeg','-y','-i', tmp+keys[0].split('.')[0]+"/%0"+str(formatn)+"d.png" ,'-r' , '30',output]
    else:
        moveNonBlended(tmp, keys[0], 1)
        moveNonBlended(tmp, keys[-1], -1)
        args = ['ffmpeg','-y','-i', tmp+"%0"+str(formatn)+"d.png" ,'-r' , '30',output]
    
    out = subprocess.run(args, capture_output=True)
    if out.returncode != 0:
        print("ffmpeg returned a nonzero exit code:")
        print(out)
    #del intermediate files
    
    with open(logfile, "a") as outfile:
        outfile.write('status:finished')
    return
# PRJDIR = "/home/thejackys/ntu/vfx/ebsynthPY/"
# VIDPATH = "/home/thejackys/ntu/vfx/ebsynthPY/input/video/out.mp4"
# KF = "/home/thejackys/ntu/vfx/stylizing-video/data/test/keys"
# OUT = "./out.mp4"
# FRAME = "./frames/"
# TMP  = "./tmp/"
# STYLIZER = "/home/thejackys/ntu/vfx/stylizing-video/Stylization"
# EBSYNTH = "/home/thejackys/ntu/vfx/stylizing-video/ebsynth"
# logfile ='ebout'
# style_transfer(VIDPATH, KF, OUT, STYLIZER, EBSYNTH, FRAME, TMP,logfile)   