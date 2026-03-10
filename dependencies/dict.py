"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""

import os
import pickle
from typing import Set
import logging
logger = logging.getLogger("FS")
class pickle_dict:
    def __init__(self, db_path:str, autosave:bool=True):
        self.db_path = db_path
        self.autosave = autosave
        self.data:Set[int] = set()
        self.load()

    
    # ---------------- Core Operations ---------------- #

    def add(self, id:int)->None:
        """
        Insert or update path with hash
        """
        self.data.add(id)
        if self.autosave:
            self.save()
        

    def remove(self, id:int)->None:
        """
        Delete path entry
        """
        try:
            self.data.remove(id)
        except Exception as e:
            logger.error(f'{e}')
        if self.autosave:
            self.save()


    def save(self)->None:
        """
        Save HashMaster state to pickle
        """
        if os.path.dirname(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with open(self.db_path, "wb") as f:
            pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)


    def load(self)->None:
        """
        Load HashMaster state from pickle
        """
        if not os.path.exists(self.db_path):
            return

        try:
            with open(self.db_path, "rb") as f:
                self.data = pickle.load(f)


        except Exception:
            logger.error('pickledict is corrupted')
            pass
    
