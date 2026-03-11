"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
import dependencies.log_config
from controller import Controller

import webview
import logging
from typing import Dict,Any
import os
logger = logging.getLogger("FS")

def create_task(worker_name:str,operation_name:str, *args:Any)-> Dict[str,Any]:
    return {
        "for": worker_name,
        "name": operation_name,
        "args": args
    }

class API:
    def __init__(self, controller: Controller)->None:
        self._ctrl = controller
        window = webview.create_window(
                title="FS Manager",
                url="frontend/main-window.html",
                width=1200,
                height=700,
                resizable=True,
                fullscreen=False,
                js_api=self
        )
        if window:
            self._window = window
            self._window.events.closed += self._ctrl.on_close

    

    def show_list(self):
        task = create_task("TaskPerformer","show_list")
        return self._ctrl.start_task(task)

    def open(self,*args:Any):
        task = create_task("TaskPerformer","open",*args)
        return self._ctrl.start_task(task)


    def backward(self):
        task = create_task("TaskPerformer","backward")
        return self._ctrl.start_task(task)
       

    def forward(self):
        task = create_task("TaskPerformer","forward")
        return self._ctrl.start_task(task)
       
    def go_root(self):
        task = create_task("TaskPerformer","go_root")
        return self._ctrl.start_task(task)
       

    def go_to_address(self,*args:Any):
        task = create_task("TaskPerformer","go_to_address",*args)
        return self._ctrl.start_task(task)
    
    def go_to_id(self,*args:Any):
        task = create_task("TaskPerformer","go_to_id",*args)
        return self._ctrl.start_task(task)
    
    def go_to_parent(self,*args:Any):
        task = create_task("TaskPerformer","go_to_parent",*args)
        return self._ctrl.start_task(task)
    

    def navigate_to(self,path:str):
        path = f'{'/'.join(path.split('/')[:-1])}"'
        self._window.evaluate_js(f'navigateToBreadcrumb(null,{(path)})') 
        
    def navigate_to_id(self,id:int):
        self._window.evaluate_js(f'navigateToBreadcrumbId(null,{(id)})')   

    def navigate_to_parent(self,id:int):
        node = self._ctrl.fs.tree.get(id)
        if node:
            p_node = node.parent
            self._ctrl.fs._set_cwd(p_node)
            self._window.evaluate_js(f'refresh()')   
       

    def rename(self,*args:Any):
        task = create_task("TaskPerformer","rename",*args)
        return self._ctrl.start_task(task)
        

    def cut(self,*args:Any):
        task = create_task("TaskPerformer","cut",*args)
        return self._ctrl.start_task(task)
       

    def copy(self,*args:Any):
        task = create_task("TaskPerformer","copy",*args)
        return self._ctrl.start_task(task)
       
        
    def paste(self):
        task = create_task("TaskPerformer","paste")
        return self._ctrl.start_task(task)

    def delete(self,*args:Any):
        task = create_task("TaskPerformer","delete",*args)
        return self._ctrl.start_task(task)
       

    def create_folder(self,*args:Any):
        task = create_task("TaskPerformer","create_folder",*args)
        return self._ctrl.start_task(task)

    def create_file(self,filename:str,content:str=""):
        task = create_task("TaskPerformer","create_file",*(filename,content))
        return self._ctrl.start_task(task)

    def path_breaker(self):
        task = create_task("TaskPerformer","path_breaker")
        return self._ctrl.start_task(task)
    
    def get_cwd(self):
        task = create_task("TaskPerformer","get_cwd")
        return self._ctrl.start_task(task)

    def get_quick(self):
        task = create_task("TaskPerformer","get_quick")
        return self._ctrl.start_task(task)

    def pin_to_quick(self,*args:Any):
        task = create_task("TaskPerformer","pin_to_quick",*args)
        return self._ctrl.start_task(task)
       
    
    def unpin_to_quick(self,*args:Any):
        task = create_task("TaskPerformer","unpin_to_quick",*args)
        return self._ctrl.start_task(task)
         

    
    def open_search(self):
        webview.create_window(
            title="FS Manager",
            url="frontend/file-search.html",
            width=550,
            height=755,
            resizable=False,
            fullscreen=False,
            js_api=self
        )
    def open_cli(self):
        webview.create_window(
            title="FS Manager",
            url="frontend/cli.html",
            width=550,
            height=550,
            resizable=False,
            fullscreen=False,
            js_api=self
        )
       

    def ultra_search(self,search_for:str,search_where:str,prifix:str,extension:str,substring:str):
        task = create_task("TaskPerformer","ultra_search",search_for,search_where,prifix,extension,substring)
        return self._ctrl.start_task(task)

    # hash
    def get_duplicates(self):
        task = create_task("TaskPerformer","get_duplicates")
        return self._ctrl.start_task(task)

    
    def find_dup(self,*args:Any):
        task = create_task("TaskPerformer","find_dup",*args)
        return self._ctrl.start_task(task)

    def copy_text(self,*args:Any):
        task = create_task("TaskPerformer","copy_text",*args)
        return self._ctrl.start_task(task)
       

    def tag_search(self,*args:Any):
        task = create_task("TaskPerformer","tag_search",*args)
        return self._ctrl.start_task(task)
       

    def lock_files(self,*args:Any):
        task = create_task("TaskPerformer","lock_files",*args)
        return self._ctrl.start_task(task)
               

    def unlock_files(self,*args:Any):
        task = create_task("TaskPerformer","unlock_files",*args)
        return self._ctrl.start_task(task)
    
    def run_command(self,*args:Any):
        task = create_task("CliPerformer","run_command",*args)
        return self._ctrl.start_task(task)

if __name__ == '__main__':
    os.makedirs(".database", exist_ok=True)
    os.makedirs(".save", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("model", exist_ok=True)

    logger = dependencies.log_config.setup_logger()
    logger.info('FS starts=====>')
    api = API(Controller())
    webview.start(debug=True)
 