#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import version
import os
import errno
import sys
import glob
import shutil
import argparse
import pathlib
import time
import yaml
from subprocess import DEVNULL, check_call, run
from rich import print
from rich.progress import Progress

# logging
from multiprocessing import Process, Queue, current_process
from logging.handlers import TimedRotatingFileHandler, QueueHandler
from rich.logging import RichHandler
import logging


class HwDocer(object):

    __def_output__ = '_build'
    __def_input__ = './'
    __def_worker_nb__ = os.cpu_count()
    __def_timeout__ = 600
    __search_folder__ = '/**/'
    __suffix_hrs__ = '.yml'
    __suffix_dia__ = '.drawio'
    __search_hrs__ = '*' + __suffix_hrs__
    __search_dia__ = '*' + __suffix_dia__
    __def_dia_format__ = 'png'
    __def_hrs_format__ = 'html'
    __dia_format_choices__ = ['png', 'pdf', 'jpg', 'svg', 'vsdx', 'xml']
    __hrs_format_choices__ = ['png', 'html', 'pdf(NOT IMPLEMENTED)', 'gv', 'svg', 'bom']
    __verb_levels__ = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    """automatic drawing of drawio diagrams and wireviz harnesses tool"""

    def __init__(self, arg):
        super(HwDocer, self).__init__()
        self.time_start = time.time()
        self.arg = arg  # save passed arguments

        # Arguments
        argParse = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, prog=__name__)
        argParse.add_argument("-v", "--verbose", help="Increase the verbosity level (can be used upto 4 times)", action='count', default=0)
        argParse.add_argument("-i", "--input", help="input directory to search for docs to build", default=self.__def_input__, type=pathlib.Path)
        argParse.add_argument("-o", "--output", help="output build directory", default=self.__def_output__, type=pathlib.Path)
        argParse.add_argument("-w", "--worker", help="maximum number of worker process to spawn", default=self.__def_worker_nb__, type=int)
        argParse.add_argument("-t", "--timeout", help="maximum execution time allowed (in sec)", default=self.__def_timeout__, type=int)
        argParse.add_argument("--version", action="version", version=f'%(prog)s {version.version}')
        argParse.add_argument("--dia", help="diagram output file format", choices=self.__dia_format_choices__, default=self.__def_dia_format__, type=str)
        argParse.add_argument("--hrs", help="harness output files to keep (many can be choosen)", choices=self.__hrs_format_choices__, default=self.__def_hrs_format__, nargs='*', type=str)
        self.args = argParse.parse_args()  # Parse & save all arguments

        # region Logger
        self.verbosity = self.__verb_levels__[min(self.args.verbose, len(self.__verb_levels__) - 1)]
        self.log_q = Queue()

        # main object logger
        self.logger = logging.getLogger('hwdocer')
        self.logger.setLevel(self.verbosity)
        self.logger.addHandler(QueueHandler(self.log_q))

        logger_p = Process(target=self.logger_process, args=(self.log_q,))
        logger_p.start()
        self.logger.debug(f'log queue: {id(self.log_q)}')
        # endregion

        # param - input files
        current_directory = os.getcwd()
        if not os.path.isabs(self.args.input):
            self.src_path = os.path.normpath(os.path.join(current_directory, self.args.input))
        else:
            self.src_path = os.path.normpath(self.args.input)
        self.logger.debug(f'args - input path: {self.src_path}')

        # param - output files
        # make output path absolute
        if os.path.isabs(self.args.output):
            self.dst_path = os.path.normpath(self.args.output)
        else:
            self.dst_path = os.path.normpath(os.path.join(current_directory, self.args.output))
        self.logger.debug(f'args - output path: {self.dst_path}')

        # param - worker number
        self.worker_nb = self.args.worker
        self.logger.debug(f'args - worker nb: {self.worker_nb}')

        # param - execution timeout
        if self.args.timeout < 0:
            self.exec_timeout = self.__def_timeout__
        else:
            self.exec_timeout = self.args.timeout
        self.logger.debug(f'args - timeout: {self.exec_timeout} sec')

        # param - diagram format
        self.dia_format = self.args.dia
        self.logger.debug(f'args - dia format: \'{self.dia_format}\'')

        # arg - harness format
        self.hrs_format = self.args.hrs
        self.logger.debug(f'args - hrs format: \'{self.hrs_format}\'')

        # start with empty work queues
        self.copy_q = Queue()
        self.work_q = Queue()
        self.done_q = Queue()
        self.logger.debug(f'copy queue: {id(self.copy_q)}, work queue: {id(self.work_q)}, done queue: {id(self.done_q)}')

        self.time_creation = time.time()
        self.logger.debug(f'{__name__} created successfully in {self.time_creation - self.time_start:.6f} sec')

    def _search_input_files(self):
        self.logger.debug(f'searching in {self.src_path} for {self.__search_folder__}')     # first search all subfolder to known the complete structure

        # searching in subfolders
        for folder in glob.iglob(self.src_path + self.__search_folder__, recursive=True):
            self.logger.debug(f'folder found: {folder}')

            # searching for harnesses
            self.logger.debug(f'searching in {folder} for {self.__search_hrs__}')
            for file in glob.iglob(folder + self.__search_hrs__):
                self.logger.debug(f'harness found: {os.path.basename(file)}')
                self.copy_q.put(file)

            # searching for diagrams
            self.logger.debug(f'searching in {folder} for {self.__search_dia__}')
            for file in glob.iglob(folder + self.__search_dia__):
                self.logger.debug(f'diagram found: {os.path.basename(file)}')
                self.copy_q.put(file)

        self.time_search = time.time()
        self.logger.info(f'found {self.work_q.qsize()} buildable files in {self.time_search - self.time_creation:.6f} sec')

    def _prep_output(self):
        self.logger.debug(f'outut folder preparation')

        # Folder structure recreation
        try:
            # ensure root folder exists
            if not os.path.exists(self.dst_path):
                self.logger.info(f'creating output folder: {self.dst_path}')
                os.makedirs(self.dst_path)
            else:
                self.logger.debug(f'output folder: {self.dst_path} already existed')
        except Exception as e:
            self.logger.error(f'failed to create output folder {self.dst_path}')
            raise e

    def _silentremove(self, file):
        try:
            os.remove(file)
        except OSError as e:
            self.logger.debug(f'tried to delete {file} but wasn\'t present')
            if e.errno != errno.ENOENT:
                raise

    def build_hrs(self, hrs) -> int:
        self.logger.info(f'hrs building: {os.path.basename(hrs)}')
        exec_status = -1

        # Building
        try:
            exec_status = run(['wireviz', hrs])
        except Exception as e:
            self.logger.error(f'wireviz failed: {e}')

        # Cleanup unwanted output
        for hrsformat in self.__hrs_format_choices__:   # delete all files that weren't mentionned to be kept
            if hrsformat not in self.hrs_format:
                # handle special cases
                if hrsformat == 'bom':
                    hrsformat = 'bom.tsv'   # extension of bom file is special
                elif hrsformat == 'pdf(NOT IMPLEMENTED)':
                    hrsformat = 'pdf'
                # delete the file with absolute path
                file2del = os.path.dirname(hrs) + '/' + pathlib.Path(hrs).stem + '.' + hrsformat
                self.logger.debug(f'deleting file {file2del}')
                self._silentremove(file2del)

        self.logger.debug(f'hrs built: {hrs}')
        return exec_status.returncode

    def build_dia(self, dia) -> int:
        self.logger.info(f'dia building: {os.path.basename(dia)}')
        exec_status = -1

        # Building
        try:
            # This still need to be sushed (check_call vs run) because of all the gpu error and chatter in stdout
            exec_status = check_call(['drawio', '-x', '-t', '-f', self.dia_format, dia], stdout=DEVNULL, stderr=DEVNULL)
        except Exception as e:
            self.logger.error(f'drawio failed: {e}')

        self.logger.debug(f'dia built {dia}')
        return exec_status

    def _get_diffpath(self, basepath: pathlib.Path, filepath: pathlib.Path) -> pathlib.Path:
        subpath = '.'
        if basepath is not None and filepath is not None:
            commonpath = os.path.commonpath([basepath, filepath])
            subpath = os.path.dirname(filepath).replace(commonpath, '')
        return subpath

    def _copy_src_files(self, file: pathlib.Path) -> pathlib.Path:
        if file is not None:
            file = pathlib.Path(file)  # ensure the file is a valid path
            resulting_file = pathlib.Path()
            # 1. Create subfolder in destination
            try:
                subfolder = self._get_diffpath(self.src_path, file)
                destination = pathlib.Path(str(self.dst_path) + str(subfolder))
                if not os.path.exists(destination):
                    self.logger.info(f'creating folder: {destination}')
                    os.makedirs(destination)
                else:
                    self.logger.debug(f'folder: {destination} already existed')
            except Exception as e:
                self.logger.error(f'failed to create folder: {destination}')
                raise e
            # 2. Copy source file
            try:
                self.logger.info(f'copying {file}to {destination}')
                shutil.copy2(file, destination)
                resulting_file = os.path.join(destination, os.path.basename(file))
            except Exception as e:
                self.logger.error(f'failed to copy file: {file}')
                raise e
            # 3. If harness, also copy images
            try:
                if file.suffix == self.__suffix_hrs__:
                    img_list = self._get_all_img_path_from_hrs(file)
                    if len(img_list) > 0:
                        self.logger.info(f'copying {len(img_list)} image(s) linked in {file}')
                    for image in img_list:
                        # compute the complete destination path
                        subfolder = self._get_diffpath(self.src_path, image)
                        destination = pathlib.Path(str(self.dst_path) + str(subfolder) + '/' + os.path.basename(image))
                        self.logger.debug(f'copying image: {image} to {destination}')
                        # make sure directory exist at destination
                        os.makedirs(os.path.dirname(destination), exist_ok=True)

                        if not os.path.exists(os.path.join(destination, os.path.basename(image))):
                            shutil.copy2(image, destination)
                        else:
                            self.logger.debug(f'{image} already exist')
            except Exception as e:
                self.logger.warning(f'failed to copy image: {destination} from {file}')

            self.logger.debug(f'successfully copied: {resulting_file}')
            return resulting_file

    def _get_all_img_path_from_hrs(self, hrs_path: pathlib.Path) -> list:
        image_list = []

        try:
            with open(hrs_path, 'r') as file:
                yaml_content = yaml.safe_load(file)
                for key, val in yaml_content.items():
                    if key == 'connectors' or key == 'cables':      # top level
                        for key2, val2 in val.items():              # connectors & cables listing level
                            for key3, val3 in val2.items():         # each conn/cable element level
                                if key3 == 'image':                 # we only care for the image element
                                    for key4, val4 in val3.items():  # image element level
                                        if key4 == 'src':           # we find the source path of it
                                            image = os.path.normpath(os.path.join(os.path.dirname(hrs_path), val4))
                                            self.logger.debug(f'image found: {val4} for {key2}')
                                            image_list.append(image)
        except Exception as e:
            self.logger.warning(f'failed to open {hrs_path}')
        # end try
        return image_list

    def run(self):
        status = 0

        self.logger.info(f'S execution, pid: {current_process().pid}')

        with Progress() as progress:
            out_prep = progress.add_task("Preparing output...", total=1)
            search_task = progress.add_task("Searching files...", total=None)
            copy_task = progress.add_task("Copying input files...", total=None)
            build_task = progress.add_task("Building files...", total=None)

            # 1. Prepare output folder
            self._prep_output()
            progress.update(out_prep, advance=1)

            # 2. Search all supported files
            progress.update(search_task, total=1)
            self._search_input_files()
            progress.update(search_task, advance=1)

            # 3. Copy all files
            nb_copy_file = self.copy_q.qsize()
            progress.update(copy_task, total=nb_copy_file)               # we now know how much input file to copy but not how much image in harness to copy
            while self.copy_q.qsize():
                file = self.copy_q.get()
                copied_file = self._copy_src_files(file)
                progress.update(copy_task, advance=1)
                if os.path.basename(copied_file) == os.path.basename(file):     # ensure the copied file atleast as the same name as original
                    self.logger.debug(f'work added: {os.path.basename(copied_file)}')
                    self.work_q.put(copied_file)
                else:
                    self.logger.error(f'problem copying {file} to {copied_file}')
            self.time_copy = time.time()
            self.logger.debug(f'copied {nb_copy_file} in {self.time_copy - self.time_search:.3f} sec')

            # 4. Start workers
            nb_work_file = self.work_q.qsize()
            progress.update(build_task, total=nb_work_file)
            self.worker_nb = min(self.worker_nb, nb_work_file)   # worker number is the lowest of: number of file or argument passed
            self.logger.info(f'starting {self.worker_nb} workers')
            processes = []
            for i in range(self.worker_nb):
                processes.append(Process(target=self.worker_process, args=(self.log_q, self.work_q, self.done_q), daemon=True))
                processes[i].start()

            # 4. Wait for results
            last_check = 0
            while True:

                # Check if some file have been done
                check = self.done_q.qsize()
                if check > last_check:
                    delta = check - last_check
                    last_check = check
                    progress.update(build_task, advance=delta)
                    self.logger.debug(f'build {delta} more file(s)')

                # All file have been done
                if self.done_q.qsize() >= nb_work_file:
                    self.time_done = time.time()
                    self.logger.info(f'all file built in {self.time_done - self.time_copy:.3f} sec')
                    break

                # Timeout reach
                waited = time.time() - self.time_copy
                if waited >= self.exec_timeout:
                    self.time_done = time.time()
                    self.logger.warning(f'timeout reached after {waited:.3f} sec')
                    for i in range(len(processes)):
                        # TODO: send explicit stop signal to workers
                        pass
                    break
                time.sleep(0.1)

        # work stats
        hrs_count = 0
        dia_count = 0
        for _ in range(self.done_q.qsize()):
            file = self.done_q.get()
            if pathlib.Path(file).suffix == self.__suffix_hrs__:
                hrs_count += 1
            elif pathlib.Path(file).suffix == self.__suffix_dia__:
                dia_count += 1

        # graceful end of exec
        print(f'{__name__} {version.version} built [dark_orange bold]{hrs_count} harnesses[/] and [purple bold]{dia_count} diagrams[/] in {self.time_done - self.time_start:.6f} sec')
        self.logger.info(f'P execution, pid: {current_process().pid}, built {hrs_count} harnesses and {dia_count} diagrams in {self.time_done - self.time_start:.6f} sec')
        self.log_q.put(None)
        return status

    def worker_process(self, log_q: Queue, q_in: Queue, q_out: Queue) -> int:
        """worker isolated process to generate output files from input file

        Args:
            file (pathlib.Path): input source file
        """
        self.logger = logging.getLogger(f'worker {current_process().pid}')
        self.logger.setLevel(self.verbosity)
        self.logger.addHandler(QueueHandler(log_q))
        self.logger.debug(f'started with in: {id(q_in)} out: {id(q_out)}')

        while True:
            # X. handle special message to kill worker
            # if work == 'STOP':
            #     self.logger.debug(f'received explicit stop')
            #     break
            # TODO: add rx signal to break execution

            # 1. take one file to build
            work = pathlib.Path(q_in.get())
            self.logger.debug(f'working on {work}')

            # 2. build the file
            exec_status = 0
            if work.suffix == self.__suffix_hrs__:
                exec_status = self.build_hrs(work)
            elif work.suffix == self.__suffix_dia__:
                exec_status = self.build_dia(work)
            else:
                self.logger.error(f'work given is not valid: {work}')
            if exec_status != 0:
                self.logger.error(f'{work} did not complete correctly with code: {exec_status}')

            # 3. cleanup src file
            self._silentremove(work)

            # 4. put the file on the build list
            q_out.put(work)

            # X. stop when we are at the end of the queue
            if q_in.qsize() <= 0:
                break

        self.logger.info(f'done')
        return 0

    def logger_process(self, queue: Queue) -> int:
        """ logging isolated process

        Args:
            queue (Queue): logging queue receiving all logs to be saved
        """

        logger = logging.getLogger('logger')
        logger.setLevel(self.verbosity)

        # Create a separate folder for logs if it doesn't exist
        log_dir = 'log'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Formater
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(name)-15s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        rich_formatter = logging.Formatter('[light_sea_green]%(name)-15s[/] %(message)s')

        # File logging
        log_filename = os.path.join(log_dir, f'hwdocer_{time.strftime("%Y-%m-%d_%H-%M-%S")}.log')
        file_handler = TimedRotatingFileHandler(log_filename, when='midnight', backupCount=4)
        file_handler.setFormatter(formatter)

        # Console logging
        rich_handler = RichHandler(rich_tracebacks=True, markup=True)
        rich_handler.setLevel(self.verbosity)
        rich_handler.setFormatter(rich_formatter)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(self.verbosity)  # Set the level as needed
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        # logger.addHandler(stream_handler)
        logger.addHandler(rich_handler)

        logger.info(f'S execution, pid: {current_process().pid}')

        # process loop
        while True:
            msg = queue.get()       # pull new message from queue
            if msg is None:         # exit process on special None message
                break
            logger.handle(msg)      # log the message

        logger.info(f'P execution, pid: {current_process().pid}')
        return 0
