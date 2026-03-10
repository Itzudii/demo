"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from fsmanager import FSManager

import pyperclip
from typing import List,Tuple,Any,Dict

class TaskPerformer:
    def __init__(self, fs:FSManager):
        self.fs = fs


    def show_list(self):
        self.fs.quick_refresh_cwd()
        return  self.fs.show_list()
        

    def open(self,name:str):
        self.fs.go_to(name)


    def backward(self):
        self.fs.go_back()
       

    def forward(self):
        self.fs.go_forward()
       

    def go_root(self):
        self.fs.go_to_root()
       

    def go_to_address(self,path:str)->Dict[str,Any]:
        isDone,msg = self.fs.go_to_address(path)
        return {
            "isdone":isDone,
            "msg":msg
        }
    
    def go_to_id(self,id:int):
        self.fs.open_id(id)

    def go_to_parent(self,id:int):
        return self.fs.go_to_parent(id)
      
       

    def rename(self,old:str,new:str):
        
        result = self.fs.rename(old,new)
       
        return result
        

    def cut(self,ids:List[int]): 
        self.fs.unselect_all()
        self.fs.select(*ids)
        self.fs.cut()
       

    def copy(self,ids:List[int]):
        self.fs.unselect_all()
        self.fs.select(*ids)
        self.fs.copy()
       
        
    def paste(self):
        result = self.fs.paste()  
        return result

    def delete(self,ids:List[int]):
        self.fs.unselect_all()
        self.fs.select(*ids)
        self.fs.delete()
       

    def create_folder(self,name:str):
        
        name = self.fs.create_dir(name)
       
        return name

    def create_file(self,filename:str,content:str=""):
        
        name = self.fs.create_file(filename,content)
       
        return name

    def path_breaker(self):
        
        result = self.fs.path_break_cwd()
        return result
    
    def get_cwd(self):
        path = self.fs.get_cwd()
        return path

    def get_quick(self):
        results:List[Tuple[str,int|None]] =[]
        for id in self.fs.quick_access.data:
            node = self.fs.tree.get(id)
            if node:
                results.append((node.name,node.id))

        return results
                

    def pin_to_quick(self,id:int):
        self.fs.quick_access.add(id)
       
    def unpin_to_quick(self,id:int):
        self.fs.quick_access.remove(id)
       

    def ultra_search(self,search_for:str,search_where:str,prifix:str,extension:str,substring:str):
        
        result = self.fs.ultra_search(search_for,search_where,prifix,extension[1:] if extension.startswith('.') else extension ,substring)
       
        return result

    # hash
    def get_duplicates(self):
        
        data = self.fs.search_duplicate_files()
    
        return data
    
    def find_dup(self,id:int):
        
        hash_= self.fs.search_hash_by_path(id)
        ids= self.fs.search_paths_by_hash(hash_)
        paths = [self.fs.get_path(id) for id in ids]
       
        return {
            "paths":list(paths)
        }

       

    def tag_search(self,tags:str):
        data = self.fs.context_search(tags)
        return data
    

    def copy_text(self,text:str):
        pyperclip.copy(text)

    def lock_files(self,ids:List[int]):
        for id in ids:
            node = self.fs.tree.get(id)
            if node:
                self.fs.lock_file(node)               

    def unlock_files(self,ids:List[int]):
        for id in ids:
            node = self.fs.tree.get(id)
            if node:
                self.fs.unlock_file(node)
       

     
