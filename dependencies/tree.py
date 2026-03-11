"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
import dependencies.helperfuncUtils 
from dependencies.storage import Storage


from collections import defaultdict
from typing import Dict,DefaultDict,Optional,Tuple,List
from typing import Optional,Dict
import logging
logger = logging.getLogger("FS")
class TreeNode:
    __slots__ = ("id","name","ext","childs","parent","size","m_time","indicator","is_dir","is_hashed","is_locked","is_hidden")
    def __init__(self,name:str,is_dir:bool):
        self.id:Optional[int] = None
        self.name:str = name
        data = dependencies.helperfuncUtils.name_ext(name)
        self.ext:str = data.get('ext','')

        self.childs:Optional[Dict[str,TreeNode]] = {} if is_dir else None
        self.parent:Optional[TreeNode] = None

        self.size:int = 0
        self.m_time:float = 0

        self.indicator:str = 'sync'

        self.is_dir:bool = is_dir
        self.is_hashed:bool = False
        self.is_locked:bool = False
        self.is_hidden:bool = data.get('ishidden',False)

class Tree:
    def __init__(self):
        self.root = None
        self.id_to_node:Dict[int,TreeNode] = dict()
        self.ext_to_node:DefaultDict[str,List[TreeNode]] = DefaultDict()

    def get(self,id:Optional[int]) -> Optional[TreeNode]:
        return self.id_to_node.get(id) if id else None
    
    def set(self,id:int,node:TreeNode) -> None:
         self.id_to_node[id] = node

    def get_ext(self,ext:str)-> list[int|None]:
        lst = self.ext_to_node.get(ext)
        if lst:
            return [node.id for node in lst]
        return []

       
    def load_from_db(self, storage:Storage):
        """
        Load tree structure from DB
        """
        logger.info("Loading tree from DB...")
        rows = storage.get_tree_structure()

        
        id_to_node:Dict[int,TreeNode] = dict()
        child_links:List[Tuple[int,TreeNode]] = list() # (parent_id, child_node)
        ext_to_node:DefaultDict[str,List[TreeNode]] = defaultdict(list)

        # 1. Create all nodes
        for row in rows:
            # row: (id, name, parent_id, type)
            node_id = row[0]
            name = row[1]
            parent_id = row[2]
            type_ = row[3]
            m_time = row[4]
            size = row[5]
            is_locked = row[6]
            indicator = row[7]
            is_hashed = True if row[8] == 'indexed' else False
            ext = row[9]

            
            is_dir = (type_ == 'd')
            node = TreeNode(name, is_dir)
            node.id = node_id
            node.m_time = m_time
            node.size = size
            node.is_locked = is_locked
            node.indicator = indicator
            node.is_hashed = is_hashed
            node.is_hidden
            node.ext = ext
            id_to_node[node_id] = node
            ext_to_node[node.ext].append(node)
            
            if parent_id is not None:
                child_links.append((parent_id, node))
            else:
                self.root = node # Found root (no parent)

        # 2. Link children to parents
        for p_id, child_node in child_links:
            parent_node = id_to_node.get(p_id)
            if parent_node:
                child_node.parent = parent_node
                if parent_node.childs is None:
                     parent_node.childs = {}
                if parent_node.is_hidden:
                    child_node.is_hidden = True
                parent_node.childs[child_node.name] = child_node
            else:
                logger.error(f"Orphan node found: {child_node.name} (parent_id: {p_id})")

        logger.info("Tree loaded from DB.")
        if id_to_node:
            self.id_to_node = id_to_node
        if ext_to_node:
            self.ext_to_node = ext_to_node
        

