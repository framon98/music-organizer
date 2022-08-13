from tkinter import *
from tkinter import Tk
from tkinter import ttk
from win32api import GetSystemMetrics
from tinytag import TinyTag
from tkinter import filedialog
import os
import logging
import coloredlogs
from os import listdir
from os.path import join
import py7zr
import shutil
from shutil import move
import subprocess as sp
import webbrowser
import patoolib
from pyunpack import Archive

#----Logging config----#
logger = logging.getLogger("MusicOrganizer")
# c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('errors.log')
# c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.ERROR)

#Formatters
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
#Handlers
# logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.setLevel(logging.DEBUG)
coloredlogs.install(level=logging.DEBUG, logger=logger, fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')


class MusicGui:
    """Class to allocate GUI regarding music organization."""

    def __init__(self, master):
        """Inicializador para la GUI de music organizer."""
        #----Screen Adjustment ----#
        screen_width = GetSystemMetrics(0)
        screen_height = GetSystemMetrics(1)
        half_width = int((screen_width/2)-(640/2))
        half_heigth = int((screen_height/2)-(480/2))

        #----Window Creation----#
        master.title("Organizador de musica")
        master.geometry(f"640x480+{half_width}+{half_heigth}")
        master.resizable(False, False)
        master.columnconfigure([0,5], weight=1)
        master.rowconfigure([0,7], weight=1)

        #----Variables----#
        self.fuente_var = StringVar()
        self.same_folder_var = IntVar()
        self.dest_var = StringVar()
        self.error_var = StringVar()
        self.zip_var = IntVar()

        #----Labels----#
        self.fuente_lbl = ttk.Label(master, text="Directorio Fuente: ")
        self.fuente_lbl.grid(row=1, column=1)

        ttk.Label(master, text="").grid(row=2, column=1)
        self.dest_lbl = ttk.Label(master, text="Directorio Destino")
        self.dest_lbl.grid(row=3, column=1)

        ttk.Label(master, text="").grid(row=5, column=1,)
        self.error_lbl = Label(master, textvariable=self.error_var, font=("Arial", 12))
        self.error_var.set("0 Errors")
        self.error_lbl.grid(row=6, column=2)

        #----Entries----#
        self.fuente_entry = ttk.Entry(master, width=40, textvariable=self.fuente_var)
        self.fuente_entry.bind('<Key>', lambda e:"break")
        self.fuente_entry.grid(row=1, column=2)

        self.dest_entry = ttk.Entry(master, width=40, textvariable=self.dest_var)
        self.dest_entry.bind('<Key>', lambda e:"break")
        self.dest_entry.grid(row=3, column=2)
        

        #----Buttons----#
        self.fuente_btn = Button(master, text="Selecciona una carpeta", command=self.choose_src_folder)
        self.fuente_btn.grid(row=1, column=3)

        self.dest_btn = Button(master, text="Selecciona una carpeta", command=self.choose_dst_folder)
        self.dest_btn.grid(row=3, column=3)

        self.same_folder_btn = Checkbutton(master, text="Misma Carpeta?", command=self.same_folder, variable=self.same_folder_var)
        self.same_folder_btn.deselect()
        self.same_folder_btn.grid(row=3, column=4, sticky='w')

        self.zip_files_btn = Checkbutton(master,text="Tiene archivos Zip?", variable=self.zip_var)
        self.zip_files_btn.deselect()
        self.zip_files_btn.grid(row=1, column=4, sticky='w')

        self.sort_btn = Button(master, text="Ordenar musica", command=self.order_music)
        self.sort_btn.grid(row=4, column=2)
        self.log_btn = Button(master, text="Ver Log", command=self.open_log)
        self.log_btn.grid(row=6, column=3)

    def choose_src_folder(self):
        """Funcion para seleccionar la carpeta fuente."""
        fuente_dir = os.path.normpath(filedialog.askdirectory())
        self.fuente_var.set(fuente_dir)

    def choose_dst_folder(self):
        """Funcion para seleccionar carpeta destino."""
        dest_dir = os.path.normpath(filedialog.askdirectory())
        self.dest_var.set(dest_dir)
    
    def same_folder(self):
        """Funcion para editar campo de dest folder si se elige el mismo."""
        if self.same_folder_var.get():
            self.dest_var.set(self.fuente_var.get())
            # print(self.fuente_var.get())
        elif not self.same_folder_var.get():
            self.dest_var.set("")

    def order_music(self):
        """Esta funcion correra la parte del move music script y del move music (Separar el zip por si se checkea o no)."""
        logger.debug("Ordering music...")
        if self.same_folder_var.get():
            if self.zip_var.get():
                self.zip_files(self.fuente_var.get())
                self.move_music_out(self.fuente_var.get())
                self.folder_org(self.fuente_var.get())
            else:
                self.move_music_out(self.fuente_var.get())
                self.folder_org(self.fuente_var.get())
            
        elif not self.same_folder_var.get():
            self.move_music_dst()
            if self.zip_var.get():
                self.zip_files(self.dest_var.get())
                self.move_music_out(self.dest_var.get())
                self.folder_org(self.dest_var.get())

    def move_music_dst(self):
        """Funcion que mueve a su destino final los archivos a organizar. 
        Permite mover .7z, .m4a y .mp3"""
        src_dir = self.fuente_var.get()
        dst_dir = self.dest_var.get()
        logger.debug("Moving music to final destination...")
        for file in listdir(src_dir):
            if file[-4:] == '.mp3' or file[-4:] == '.m4a' or file[-3:] == '.7z':
                logger.info("Moving {} to {}".format(join(src_dir, file), join(dst_dir, file)))
                move(join(src_dir, file), join(dst_dir, file))

    def move_music_out(self, dstfolder):
        """Funcion para mover fuera las canciones de suscarpetas y eliminar esas carpetas"""
        directory = dstfolder
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
                logger.warning("Deleting directory {}".format(join(directory, music_dir)))
                try:
                    shutil.rmtree(join(directory, music_dir))
                    # logger.debug(join(directory, music_dir))
                except OSError as e:
                    # print("Error: %s - %s." % (e.filename, e.strerror))
                    logger.error("Error: %s - %s." % (e.filename, e.strerror))
            except:
                # print("File {} not compatible".format(music_dir))
                logger.error("File {} not compatible".format(music_dir)) 

    def open_log(self):
        """
        En esta funcion se abrira una top level window que va a leer el log file creado.
        Lo muestra despues para ver los errores.
        """
        logger.info("Opening log")
        webbrowser.open("errors.log")
        # programName = r"C:\Users\Paquito\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        # fileName = "errors.log"
        # sp.Popen([programName, fileName])

    def zip_files(self, dstfolder):
        """
        Esta funcion se encarga de primero hacerle unzip o unrar a los comprimidos.
        Los elimina una vez extraidos.
        """
        directory = dstfolder
        logger.debug("Unziping files first...")
        logger.info(directory)
        for zipfile in listdir(directory):
            if zipfile[-3:] == '.7z':
                try:
                    with py7zr.SevenZipFile(join(directory, zipfile), mode='r') as z:
                        z.extractall(path=directory)
                    # patoolib.extract_archive(join(directory, zipfile))

                    # Archive(zipfile).extractall(join(directory, zipfile))
                    logger.warning("Deleting compressed file {}".format(join(directory, zipfile)))
                
                    os.remove(join(directory, zipfile))
                except:
                    logger.critical("File not Found")

    def folder_org(self, dstfolder):
        """
        Esta funcion se encarga de cear, mover y organizar la musica que tengas siempre que haya metadatos
        """
        directory = dstfolder
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
            


def main():
    """Funcion que corre la GUI una vez ejecutada."""
    root = Tk()
    feedback = MusicGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
