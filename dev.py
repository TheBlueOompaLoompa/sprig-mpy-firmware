import sys
import time
import os
from shutil import copyfile, move
from setuptools._distutils.dir_util import copy_tree
import mpy_cross
from ampy.files import Files
from ampy.pyboard import Pyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent

board_path = '/dev/ttyACM1'

def open_board():
    board = Pyboard(board_path)
    files = Files(board)
    return (board, files)

import subprocess

def recursive_put_dir(files: Files, src_path: str, target_path: str, compile = False):
    for path in os.listdir(src_path):
        sub_target = target_path + '/' + path.split('/')[-1]
        if os.path.isdir(path):
            files.mkdir(sub_target)
            recursive_put_dir(files, sub_target)
        else:
            build_path = path
            if compile and build_path.endswith('.py'):
                mpy_cross.run(str(build_path), '-o', str(build_path.replace('.py', '.mpy'))).wait()
                os.remove(build_path)
                build_path = build_path.replace('.py', '.mpy')
                sub_target = sub_target.replace('.py', '.mpy')

            put_file(files, build_path, sub_target)

def put_file(files: Files, path: str, target: str):
    with open(path, 'rb') as f:
        files.put(target, f.read())
        f.close()

def is_valid_path(path: str):
    valid = path.find('.') >= 0 and path.find('~') < 0
    print(valid, path)

class EventHandler(FileSystemEventHandler):
    def on_created(self, event: FileCreatedEvent):
        (board, files) = open_board()
        device_path = event.src_path.replace('src/', '/')
        build_path = event.src_path.replace('src/', 'build/')
        if event.is_directory:
            files.mkdir(device_path, exists_okay=True)
            copy_tree(event.src_path, build_path)
            recursive_put_dir(files, build_path, device_path, compile=True)
        else:
            if is_valid_path(device_path):
                if device_path.endswith('.py'):
                    device_path = device_path.replace('.py', '.mpy')
                    build_path = build_path.replace('.py', '.mpy')
                    print('Compiling ' + event.src_path + ' to ' + build_path)
                    mpy_cross.run(str(event.src_path), '-o', str(build_path)).wait()
                else:
                    copyfile(str(event.src_path), str(build_path))
                    
                put_file(files, build_path, device_path)
            else:
                print('????? Nothing uploaded')

        board.close()
        print('Uploaded ' + build_path + ' to :' + device_path)

    def on_moved(self, event: FileMovedEvent):
        (board, files) = open_board()
        build_src = event.src_path.replace('src/', 'build/')
        build_dest = event.dest_path.replace('src/', 'build/')
        device_src = event.src_path.replace('src/', '/')
        device_dest = event.dest_path.replace('src/', '/')
        if event.is_directory:
            move(build_src, build_dest)
            files.rmdir(device_src, missing_okay=True)
            files.mkdir(device_dest)
            recursive_put_dir(files, build_dest, device_dest)
        else:
            if build_src.endswith('.py'):
                build_src = build_src.replace('.py', '.mpy')
                build_dest = build_dest.replace('.py', '.mpy')
            if is_valid_path(build_src) and is_valid_path(build_dest):
                move(build_src, build_dest)

        board.close()

    def on_modified(self, event: FileModifiedEvent):
        device_path = event.src_path.replace('src/', '/')
        build_path = event.src_path.replace('src/', 'build/')

        if event.is_directory:
            print('How do modify dir?')
        else:
            if is_valid_path(build_path):
                (board, files) = open_board()
                if device_path.endswith('.py'):
                    device_path = device_path.replace('.py', '.mpy')
                    build_path = build_path.replace('.py', '.mpy')
            
                put_file(files, build_path, device_path)
                print('Modified ' + event.src_path)
                board.close()
            else:
                print('?????')

    def on_deleted(self, event: FileDeletedEvent):
        (board, files) = open_board()
        device_path = event.src_path.replace('src/', '/')
        build_path = event.src_path.replace('src/', 'build/')
        if event.is_directory:
            files.rmdir(device_path, missing_okay=True)
            os.rmdir(build_path)
        else:
            if is_valid_path(device_path):
                if device_path.endswith('.py'):
                    device_path = device_path.replace('.py', '.mpy')
                    build_path = device_path.replace('.py', '.mpy')
            
                files.rm(device_path)
                os.remove(build_path)
        board.close()
        print('Deleted ' + build_path + ' and :' + device_path)


if __name__ == "__main__":
    path = 'src/'
    try:
        os.mkdir('build')
    except Exception as e:
        print('Probably not an error: ' + str(e))
    observer = Observer()
    event_handler = EventHandler()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
