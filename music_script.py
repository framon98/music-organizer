from tinytag import TinyTag
import os 
import shutil
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
logger.debug("You are working in {}".format(directory))


for file in os.listdir(directory):
    if file[-4:] == '.mp3' or file[-4:] == '.m4a':
        full_path = directory + "\\" + file
        # print("Your full path for this file is {}".format(full_path))
        logger.info("Your full path for this file is {}".format(full_path))
        # print(file[-3:])
        # print(file)
        tag = TinyTag.get(full_path)
        try:
            # print(type(tag.albumartist))
            if tag.albumartist is None:
                artist_dir_path = directory + "\\" + tag.artist
                artist_dir_path = artist_dir_path.strip()
            else:
                artist_dir_path = directory + "\\" + tag.albumartist
                artist_dir_path = artist_dir_path.strip()
            album = tag.album
            album = album.replace(':', ' ')
            album = album.replace('/', ' ')
            album = album.replace('"', ' ')
            album = album.replace('|', ' ')
            album = album.replace('?', ' ')
            # album = album.replace('*', ' ')
            album = album.replace('...', ' ')
            

            album_dir_path = directory + "\\" + album
            album_dir_path = album_dir_path.strip()
            final_move = artist_dir_path + "\\" + album
            final_move = final_move.strip()

            # print(artist_dir_path)
            logger.info("Artist dir: {}".format(artist_dir_path))
            # print(album_dir_path)
            logger.info("Album dir: {}".format(album_dir_path))
            # print(final_move)
            logger.info("Final destination: {}".format(final_move))
            if not os.path.exists(album_dir_path) and not os.path.exists(final_move):
                # if ':' in album_dir_path:
                #     album_dir_path = album_dir_path.replace(':', ' ')
                os.makedirs(album_dir_path)
                # print("Directory created for album")
                logger.debug("Directory created for album")

            if not os.path.exists(artist_dir_path):
                os.makedirs(artist_dir_path)
                # print("Directory created for artist")
                logger.debug("Directory created for artist")
            
            if os.path.exists(album_dir_path):
                shutil.move(full_path, album_dir_path)
                # print("Song moved to album dir")
                logger.debug("Song moved to album dir")
            elif os.path.exists(final_move):
                shutil.move(full_path, final_move)
                # print("Song moved to album dir inside artist dir")
                logger.warning("Song moved to album dir inside artist dir")
                continue

            if os.path.exists(artist_dir_path):
                shutil.move(album_dir_path, final_move)
                # print("Album moved to artist dir")
                logger.warning("Album moved to artist dir")

            
            # print(tag.artist)
            # print(tag.album)
            print("----------------------------------")
        except:
            # print("Could not create folder for the file {} or move it correctly".format(full_path))
            logger.error("Could not create folder for the file {} or move it correctly".format(full_path))
    


