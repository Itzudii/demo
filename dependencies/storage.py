"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
import sqlite3
from typing import Optional,List,Any,Tuple,Dict
from numpy import ndarray

DB_PATH = ".database/fs_index.db"
import logging
logger = logging.getLogger("FS")
class Storage:
    def __init__(self):
        logger.info('Storage init...')
        path = DB_PATH
        self.conn = sqlite3.connect(path, timeout=30, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()
        # self._create_metadata_table()
       
    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY ,
            name TEXT,
            path TEXT,
            type TEXT,
            state TEXT,
            indicator TEXT,
            islocked INTEGER,
            locked_hash TEXT,
            ext TEXT,
            hash TEXT,
            vector BLOB,
            tags TEXT,
            size INTEGER,
            modified_time TEXT,
            created_time TEXT,
            mode TEXT,
            parent_id INTEGER
        )
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext ON nodes(ext)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON nodes(name)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent ON nodes(parent_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON nodes(hash)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON nodes(tags)")
        self.cursor.execute("PRAGMA journal_mode=WAL;")

        self.conn.commit()

    def _create_metadata_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata   (
            key TEXT PRIMARY KEY ,
            value INTEGER
        )
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_key ON metadata(key)")
        self.cursor.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES ("last_id", 0);')
        self.conn.commit()

    
    def set_last_id(self, new_id:int):
        self.cursor.execute(
            "UPDATE metadata SET value=? WHERE key='last_id'",
            (new_id,)
        )
        self.conn.commit()


    def get_next_id(self):
        self.cursor.execute("SELECT MAX(id) FROM nodes")
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1


    def commit(self):
        self.conn.commit()

    def get_tree_structure(self):
        """
        Returns list of tuples:
        [(id, name, parent_id), ...]
        """
        self.cursor.execute("SELECT id, name, parent_id,type,modified_time,size,islocked,indicator,state,ext FROM nodes")
        return self.cursor.fetchall()
    
    def get_all_blobs(self):
        """
        """
        self.cursor.execute("""SELECT id, vector FROM nodes WHERE vector IS NOT NULL""")
        return self.cursor.fetchall()


    def add_node(self,id:int, name:str, path:str, type_:str, parent_id:Optional[int]=None, ext:Optional[str]=None, tags:Optional[List[str]]=None,
                 hash_:Optional[str]=None, vector:Optional[ndarray]=None, size:int=0, modified_time:Optional[float]=None, created_time:Optional[float]=None, mode:Optional[int]=None):
        # node_id = type_+uuid.uuid4().hex
        state = "pending"
        indicator = "sync"
        islocked = 0
        locked_hash = None
        self.cursor.execute("""
        INSERT INTO nodes (name, path, type, state, indicator, islocked, locked_hash, ext, hash, vector, tags, size, modified_time, created_time, mode, parent_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ( name, path, type_, state, indicator, islocked, locked_hash, ext, hash_, vector, tags, size, modified_time, created_time, mode, parent_id))
        # self.conn.commit()
        return self.cursor.lastrowid
    
    def batch_add(self,nodes:List[Tuple[Any,...]]):
        # state = "pending"
        # indicator = "sync"
        # islocked = 0
        # locked_hash = None
        # created_time = created_time or time.strftime("%Y-%m-%d %H:%M:%S")
        # modified_time = modified_time or created_time
        self.cursor.executemany("""
        INSERT INTO nodes (id ,name, path, type, state, indicator, islocked, locked_hash, ext, hash, vector, tags, size, modified_time, created_time, mode, parent_id)
         VALUES (?, ?, ?, ?, 'pending', 'sync', 0,Null , ?,Null ,Null ,Null , ?, ?, ?, ?,?)
        """, nodes)
        # self.conn.commit()
        return self.cursor.lastrowid

    # Fetch full node attributes by UUID
    def get_node(self, node_id:int):
        self.cursor.execute("SELECT * FROM nodes WHERE id=?", (node_id,))
        return self.cursor.fetchone()
    
    # Fetch full node attributes by parentid
    def get_node_by_parent(self, parent_id:int)->List[Tuple[Any]]:
        self.cursor.execute("SELECT * FROM nodes WHERE parent_id=?", (parent_id,))
        return self.cursor.fetchall()

    # Prefix search
    def search_prefix(self, prefix:str, type_:Optional[str]=None, parent_id:Optional[int]=None, limit:Optional[int]=None):
        query = "SELECT id FROM nodes WHERE name LIKE ?"
        params:List[Any] = [prefix + "%"]

        if type_ is not None:
            query += " AND type=?"
            params.append(type_)

        if parent_id is not None:
            query += " AND parent_id=?"
            params.append(parent_id)

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()


    # Hash search
    def search_hash(self, hash_:str):
        self.cursor.execute("SELECT id, name FROM nodes WHERE hash=?", (hash_,))
        return self.cursor.fetchall()

    def duplicates_hash(self):
        """
        Returns duplicate files grouped by hash.
        Output format:
        {
            "hash1": [id1, id2, id3],
            "hash2": [id4, id5]
        }
        """

        query = """
        SELECT n.hash, n.id, n.name
        FROM nodes n
        JOIN (
            SELECT hash
            FROM nodes
            WHERE hash IS NOT NULL
            AND type='f'
            GROUP BY hash
            HAVING COUNT(*) > 1
        ) d
        ON n.hash = d.hash
        WHERE n.type='f'
        ORDER BY n.hash
        """

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        duplicates:Dict[str,List[Tuple[int,str]]] = {}

        for file_hash, file_id, file_name in rows:
            duplicates.setdefault(file_hash, []).append((file_id,file_name))

        return duplicates

    
    def get_empty_hash(self):
        self.cursor.execute("SELECT id FROM nodes WHERE hash IS NULL AND type='f'")
        return self.cursor.fetchall()
    
    def get_empty_tags(self,exts:List[str]):
        # exts = ('txt', 'pdf', 'doc')
        query = f"""
            SELECT id FROM nodes
            WHERE tags IS NULL
            AND ext IN ({','.join(['?']*len(exts))})
        """
        self.cursor.execute(query, exts)
        return self.cursor.fetchall()


    # Close DB
    def close(self):
        self.conn.close()


     # -----------------------
    # Node setters
    # -----------------------
    def set_vector(self, node_id:int, vector:Any):
        """Store or update vector for a node."""
        self.cursor.execute("UPDATE nodes SET vector=? WHERE id=?", (vector, node_id))
        # self.conn.commit()

    def set_indicator(self, node_id:int, indicator:str):
        """Store or update vector for a node."""
        self.cursor.execute("UPDATE nodes SET indicator=? WHERE id=?", (indicator, node_id))
        

    def set_tags(self, node_id:int, tags:List[str]):
        """Store or update tags for a node."""
        self.cursor.execute("UPDATE nodes SET tags=? WHERE id=?", (tags, node_id))
        # self.conn.commit()

    def set_hash(self, node_id:int, hash_:str):
        """Store or update hash for a node."""
        self.cursor.execute("UPDATE nodes SET hash=? WHERE id=?", (hash_, node_id))
        # self.conn.commit()

    def set_size(self, node_id:int, size:int):
        self.cursor.execute("UPDATE nodes SET size=? WHERE id=?", (size, node_id))
      

    def set_modified_time(self, node_id:int, modified_time:float):
        self.cursor.execute("UPDATE nodes SET modified_time=? WHERE id=?", (modified_time, node_id))
 

    def set_locked(self, node_id:int, locked:bool=True):
        """Lock or unlock a node."""
        self.cursor.execute("UPDATE nodes SET islocked=? WHERE id=?",
                            (int(locked), node_id))
        self.conn.commit()
    
    def set_name(self, node_id:int, name:str):
        self.cursor.execute("UPDATE nodes SET name=? WHERE id=?", (name, node_id))
        self.conn.commit()

    def set_state(self, node_id:int, state:str):
        self.cursor.execute("UPDATE nodes SET state=? WHERE id=?", (state, node_id))

    def set_parent(self, node_id:int, p_id:int):
        self.cursor.execute("UPDATE nodes SET parent_id=? WHERE id=?", (p_id, node_id))
        # self.conn.commit()

    # -----------------------
    # Node getters
    # -----------------------
    def get_vector(self, node_id:int):
        self.cursor.execute("SELECT vector FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_parent_id(self, node_id:int):
        self.cursor.execute("SELECT parent_id FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_tags(self, node_id:int):
        self.cursor.execute("SELECT tags FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_hash(self, node_id:int):
        self.cursor.execute("SELECT hash FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_id_by_hash(self, hash:str):
        self.cursor.execute("SELECT id FROM nodes WHERE hash=?", (hash,))
        return self.cursor.fetchall()
    
    def get_modified_time(self, node_id:int):
        self.cursor.execute("SELECT modified_time FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_size(self, node_id:int):
        self.cursor.execute("SELECT size FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_path(self, node_id:int):
        self.cursor.execute("SELECT path FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_islocked(self, node_id:int):
        self.cursor.execute("SELECT islocked FROM nodes WHERE id=?", (node_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    # -----------------------
    # multiple set
    # -----------------------
    def set_vectors_batch(self, updates:List[Tuple[int,Any]]):
        """
        updates = [(uuid1, vector1), (uuid2, vector2), ...]
        """
        self.cursor.executemany("UPDATE nodes SET vector=? WHERE id=?", updates)
        self.conn.commit()

    def delete_ids_helper(self,ids:List[int]):
        placeholders = ",".join("?" * len(ids))
        query = f"DELETE FROM nodes WHERE id IN ({placeholders})"
        self.cursor.execute(query,ids)
        self.conn.commit()

    def delete_ids(self,ids:List[int]):
        def chunked(iterable, size):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]
        for chunk in chunked(ids, 900):
            self.delete_ids_helper(chunk)


        

    