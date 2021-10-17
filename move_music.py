from os.path import join
from os import listdir, rmdir
from shutil import move
import shutil
import os
import patoolib
import py7zr
import logging
import coloredlogs


#----Logging config----#
logger = logging.getLogger("MusicOrganizer")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('errors.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.ERROR)

#Formatters
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
#Handlers
logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.DEBUG)
coloredlogs.install(level=logging.DEBUG, logger=logger, fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')

directory = os.getcwd()
# print("You are working in {}".format(directory))
logger.info("You are working in {}".format(directory))
# print("Extracting Files")
logger.info("Extracting Files")

# for rar in listdir(directory):
#     try: 
#         if rar[-4:] == '.7z':
#             patoolib.extract_archive(f"{rar}.7z", outdir=directory)
#     except:
#         print("Couldn't extract file")


for zipfile in listdir(directory):
    if zipfile[-3:] == '.7z':
        with py7zr.SevenZipFile(zipfile, mode='r') as z:
            z.extractall(path=directory)
        logger.warning("Deleting {}".format(zipfile))
        os.remove(zipfile)
        

# print("Already extracted all files")
# logger.info("Already extracted all files")

for music_dir in listdir(directory):
    try:
        if music_dir[0] == '.':
            logger.debug("Ignoring this directory {}".format(music_dir))
            continue
        if music_dir[-3:] == '.py':
            logger.debug("Ignoring this python file {}".format(music_dir))
            continue
        for file in listdir(join(directory, music_dir)):
            if file[-4:] == '.mp3' or file[-4:] == '.m4a':
                move(join(directory, music_dir, file), join(directory, file))
                # print("Moving {} to {}".format(join(directory, music_dir, file),join(directory, file)))
                logger.info("Moving {} to {}".format(join(directory, music_dir, file),join(directory, file)))
        # print("Deleting...{}".format(join(directory, music_dir)))
        logger.warning("Deleting...{}".format(join(directory, music_dir)))
        try:
            shutil.rmtree(join(directory, music_dir))
        except OSError as e:
            # print("Error: %s - %s." % (e.filename, e.strerror))
            logger.error("Error: %s - %s." % (e.filename, e.strerror))
    except:
        # print("File {} not compatible".format(music_dir))
        logger.error("File {} not compatible".format(music_dir))
    # if file[-4:] == '.mp3' or file[-4:] == '.m4a':
    #     pass

