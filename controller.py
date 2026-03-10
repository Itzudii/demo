"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from tag import TagGenerator
from fsmanager import FSManager
from dependencies.storage import Storage
from cli import CliPerformer
from task import TaskPerformer

import threading
import time
import queue
from multiprocessing import Process, Queue, Event,synchronize

from typing import Dict,Any
import logging
logger = logging.getLogger("FS")

def tag_worker(tag_queue: Queue, result_queue: Queue, pause_event: synchronize.Event, stop_event: synchronize.Event):

        tagG = TagGenerator()
        tagG.load_model()

        while not stop_event.is_set():
            # pause support
            pause_event.wait()
            try:
                path = tag_queue.get(timeout=0.5)
            except:
                continue

            logger.info(f"Generating tag for:{path}")
            
            # simulate heavy work
            time.sleep(3)
            if stop_event.is_set():
                break

            tag = tagG.generate_tags_path(path)
            result_queue.put({
                "type":"tagGenration",
                "path":path,
                "tags":tag
            })


class Controller:
    def __init__(self):
        logger.info('Controller init...')
        self.task_queue= queue.Queue()
        self.task_result_queue = queue.Queue()

        self.task_pause_event = threading.Event()
        self.task_stop_event = threading.Event()

        self.tag_queue = Queue()
        self.tag_result_queue = Queue()
 
        self.tag_pause_event = Event()
        self.tag_stop_event = Event()

        self.db_queue = queue.PriorityQueue()
        
        self.isRunning = True

        self.fs = FSManager(self.tag_queue,self.tag_result_queue,self.db_queue)
        # self.fs.load()
        self.cli = CliPerformer(self.fs)
        self.performer = TaskPerformer(self.fs)

        #  multi processing || TAG PROCESSING
        self.tag_pause_event.set()   # allow running
        self.tag_process = Process(
            target=tag_worker,
            args=(self.tag_queue, self.tag_result_queue, self.tag_pause_event, self.tag_stop_event)
        )
        logger.info('TAG PROCESS STARTS')
        self.tag_process.start()


        # Task performer
        self.task_pause_event.set()
        self.task_process = threading.Thread(target=self.fs_background,daemon=True)
        self.task_process.start()
        logger.info('TASK PROCESS TREAD STARTS')

    def on_close(self):
        logger.info("CLOSING..")
        self.stop_fs_background()
        self.stop_tag_worker()
        logger.info("CLOSED")

    def stop_fs_background(self):
        self.task_stop_event.set()
        self.task_pause_event.set()
        self.task_process.join()

    def stop_tag_worker(self):
        self.tag_stop_event.set()
        self.tag_pause_event.set()
        self.tag_process.join(timeout=5)
        if self.tag_process.is_alive():
            self.tag_process.terminate()
            self.tag_process.join()

        logger.info("Tag worker stopped")

        
    def fs_background(self):
        'priority schudeling and background runs'
        db = Storage()
        self.fs.startup()

        logger.info('background tread starts')
        while not self.task_stop_event.is_set():
            self.task_pause_event.wait() # stopper

            try:
                task = self.task_queue.get_nowait()
                logger.info(f"task found: {task['name']}")
                result = self.task_handler(task)
                self.task_result_queue.put(result)
                continue

            except queue.Empty:
                pass
        
            self.fs.active()

            self.fs.background_index_step1() #tags
          
            self.fs.background_index_step2(db) #hash

            self.fs.background_index_step3(db) #db

            self.fs.mrvec.background_task_step()

            time.sleep(0.001)
        while True:
           
            isDone = self.fs.background_index_step3(db)
            if not isDone:
                break

        # Now wait for safety (if you use task_done properly)
        self.db_queue.join()
        db.commit()
        
        db.close()
        logger.info("Safely Tread Exit")

    def task_handler(self, task:Dict[str,Any]):
        'assign task and execute'

        target = task.get("for")
        name = task.get("name")
        args = task.get("args", [])

        if target == "TaskPerformer":
            fn = getattr(self.performer, name)
            logger.info("task run")
            return fn(*args)
        
        if target == "CliPerformer":
            fn = getattr(self.cli, name)
            return fn(*args)
        logger.info('unknown task')
        return {"error": "unknown task"}

    def start_task(self, task:Dict[str,Any]):
        'start task'
        self.task_queue.put(task)

        while True:
            try:
                return self.task_result_queue.get_nowait()
            except queue.Empty:
                pass

            time.sleep(0.001)
