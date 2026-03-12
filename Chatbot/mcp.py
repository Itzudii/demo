
from task import TaskPerformer,base,fail,success
from typing import List,Tuple,Any,Dict

class FSTools:
    TOOLS = [
    # ── Navigation ────────────────────────────────────────────
    {
        "name": "goto_path",
        "description": "Navigate to a directory path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Target directory path"}
            },
            "required": ["path"]
        }
    },

    # ── List Files ────────────────────────────────────────────
    {
        "name": "list_files",
        "description": "List files in the current directory",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "list_files_path",
        "description": "List files in a specific directory path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path to list"}
            },
            "required": ["path"]
        }
    },

    # ── Create Folder ─────────────────────────────────────────
    {
        "name": "create_folder",
        "description": "Create a folder in the current directory",
        "parameters": {
            "type": "object",
            "properties": {
                "foldername": {"type": "string", "description": "Name of the folder to create"}
            },
            "required": ["foldername"]
        }
    },
    {
        "name": "create_folder_on",
        "description": "Create a folder at a specific path",
        "parameters": {
            "type": "object",
            "properties": {
                "foldername": {"type": "string", "description": "Name of the folder to create"},
                "path":       {"type": "string", "description": "Target directory path"}
            },
            "required": ["foldername", "path"]
        }
    },

    # ── Create File ───────────────────────────────────────────
    {
        "name": "create_file",
        "description": "Create a file in the current directory with optional content",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to create"},
                "content":  {"type": "string", "description": "Initial file content", "default": ""}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "create_file_on",
        "description": "Create a file at a specific path with optional content",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to create"},
                "path":     {"type": "string", "description": "Target directory path"},
                "content":  {"type": "string", "description": "Initial file content", "default": ""}
            },
            "required": ["filename", "path"]
        }
    },

    # ── Delete ────────────────────────────────────────────────
    {
        "name": "delete",
        "description": "Delete a file or folder by name in the current directory",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the file or folder to delete"}
            },
            "required": ["name"]
        }
    },

    # ── Rename ────────────────────────────────────────────────
    {
        "name": "rename",
        "description": "Rename a file or folder",
        "parameters": {
            "type": "object",
            "properties": {
                "oldname": {"type": "string", "description": "Current name of the file or folder"},
                "newname": {"type": "string", "description": "New name for the file or folder"}
            },
            "required": ["oldname", "newname"]
        }
    },

    # ── Lock / Unlock ─────────────────────────────────────────
    {
        "name": "lock_file",
        "description": "Lock a file to prevent modification or deletion",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the file to lock"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "unlock_file",
        "description": "Unlock a previously locked file",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the file to unlock"}
            },
            "required": ["name"]
        }
    },
]
    def __init__(self, task:TaskPerformer):
        self.task = task

    def goto_path(self,path):
        return self.task.go_to_address(path)
    #=========================
    # show list
    #=========================   
    def list_files(self):
        return self.task.show_list()
        
    def list_files_path(self, path:str):
        isSuccess,msg = self.task.fs.go_to_address(path)
        if isSuccess:
            return self.task.show_list()
        return fail(msg)
    #=========================
    # create Folder
    #=========================  
    def create_folder(self,foldername):
        return self.task.create_folder(foldername)
    
    def create_folder_on(self,foldername,path):
        isSuccess,msg = self.task.fs.go_to_address(path)
        if isSuccess:
            return self.task.create_folder(foldername)
        return fail(msg)
         
    #=========================
    # create Files
    #=========================  
    def create_file(self,filename,content=''):
        return self.task.create_file(filename,content)
    
    def create_file_on(self,filename,path,content=''):
        isSuccess,msg = self.task.fs.go_to_address(path)
        if isSuccess:
            return self.task.create_file(filename,content)
        return fail(msg)
    #=========================
    # delete File and Folder
    #=========================

    def delete(self,name):
        node = self.task.fs.get_node(name)
        if node:
            return self.task.delete(node.id)
        return fail(f'{name} not found')
    
    #=========================
    # rename
    #=========================

    def rename(self,oldname,newname):
        return self.task.rename(oldname,newname)

        
    #=========================
    # lock and Unlock File
    #=========================

    def lock_file(self,name):
        node = self.task.fs.get_node(name)
        if node:
            return self.task.lock_files(node.id)
        return fail(f'{name} not found')

    
    def unlock_file(self,name):
        node = self.task.fs.get_node(name)
        if node:
            return self.task.unlock_files(node.id)
        return fail(f'{name} not found')
    