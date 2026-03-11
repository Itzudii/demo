"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from dependencies.tree import Tree,TreeNode
from dependencies.stack import Stack
from dependencies.dict import pickle_dict
import dependencies.helperfuncUtils
from dependencies.storage import Storage
from dependencies.logmanger import LogManager
from dependencies.vector import MrVectorExpert

import os
import sys
import time
import uuid
import queue
import shutil
import logging
import itertools
import numpy as np
import multiprocessing
from pathlib import Path
from os import stat_result
from typing import List,Tuple,Optional,Any,Dict,Set


active = "watcher/logs/active.jsonl"
processing = "watcher/logs/processing.jsonl"
logger = logging.getLogger("FS")

DEFAULT_PATH = "d:/don'tDelete/Desktop/Cortex-FS - Copy/FS/demo_d"
DEFAULT_NAME = str(DEFAULT_PATH.split('/')[-1])
ALLOWED_TAGS_EXT = ['txt','pdf','doc','docx']

class FSManager:
    '''file management'''
    def __init__(self,tagq:multiprocessing.Queue,tagrq:multiprocessing.Queue,db_queue:queue.PriorityQueue):
        logger.info('FSManager init...')
        self.count_ = 0
        self.default:str = DEFAULT_PATH
        self.default_name:str = DEFAULT_NAME

        self.counter =  itertools.count()

        self.db_queue = db_queue
        self.tag_queue = tagq
        self.tag_result_queue = tagrq

        self.db = Storage()
        self.mrvec = MrVectorExpert()
        self.mrvec.load_model()

        self.tree:Optional[Tree] = Tree()
        self.tree.load_from_db(self.db)
        
        if self.tree.root is None:
            logger.info("DB is empty, initializing fresh root.")
            self._refresh_first() # Populate from filesystem
            self.tree.load_from_db(self.db)
            self.root:Optional[TreeNode] = self.tree.root
        else:
            self.root:Optional[TreeNode] = self.tree.root

        self.cwd:Optional[TreeNode] = self.root

        self.selected_nodes:Set[int] = set()
        self.state:str = 'ideal'
        self.pointer = None
        self.undoStack = Stack()
        self.redoStack = Stack()
        # self.hash_queue = []
        # self.hash_Master = HashMaster()

        self.rehash_queue:queue.Queue = queue.Queue()
        self.quick_access = pickle_dict(db_path=".save/quickA.pkl")
        #  all time are in nano second
        self.average_prifixS_time = 0
        self.average_extS_time = 0

        self.log = LogManager(active,processing)
        self.last_id = self.db.get_next_id()
      
    @staticmethod
    def needs_rehash(node:TreeNode, st:stat_result):
        """
        Decide whether file content hash must be recalculated
        """

        # Case 1: hash not calculated yet
        # if not hasattr(node, "hash") or node.hash is None:
        #     return True

        # Case 2: file size changed
        if node.size != st.st_size:
            return True

        # Case 3: modification time changed
        if node.m_time != st.st_mtime:
            return True

        # Otherwise: safe to skip hashing
        return False

    def process_event(self,event):
        path = FSManager.normalize_path(event['path'])
        data = self.get_node_by_path(path)
        node = data['result']
        if node is None:
            return
        if node.is_dir:
            for _ in self._refresh_quick(node):
                pass

    def active(self):
        new_events = self.log.active()
        if new_events:
            logger.info("newevents",new_events)
        for e in new_events:
            self.process_event(e)     

    def startup(self)->None:
        logger.info('FS start up init...')
        self.fill_queues_hash()
        self.fill_queues_tag()
        events = self.log.startup()
        for event in events:
            self.process_event(event)

    def fill_queues_hash(self)->None:
        data = self.db.get_empty_hash()
        if self.tree:
            for id, in data:
                node = self.tree.get(id)
                if node and not node.is_hidden:
                    self.rehash_queue.put(self.get_path(node.id))
           
    def fill_queues_tag(self):
        data = self.db.get_empty_tags(ALLOWED_TAGS_EXT)
        if self.tree:
            for id, in data:
                node:Optional[TreeNode] = self.tree.get(id)
                if node and not node.is_hidden:

                    self.tag_queue.put(self.get_path(node.id))
    @staticmethod               
    def normalize_path(path:str)->str: # verified
        driver,path = path.split(':',1)
        path = driver.lower()+':'+path
        return Path(path).as_posix()
    
    def _set_cwd(self,node:TreeNode)->None:
        self.undoStack.push(self.cwd)
        self.cwd = node

    def get_path(self,id:Optional[int]): # verified
        node:TreeNode = self.tree.get(id)
        stack:List[str] = []
        if node:
            while node.parent:
                stack.append(node.name)
                node = node.parent
            stack.append(DEFAULT_PATH)

        return '/'.join(reversed(stack))
        
    def get_cwd(self)->str:
        return self.get_path(self.cwd.id)

    '''                                                                                
        CORE FEATURE OF FILE MANGEMENT SYSTEM 
        > REFRESH Very Experimental do not touch currently in 99.9% safe stage   
    '''
    def _refresh_quick(self, root_node:TreeNode)->None: # verified
            root_path = self.get_path(root_node.id)

            stack:list[TreeNode] = [root_node]
            paths:list[str] = [root_path]
    

            nodes:List[Tuple[Any,...]]=[]
            # last_id = self.db.get_next_id()

            while stack:
                node = stack.pop()
                path = paths.pop()
    
                try:
                    internal = node.childs
                    seen:Set[str] = set()
                    
                    for item in os.scandir(path):
                            print(item.name,item.path)

                            name = item.name
                            seen.add(name)
                            st = item.stat(follow_symlinks=False)

                            node_:Optional[TreeNode] = internal.get(name)

                            # CREATE
                            if node_ is None:
                                print("create node",name)
                                is_dir = item.is_dir(follow_symlinks=False)
                                data = dependencies.helperfuncUtils.name_ext(name)
                                path_ = FSManager.normalize_path(item.path)

                            #    enqueue db
                                # 
                                nodes.append((
                                self.last_id,
                                name,
                                path_,
                                'd' if is_dir else 'f',
                                data.get('ext','unknown'),
                                st.st_size,
                                st.st_mtime,
                                st.st_ctime,
                                st.st_mode,
                                node.id
                                ))

                                # add new node
                                newNode = TreeNode(name,is_dir)
                                newNode.id = self.last_id
                                node.childs[name] = newNode
                                newNode.parent = node
                                newNode.size =  st.st_size
                                newNode.m_time =  st.st_mtime
                                newNode.is_hidden = data.get('ishidden',False)

                                self.tree.set(self.last_id, newNode)

                                if not is_dir:
                                    self.rehash_queue.put(path_)

                                node_ = newNode
                                self.last_id+=1
                            else:
                                if not node_.is_locked:
                                    if node_.indicator != 'sync':
                                        self.normal_request({"name":'set_indicator',
                                         "para":(node_.id,'sync')})
                                        node_.indicator = 'sync'
                                        
                                if FSManager.needs_rehash(node_, st):
                                    path_= FSManager.normalize_path(item.path)
                                    if not node_.is_dir and not node_.is_hidden:
                                        self.rehash_queue.put(path_)
                                    self.normal_request({"name":'set_size',
                                         "para":(node_.id,st.st_size)})
                                    self.normal_request({"name":'set_modified_time',
                                         "para":(node_.id,st.st_mtime)})
                                    self.normal_request({"name":'set_indicator',
                                         "para":(node_.id,'modified')})
                                    node_.indicator = 'modified'
                                    node_.size = st.st_size
                                    node_.m_time = st.st_mtime

                                


                        # DELETE
                    for name in tuple(internal):
                            if name not in seen:
                                d_node = internal[name]
                                self._delete_internal(d_node)

                except Exception as e:
                    logger.error(f'{e}')
            logger.info('loop finsh')
            self.urgent_request({
                "name":"batch_add",
                "para":(nodes,)
            })

    def _refresh_first(self): # verified
        paths = [DEFAULT_PATH]

        normalize = FSManager.normalize_path

        st = os.stat(DEFAULT_PATH)
        # last_id = self.db.get_next_id()
        # print(last_id,'last_id')
        nodes:List[Tuple[Any,...]] = [(self.last_id,
            DEFAULT_NAME,
            DEFAULT_PATH,
            'd',
            'unknown',
            st.st_size,
            st.st_mtime,
            st.st_ctime,
            st.st_mode,
            None
        )]

        parent_id = [self.last_id]
        while paths:
            path = paths.pop()
            p_id = parent_id.pop()

            try:
                for item in os.scandir(path):
                    try:
                        name = item.name
                        is_dir = item.is_dir(follow_symlinks=False)
                        st = item.stat(follow_symlinks=False)
                        data = dependencies.helperfuncUtils.name_ext(name)
                        path_ = normalize(item.path)
                        
                        self.last_id+=1
                        nodes.append((#no vector and hash after ext
                            self.last_id,
                            name,
                            path_,
                            'd' if is_dir else 'f',
                            data.get('ext','unknown'),
                            st.st_size,
                            st.st_mtime,
                            st.st_ctime,
                            st.st_mode,
                            p_id,
                        ))

                        self.count_ += 1
                        if is_dir and not item.is_symlink():
                            paths.append(path_)
                            parent_id.append(self.last_id)
                    except Exception as e:
                        logger.error(f'{e}')

            except Exception as e:
                logger.error(f'{e}')
        
        self.db.batch_add(nodes) 
        self.db.commit() 

    def _refresh(self, root_node): # verified
            root_path = self.get_path(root_node.id)
            nodes=[]
            if root_path:


                stack:list[TreeNode] = [root_node]


                paths:list[str] = [root_path]

                normalize = FSManager.normalize_path

                
                # last_id = self.db.get_next_id()

                while stack:
                    node = stack.pop()
                    path = paths.pop()

                    try:
                        internal = node.childs
                        seen = set()

                        for item in os.scandir(path):

                            name = item.name
                            seen.add(name)
                            st = item.stat(follow_symlinks=False)

                            node_:TreeNode = internal.get(name)

                            path_ = normalize(item.path)
                            # CREATE
                            if node_ is None:
                                is_dir = item.is_dir(follow_symlinks=False)
                                data = dependencies.helperfuncUtils.name_ext(name)

                            #    enqueue db
                                
                                nodes.append((#no vector and hash after ext
                                self.last_id,
                                name,
                                path_,
                                'd' if is_dir else 'f',
                                data.get('ext','unknown'),
                                st.st_size,
                                st.st_mtime,
                                st.st_ctime,
                                st.st_mode,
                                node.id,
                                ))

                                # add new node
                                newNode = TreeNode(name,is_dir)
                                newNode.id = self.last_id
                                node.childs[name] = newNode
                                newNode.parent = node
                                newNode.size =  st.st_size
                                newNode.m_time =  st.st_mtime
                                newNode.is_hidden = data.get('ishidden',False)


                                self.tree.set(self.last_id, newNode)

                                if not is_dir and newNode.is_hidden:
                                    self.rehash_queue.put(path_)

                                node_ = newNode
                                self.last_id+=1
                            else:
                                if not node_.is_locked:
                                    if node_.indicator != 'sync':
                                        self.normal_request({"name":'set_indicator',
                                         "para":(node_.id,'sync')})
                                        node_.indicator = 'sync'
                                if FSManager.needs_rehash(node_, st):
                                    if not node_.is_dir and not node_.is_hidden:
                                        self.rehash_queue.put(path_)
                                    self.normal_request({"name":'set_size',
                                         "para":(node_.id,st.st_size)})
                                    self.normal_request({"name":'set_modified_time',
                                         "para":(node_.id,st.st_mtime)})
                                    self.normal_request({"name":'set_indicator',
                                         "para":(node_.id,'modified')})
                                    node_.indicator = 'modified'
                                    node_.size = st.st_size
                                    node_.m_time = st.st_mtime

                            if node_.is_dir:
                                stack.append(node_)
                                paths.append(path_)
                            yield

                        # DELETE
                        for name in tuple(internal):
                            if name not in seen:
                                d_node = internal[name]
                                self._delete_internal(d_node)
                            yield

                    except Exception as e:
                        logger.error(f'{e}')
                        yield
            self.urgent_request({
                "name":"batch_add",
                "para":(nodes,),
            })

    def refresh_cwd(self): # verified
        ''' start analysis and updating tree structure from cwd '''
        for _ in self._refresh(self.cwd):
            pass  
    
    def refresh_root(self): # verified
        ''' start analysis and updating tree structure from root '''
        logger.info("full root loading started")
        for _ in self._refresh(self.root):
            pass

    def refresh_node(self,node): # verified
        ''' start analysis and updating tree structure from given node '''
        logger.info(f"refresh start > {node.id}")
        for _ in self._refresh(node):
            pass

    def quick_refresh_cwd(self):
        self._refresh_quick(self.cwd)
    
   
    """
       > SELECT > UNSELECT > SELECTALL > UNSELECTALL
    """ 
    def select(self,*args): # verified
        self.selected_nodes = self.selected_nodes.union(args)

    def unselect(self,*args): # verified
        self.selected_nodes.difference_update(args)
      
    def select_all(self):  # verified
        self.select(*[node.id for node in self.cwd.childs.values()])
    
    def unselect_all(self): # verified
        self.selected_nodes.clear()

    """
        > OPEN 
    """
    @staticmethod
    def _open_file_with_default_app(file_path:str)->bool:   # verified
        file_path = os.path.abspath(file_path)  # make path absolute
        if not os.path.exists(file_path):
            logger.error(f"open > {file_path} : not found")
            return False
        try:
            if sys.platform == "win32":                    # Windows
                os.startfile(file_path)                    # simplest for Windows
            logger.info(f"open > {file_path} : successfully")
            return True
        except Exception as e:
            logger.error(f"open > {file_path} :Could not open file > {e}")
            return False

    def open(self,node:TreeNode)->None: # verified
        ''' open file with default application '''
        if not node.is_dir:
           
            path = self.get_path(node.id)
            FSManager._open_file_with_default_app(path)
        else:
            if self.state == 'ideal':
                self.unselect_all()
            self._set_cwd(node)

    def open_id(self,id:int): # verified
        if self.tree:
            node= self.tree.get(id)
            if node:
                self.open(node)
            if self.root:
                self.open(self.root)
                logger.warning("node not found:open_id")


    """
    > DELETE
    """
    @staticmethod
    def get_meta(node:List[Any])->Dict[str,Any]: # verified
        return {
            "id":node[0],
           "name":node[1],
           "path":node[2],
           "type":node[3],
           "state":node[4],
           "indicator":node[5],
           "islocked":node[6],
           "locked_hash":node[7],
           "ext":node[8],
           "hash":node[9],
           "vector":node[10],
           "tags":node[11],
           "size":node[12],
           "modified_time":node[13],
           "created_time":node[14],
           "mode":node[15],
           "parent_id":node[16]
        }
    
    def collect_metadata_parent_id(self,parent_id:int): # verified
        meta_data:Dict[int,Tuple[Any]] = dict()
        all_nodes = self.db.get_node_by_parent(parent_id)

        if all_nodes:
            for node in all_nodes:
                meta_data[node[0]] = FSManager.get_meta(node)
        return meta_data
    
    def _delete_internal(self,del_node:TreeNode): # verified
        pop_node = self.tree.id_to_node.pop
        stack = [del_node]
        ids:List[int] = []
        while stack:
            node =  stack.pop()
            ids.append(node.id)
            if node.is_dir:
                stack.extend(node.childs.values())

        # self.db.delete_ids(ids)
        self.urgent_request({
            'name':'delete_ids',
            'para':(ids,)
        }) # remove in db
        
        for id in ids: # remove in id_to_node
            pop_node(id,None)
        
        p_node = del_node.parent
        p_node.childs.pop(del_node.name) # pop in parents
           
    def _delete_memory(self,node): # verified 
        ''' delete file/folder from memeory only '''
        path = self.get_path(node.id)
        if node.is_dir:
            shutil.rmtree(path)
        else:
            os.remove(path)
    
    def delete_node(self,node): # verified 
        ''' delete file/folder from disk and tree structure '''
        self._delete_memory(node)
        self._delete_internal(node)

    def delete(self): # verified
        # childs_metadata = self.collect_metadata_parent_id(self.cwd.id)
        for id in self.selected_nodes:
            node = self.tree.get(id)
            # meta = childs_metadata.get(id)
            if node:
                self.delete_node(node)

    """
    > CUT > COPY > PASTE
    """
    
    def cut(self): # verified
        if self.state == 'ideal':
            if self.selected_nodes:
                self.state = 'move'
                # self._set_pointer(self.cwd)
                logger.info("move mode activated")

    def copy(self): # verified
        if self.state == 'ideal':
            if self.selected_nodes:
                self.state = 'copy'
                # self._set_pointer(self.cwd)
                logger.info("copy mode activated")
   
    def _paste_for_move(self): # verified
        def _paste_for_move_helper(node:TreeNode)->bool:
            try:
                shutil.move(self.get_path(node.id),self.get_path(self.cwd.id))
                self.cwd.childs[node.name] = node
    
                p_node = node.parent
                p_node.childs.pop(node.name)
                logger.info('done copy')
                self.urgent_request({"name":'set_parent',
                                     "para":(node.id,self.cwd.id)})

                return True
            except Exception as e:
                logger.error(f'{e}')
                return False
        results:List[Tuple[str,bool]] = []
        for id in self.selected_nodes:
            node = self.tree.get(id)
            if node:
                result = (node.name,_paste_for_move_helper(node))
                results.append(result)
        return results

    def _paste_for_copy_helper(self,node:TreeNode)->bool: # verified
        try:
            cwd_path = self.get_path(self.cwd.id)
            node_path = self.get_path(node.id)
            if not node.is_dir:
                shutil.copy2(node_path,cwd_path)
            elif node.is_dir:
                dest_path = os.path.join(cwd_path,node.name)
                shutil.copytree(node_path,dest_path)
            
            return True
        except Exception:
            return False

    def _paste_for_copy(self): # verified
        results:List[Tuple[str,bool]] = []
        for id in self.selected_nodes:
            node = self.tree.get(id)
            if node:
                result = (node.name,self._paste_for_copy_helper(node))
                results.append(result)
        return results

    def paste(self)->List[Tuple[str, bool]|None]: # verified
        '''there is a issue of already exist thing'''#<<<<<<<<<<ERROR
        if self.state == 'move':
            result = self._paste_for_move()
            self.unselect_all()
            self.state = 'ideal'
            return result
        elif self.state == 'copy':
            result = self._paste_for_copy()
            self.unselect_all()
            self.refresh_cwd()
            self.state = 'ideal'
            return result
        self.unselect_all()
        return []
    
    """
    > CREATE
    """
    @staticmethod
    def _write_content_to_file(filepath:str,content:str): # verified
        with open(filepath,"w") as f:
            f.write(f'{content}\n')

    @staticmethod
    def _append_content_to_file(filepath:str,content:str): # verified
        with open(filepath,"a") as f:
            f.write(f'{content}\n')

    def _create_dir_memory(self,dir_name:str,p_node:Optional[TreeNode]= None): # verified
        if p_node is None:
            p_node = self.cwd
        p_path = self.get_path(p_node.id)
        new_dir_path = os.path.join(p_path,dir_name)
        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)
            logger.info(f"directory created at:{new_dir_path}") 
            return True
        else:
            return False
    
    def _create_dir_internal(self,dir_name:str,p_node:Optional[TreeNode]= None): # verified
        if p_node is None and self.cwd:
            p_node = self.cwd

        # last_id = self.db.get_next_id()

        p_path = self.get_path(p_node.id)

        new_dir_path = '/'.join([p_path,dir_name])
  
        st = os.stat(new_dir_path)
        self.urgent_request({
            "name":"add_node",
            "para":(self.last_id,
                    dir_name,
                    new_dir_path,
                    'd',
                    p_node.id,
                    'unknown',
                    None,None,None,
                    st.st_size,                    
                    st.st_mtime,                    
                    st.st_ctime,                    
                    st.st_mode
                    ),
        })
      
        newNode = TreeNode(dir_name,True)
        newNode.parent = p_node
        newNode.id = self.last_id
        newNode.size = st.st_size
        newNode.m_time = st.st_mtime
        p_node.childs[dir_name] = newNode

        self.tree.set(self.last_id, newNode)
        self.last_id +=1
        return newNode
    
    def _create_file_memory(self,file_name:str,content:str="",p_node:Optional[TreeNode]= None): # verified
        if p_node is None:
            p_node = self.cwd
        p_path = self.get_path(p_node.id)
        new_file_path = os.path.join(p_path,file_name)
       
        if not os.path.exists(new_file_path):
            FSManager._write_content_to_file(new_file_path,content)
            logger.info(f"file created at:{new_file_path}")
            return True
        return False
    
    def _create_file_internal(self,file_name:str,p_node:Optional[TreeNode]= None): # verified
        if p_node is None:
            p_node = self.cwd
        # last_id = self.db.get_next_id()
        p_path = self.get_path(p_node.id)
        new_file_path = '/'.join([p_path,file_name])
        st = os.stat(new_file_path)
        data = dependencies.helperfuncUtils.name_ext(file_name)
        # last_id+=1
        self.urgent_request({
            "name":"add_node",
            "para":(self.last_id,
                    file_name,
                    new_file_path,
                    'f',
                    p_node.id,
                    data.get('ext'),
                    None,None,None,
                    st.st_size,                    
                    st.st_mtime,                    
                    st.st_ctime,                    
                    st.st_mode
                    ),
            
        })
        

        newNode = TreeNode(file_name,False)
        newNode.parent = p_node
        newNode.id = self.last_id
        p_node.childs[file_name] = newNode
        newNode.size = st.st_size
        newNode.m_time = st.st_mtime

        self.tree.set(self.last_id, newNode)
        self.last_id +=1
        return newNode

    def create_dir(self,dir_name:str,p_node:Optional[TreeNode]= None): # verified
        isDone = self._create_dir_memory(dir_name,p_node)
        if isDone:
            self._create_dir_internal(dir_name,p_node)
            logger.info(f"create in dir > {dir_name}")
            return dir_name
        else:
            self.create_dir(dependencies.helperfuncUtils.filename_dup_normalizer(dir_name),p_node)

    def create_file(self,file_name:str,content:str="",p_node:Optional[TreeNode]= None): # verified
        isDone = self._create_file_memory(file_name,content,p_node)
        if isDone:
            node = self._create_file_internal(file_name,p_node)
            self.rehash_queue.put(self.get_path(node.id))
           
            return file_name
            
        else:
            self.create_file(dependencies.helperfuncUtils.filename_dup_normalizer(file_name),content,p_node)
    
    def write_to_file(self,node:TreeNode,content:str): # verified
        if not node.is_dir:
            FSManager._write_content_to_file(self.get_path(node.id),content)
            self._refresh_quick(node.parent)
            logger.info(f"written to file > {node.name}")
        else:
            logger.error(f"cannot write to a directory > {node.name}")
    
    def append_to_file(self,node:TreeNode,content:str): # verified
        if not node.is_dir:
            FSManager._append_content_to_file(self.get_path(node.id),content)
            self._refresh_quick(node.parent)
            logger.info(f"append to file > {node.name}")
        else:
            logger.error(f"cannot append to a directory > {node.name}")

    """
    > SHOW LIST

    """
    def to_dict(self,node:TreeNode)->Dict[str,Any]:
        return {
                "id":node.id,
                "name":node.name,
                "path":self.get_path(node.id),
                "type":'folder' if node.is_dir else 'file',
                "state":node.is_hashed,
                "indicator":dependencies.helperfuncUtils.get_indicator(node.indicator),
                "islock":node.is_locked,
                "ext":node.ext,
                "size":node.size,
                "modified_time":dependencies.helperfuncUtils.formate_sttime(node.m_time),
                "icon":'<svg xmlns="http://www.w3.org/2000/svg" height="30px" viewBox="0 -960 960 960" width="30px" fill="#fff"><path d="m484-288 89-68 89 68-34-109.15L717-468H607.56L573-576l-34 108H429l89 70.85L484-288Zm-316 96q-29 0-50.5-21.5T96-264v-432q0-29.7 21.5-50.85Q139-768 168-768h216l96 96h312q29.7 0 50.85 21.15Q864-629.7 864-600v336q0 29-21.15 50.5T792-192H168Zm0-72h624v-336H450l-96-96H168v432Zm0 0v-432 432Z"/></svg>' if node.is_dir else '<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M263.72-96Q234-96 213-117.15T192-168v-624q0-29.7 21.15-50.85Q234.3-864 264-864h312l192 192v504q0 29.7-21.16 50.85Q725.68-96 695.96-96H263.72Zm.28-72h432v-456H528v-168H264v624Zm203.54-24q65.52 0 110.99-45.5T624-348v-132h-72v132q0 34.65-24.5 59.33Q503-264 467.51-264q-34.45 0-58.98-24.67Q384-313.35 384-348v-180q0-10 7.2-17t16.8-7q10 0 17 7t7 17v192h72v-192q0-40.32-27.77-68.16-27.78-27.84-68-27.84Q368-624 340-596.16q-28 27.84-28 68.16v180q0 65 45.5 110.5T467.54-192ZM264-792v189-189 624-624Z"/></svg>'
            }

    def show_list(self,filter:None = None): # verified
        ''' show list of files and folders in current working directory '''
        return [self.to_dict(node) for node in self.cwd.childs.values()]
        # return data
    """
    > HOME >GOTO > UNDO 

    """

    def go_to_root(self): # verified
        self._set_cwd(self.root)   
    
    def go_to(self,name:str): # verified
        node = self.get_node(name)
        if node:
            self.open(node)
            return True
        else:
            logger.warning(f"{name} not found in cwd")
            return False
    
    def go_back(self): # verified
        if self.state == 'ideal':
            self.unselect_all()
        if self.undoStack.empty():
            logger.warning("no undo -> Empty")
            return False
        # it not need history push
        self.redoStack.push(self.cwd)
        prev_node = self.undoStack.pop()
        self.cwd = prev_node
        return True

    def go_forward(self): # verified
        if self.state == 'ideal':
            self.unselect_all()
        if self.redoStack.empty():
            
            logger.warning("no redo->empty")
            return
        # it not need history push
        prev_node = self.redoStack.pop()
        self.open(prev_node)

    def go_to_address(self,path:str): # verified
        try:
            driver,sub_path = path.split(':',1)
        except Exception as e:
            return (False,e)
        path = driver.lower()+":"+sub_path
        data = self.get_node_by_path(path)
        r = data['result']
        m = data['message']
        if r:
            self.open(r)
            return (True,m)
        return (False,m)
    
    def go_to_parent(self,id:int):
        p_id = self.db.get_parent_id(id)
        node = self.tree.get(p_id)
        if node:
            self.open(node)
            return node.id
        return None

    """
   > RENAME

    """
    def _rename_internal(self,filename:str,node:TreeNode,p_node:Optional[TreeNode]=None): # verified
        if p_node is None:
            p_node = self.cwd

        if filename not in p_node.childs:
            p_node.childs.pop(node.name)
            node.name = filename
            p_node.childs[filename] = node

            self.urgent_request({"name":'set_name',
                                     "para":(node.id,filename)})
          
    def _rename_memory(self,name:str,node:TreeNode)->bool: # verified
        old_add = self.get_path(node.id)
        new_add = old_add[:-len(node.name)]+name
        temp_add = old_add[:-len(node.name)]+uuid.uuid4().hex
        try:
            if node.name.lower() == name.lower():
                os.rename(old_add,temp_add)
                os.rename(temp_add,new_add)
            else:
                os.rename(old_add,new_add)
            return True
        except Exception as e:
            logger.error(f'{e}')
            return False

    def rename_node(self,name:str,node:TreeNode,p_node:Optional[TreeNode]=None)->Dict[str,Any]: # verified
        isDone = self._rename_memory(name,node)
        if isDone:
            self._rename_internal(name,node,p_node)
            logger.info(f"rename > '{node.name}' to '{name}'")
            return {
            "status":True,
            "msg": "name rename done"
            }
        return {
            "status":False,
            "msg": "invalid charcters used"
        }
        
    def rename(self,old:str,new:str)->Dict[str,Any]: # verified
        if any([new.__contains__(char)for char in '/*?"<>:|']):
            return {
            "status":False,
            "msg": 'not use this any this character / * ? " < > : |'
        }
        if new not in self.cwd.childs:
            node = self.get_node(old)
            if node:
                return self.rename_node(new,node)

        return {
            "status":False,
            "msg": "name alredy exist"
        }
        
    """
        EXTRA HELPING FEATURES 
        >GET NODE > GET NODE BY PATH
    """

    def get_node(self,filename:str)->Optional[TreeNode]: # verified
        return self.cwd.childs.get(filename)

    @staticmethod
    def path_verifier(path:str)->bool: # verified
        return True if DEFAULT_PATH in path else False
    
    @staticmethod
    def path_breaker(path:str)->List[str]: # verified
        rootv=DEFAULT_PATH.split('/')
        pathv=path.split('/')
        length = len(rootv)
        return pathv[length:]
    
    def _path_break_to_dict(self,path:str)->Dict[Any,Any]: # verified
        if FSManager.path_verifier(path):
            root_path = self.get_path(self.root.id)
            rootv=root_path.split('/')
            pathv=path.split('/')
            length = len(rootv)
            data:Dict[str,str] = {"HOME":root_path}
            names:List[str] = pathv[length:]
            node = self.root
            for name in names:
                node = node.childs.get(name)
                if node:
                    data[node.name] = node.id
            return data
        return {}

    def path_break_cwd(self): # verified
        return self._path_break_to_dict(self.get_path(self.cwd.id))
        
    def get_node_by_path(self,path:str)->Dict[str,Any]: # verified
        if FSManager.path_verifier(path):
            results = FSManager.path_breaker(path)
            root = self.root
            for pathname in results:
                if pathname in root.childs:
                    root = root.childs[pathname]
                elif pathname:
                    return {
                        'result':None,
                        'message':'path not exist'
                    }
              
            return {
                    'result':root,
                    'message':'path exist'
            }
        return {
                    'result':None,
                    'message':'path is incorrect or formate is incorrect'
            }
    @staticmethod
    def get_sub_ids(start_node:TreeNode)->list[int]:
        stack:List[TreeNode] = [start_node]
        ids:List[int] = []
        while stack:
            node = stack.pop()
            for n in node.childs.values():
                ids.append(n.id)
                if n.is_dir:
                    stack.append(n)
        return ids


            

    """
     > SEARCH
    """ 
    "PRIFIX AND EXTENSION"
    @staticmethod
    def search_helper_prifix(root_node:TreeNode,prifix:str,results:List[int],type_:str,subdir:bool = True):
        stack = [root_node]
        is_dir = True if type_ == 'd' else False
        while stack:

            node:TreeNode =  stack.pop()
            childs = node.childs
            for name,n in childs.items():
                if name.startswith(prifix) and n.is_dir == is_dir:
                    results.append(n.id)
            
                if subdir and n.is_dir:
                    stack.append(n)
                
        return results
    
    def search_prifix(self,prifix:str,type_:str,subdir:bool = True):
        results:List[int] = []
        ns1 =time.perf_counter_ns()
        FSManager.search_helper_prifix(self.cwd,prifix,results,type_,subdir)
        ns2 =time.perf_counter_ns()
        self.average_prifixS_time = ns2-ns1
        return results
    
    def search_prifix_all(self,prifix:str,type_:str)->List[int|None]:
        ns1 =time.perf_counter_ns()
        data = self.db.search_prefix(prifix,type_)
        ns2 =time.perf_counter_ns()
        self.average_prifixS_time = ns2-ns1
        if data:
            return [id for id, in data]
        return []

    def search_helper_ext(self,node:TreeNode,ext:str,subdir:bool = True):
        if subdir:
            ext_ids = self.tree.get_ext(ext)
            sub_ids = FSManager.get_sub_ids(node)

            results = set(ext_ids)
            set_sub_ids = set(sub_ids)
            results.intersection_update(set_sub_ids)  
            return list(results)
        
        return [node.id for node in node.childs.values() if node.ext == ext]
 
    def search_ext(self,ext:str,subdir:bool = True):
 
        ns1 =time.perf_counter_ns()
        results = self.search_helper_ext(self.cwd,ext,subdir)
        ns2 =time.perf_counter_ns()
        self.average_extS_time = ns2-ns1
        return results

    def search_ext_all(self,ext:str)->List[int|None]:
        if self.tree:
            return self.tree.get_ext(ext)
        return []

    def ultra_search(self,search_for:str,search_where:str,prifix:str,extension:str,substring:str)->List[Dict[str,Any]]:
        results:List[int|None] =[]
        Both = True if search_for == 'fd' else False
        tree_get=self.tree.get
        if extension:
            if search_where == 'pd':
                results = self.search_ext(extension,False)
            elif search_where == 'sd':
                results = self.search_ext(extension,True)
            elif search_where == 'rd':
                results = self.search_ext_all(extension)
            final_result:List[Dict[str,Any]] = []
            for id in results:
                node = tree_get(id)
                if node:
                    final_result.append({
                       'name':node.name,
                       'id':node.id,
                    })
            return final_result
        
      
        if search_for == 'f' or Both:
            if search_where == 'pd':
                results += self.search_prifix(prifix,'f',False)
            elif search_where == 'sd':
                results += self.search_prifix(prifix,'f',True)
            elif search_where == 'rd':
                results += self.search_prifix_all(prifix,'f')
        if search_for == 'd' or Both:
            if search_where == 'pd':
                results += self.search_prifix(prifix,'d',False)
            elif search_where == 'sd':
                results += self.search_prifix(prifix,'d',True)
            elif search_where == 'rd':
                results += self.search_prifix_all(prifix,'d')
        # if substring:
        #     results = self.filter_substring(substring,results)
        
        final_result = []
        for id in results:
            node = tree_get(id)
            final_result.append({
                'name':node.name,
                'id':node.id,
            })
        return final_result



    "HASH"
    def search_hash_by_path(self, id:int):
        hash = self.db.get_hash(id)
        return hash if hash else ''
        
    def search_paths_by_hash(self, file_hash: str)->List[int]:
        ids = self.db.get_id_by_hash(file_hash)
        return ids

    def search_duplicate_files(self):
        data = self.db.duplicates_hash()
        result:List[List[int]] = []
        if data:
            for hash,lst in data.items():
                if lst:
                    result.append(lst)
        return result


       
    def lock_file(self,node:TreeNode):# we not update locked_hash currently
        if not node.is_dir:
            node.is_locked = True
            self.urgent_request({
                'name':'set_locked',
                "para":(node.id,True)
            })
            return True
        return False

    def unlock_file(self,node:TreeNode):
        node.is_locked = False
        self.urgent_request({
                'name':'set_locked',
                "para":(node.id,False)
            })
    

    """
        CONTEXT
    """
    def context_search(self,query:str):
        print(query)
        tags = query.split(',')
        vector:Any = self.mrvec.convert_tags_to_vector(tags)
        print(tags)

        blobs = self.db.get_all_blobs()
        ids:List[int] = []
        vectors:List[Any] = []
        
        for id_, blob in blobs:
            arr = np.frombuffer(blob, dtype=np.float32)
            ids.append(id_)
            vectors.append(arr)
        
        if vectors:
        
            vectors = np.vstack(vectors)


            results = self.mrvec.search_by_vector(vector,vectors,ids)
            final_result:List[Dict[str,Any]] = []
            tree_get = self.tree.get
            for id in results:
                node = tree_get(id)
                final_result.append({
                    'name':node.name,
                    'id':node.id,
                })
            return final_result
        return [{
                    'name':"no value found",
                    'id':self.root.id,
                }]

    
    """
        performance table
    """
    def _status(self):
        return f'''
        FS State: Active
        Indexed File: 
        pending tag jobs: 
        pending vector jobs: 
        '''
   
    def _stats(self):
        return f'''
        Indexed File: 
       Average Search Time:
                prifix -> {self.average_prifixS_time}
                extension -> {self.average_extS_time}
                context -> {self.mrvec.average_contextS_time}
        '''

        
    """
    > CONTEXT CHANGE DETECT 
    
    """
    def changes_detector(self,meta:Dict[str,Any]):
        id = meta.get('id')
        path = self.get_path(id)

        old_hash = meta.get('hash')
        new_hash = dependencies.helperfuncUtils.file_hash(path)

        if old_hash != new_hash:
            self.normal_request({"name":'set_indicator',
                                     "para":(id,"c_modified")})
            self.normal_request({"name":'set_hash',
                                     "para":(id,new_hash)})
            if meta.get('ext') in ALLOWED_TAGS_EXT:
                self.normal_request({"name":'set_state',
                                     "para":(id,"pending") })
                self.tag_queue.put(path)
           
    """
    > BACKGROUND TASK AND TAG GENRATION
    
    """
    def urgent_request(self,task:Dict[str,Any])-> None:
        self.db_queue.put((0,next(self.counter),task))

    def normal_request(self,task:Dict[str,Any])-> None:
        self.db_queue.put((10,next(self.counter),task))

    

    def background_index_step1(self):
        if self.tag_result_queue.empty():
            return False     
    
        tag_data = self.tag_result_queue.get()
        data = self.get_node_by_path(tag_data['path'])
        node_:TreeNode = data['result']
        mgs = data['message']
        if node_:
            tags = tag_data['tags']
            if tags:
                vector = self.mrvec.convert_tags_to_vector(tags)
                blob = np.array(vector).astype(np.float32).tobytes()

                self.normal_request({"name":'set_vector',
                                     "para":(node_.id,blob)})
                self.normal_request({"name":'set_tags',
                                     "para":(node_.id,' '.join(tags))})
             
            self.normal_request({"name":'set_state',
                                     "para":(node_.id,"indexed")})
            node_.is_hashed = True
       
            
            self.normal_request({"name":'commit',
                                     "para":()})
            
        return True

    def background_index_step2(self,db:Storage):
       

        if self.rehash_queue.empty():
            return False
    
        path_ = self.rehash_queue.get()
        data = self.get_node_by_path(path_)
        node_ = data['result']
        mgs = data['message']
    
        if node_ and not node_.is_hidden:
            node = db.get_node(node_.id)
            if not node:
                # self.rehash_queue.put(path_)
                return False
            
            meta = FSManager.get_meta(node)
            self.changes_detector(meta)
      
        return True
    
    def background_index_step3(self,storage:Storage):
        if self.db_queue.empty():
            return False
        p,counter,task = self.db_queue.get()
        print('task',task)
        name = task.get('name')
        para = task.get('para')
        event = task.get('event')
        if name:
            getattr(storage,name)(*para)
        if event:
            event.set()
            self.db.commit()
        self.db_queue.task_done()
        return True

  