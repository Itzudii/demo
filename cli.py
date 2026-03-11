"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from fsmanager import FSManager
import dependencies.helperfuncUtils

import os
import logging
from typing  import Dict,Any

logger = logging.getLogger("FS")

def cli_result(success:bool,result:str,islist)->Dict[str,Any]:
    return {
        "success":success,
        "result":result,
        'islist': islist
    }
class CliPerformer:
    def __init__(self,fs:FSManager) -> None:
        logger.info('CliPerformer init...')
        self.fs = fs

    # ------------------------------
    # Helpers
    # ------------------------------
    
    def ok(self, msg:str,islist = False):
        return cli_result(True, msg, islist)
    
    def error(self, msg:str,islist = False):
        return cli_result(False, msg, islist)
    
    # ------------------------------
    # Commands
    # ------------------------------

    def _ls(self,command:str):
        base = command.split()
        if len(base) == 1:
            return self.ok(f'{'\n'.join(list(self.fs.cwd.childs.keys()))}')
        else:
            return self.error(f'not a valid command , what do you mean by- -->[{base[1]}]')

    def _cd(self,command):
        try:
            c,name = command.strip().split(" ",1)
            if name == './':
                self.fs.go_back()
                return  self.ok(f'{self.fs.get_cwd()}')
            else:
                isDone = self.fs.go_to(name)
                if isDone:
                    return  self.ok(f'{self.fs.get_cwd()}')
                else:
                    return self.error(f'{name} not found')
        except Exception:
            return self.error(f'try cd help')

    def _pwd(self, command):
        base = command.split()
        if len(base) == 1:
            return self.ok(self.fs.cwd.path)
        return self.error(f'Invalid argument: {base[1]}')


    def _prd(self, command):
        base = command.split()
        if len(base) == 1:
            return self.ok(self.fs.root.path)
        return self.error(f'Invalid argument: {base[1]}')


    def _refresh(self, command):
        base = command.split()

        if len(base) == 1:
            self.fs.refresh_cwd()
            return self.ok('Refreshed current directory')

        if len(base) == 2 and base[1] == '--deep':
            self.fs.refresh_root()
            return self.ok(f'Full refresh from root: {self.fs.root.path}')

        return self.error(f'Invalid argument: {base[1] if len(base) > 1 else ""}')


    def _open(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            FSManager._open_file_with_default_app(path)
            return self.ok(f'Opened: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _cut(self, command):
        return self.error('Not available yet')


    def _copy(self, command):
        return self.error('Not available yet')


    def _del(self, command):
        try:
            _, path = command.strip().split(" ", 1)
        except Exception as e:
            logger.error(f'{e}')
            return self.error(f"{command} not valid")

        data = self.fs.get_node_by_path(path)
        node = data['result']
        msg = data['message']

        if node:
            self.fs.delete_node(node)
            return self.ok(f'{path} deleted successfully')

        return self.error(f'{msg}, use "/" instead of "\\"')


    def _mkdir(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            os.makedirs(path)
            return self.ok(f'Directory created: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _mkf(self, command):
        try:
            _, path, content = command.strip().split(" ", 2)
            FSManager._write_content_to_file(path, content)
            return self.ok(f'File created: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _append(self, command):
        try:
            _, path, content = command.strip().split(" ", 2)
            FSManager._append_content_to_file(path, content)
            return self.ok(f'Content appended to: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _info(self, command):
        # try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node_ = data['result']
            msg = data['message']

            if node_:
                node = self.fs.db.get_node(node_.id)
                meta = FSManager.get_meta(node)
                result = (
                    f'id: {meta.get('id')}',
                    f'name: {meta.get('name')}',
                    f'path: {meta.get('path')}',
                    f'type: {meta.get('type')}',
                    f'state: {meta.get('state')}',
                    f'indicator: {meta.get('indicator')}',
                    f'islocked: {meta.get('islocked')}',
                    f'locked_hash: {meta.get('locked_hash')}',
                    f'ext: {meta.get('ext')}',
                    f'hash: {meta.get('hash')}',
                    f'vector: {meta.get('vector')}',
                    f'tags: {meta.get('tags')}',
                    f'size: {dependencies.helperfuncUtils.bytes_to_mb(meta.get('size'))} MB',
                    f'modified_time: {dependencies.helperfuncUtils.formate_sttime(meta.get('modified_time'))}',
                    f'created_time: {dependencies.helperfuncUtils.formate_sttime(meta.get('created_time'))}',
                    f'mode: {dependencies.helperfuncUtils.filemode_readable(dependencies.helperfuncUtils.get_filemode(int(meta.get('mode'))))}',
                    f'parent_id: {meta.get('parent_id')}',
                )
                return self.ok(result,True)

            return self.error(msg)

        # except Exception as e:
        #     logger.error(f'{e}')
        #     return self.error(str(e))


    def _rename(self, command):
        return self.error('Not available yet')


    def _tree(self, command):
        return self.error('Not available yet')


    def _search(self, command):
        return self.error('Not available yet')


    def _find(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node = data['result']
            msg = data['message']

            if node:
                paths = self.fs.search_paths_by_hash(node.hash)
                if paths:
                    joined = "\n".join(paths)
                    return self.ok(f'total:{len(paths)}\n{joined}')
                return self.ok('total:0\nNo duplicates found')

            return self.error(msg)

        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _tag(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node = data['result']
            msg = data['message']

            if node:
                tags = self.fs.tagG.generate_tags_path(path)
                return self.ok(' '.join(tags))

            return self.error(msg)

        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _verify(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node = data['result']
            msg = data['message']

            if node:
                data = self.fs.is_corupted(node)
                return self.ok(data['status'])

            return self.error(msg)

        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _hash(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node = data['result']
            msg = data['message']

            if node:
                return self.ok(node.hash)

            return self.error(msg)

        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _dup(self, command):
        base = command.split()

        if len(base) == 1:
            data = self.fs.search_duplicate_files()

            if not data:
                return self.ok("No duplicates found")

            string = ''
            for hash_, paths in data.items():
                joined = "\n   |--->".join(paths)
                string += f'hash:{hash_}\n   |--->{joined}\n\n'

            return self.ok(string)

        return self.error(f'Invalid argument: {base[1]}')


    def _status(self, command):
        base = command.split()
        if len(base) == 1:
            return self.ok(self.fs._status())
        return self.error(f'Invalid argument: {base[1]}')


    def _stats(self, command):
        base = command.split()
        if len(base) == 1:
            return self.ok(self.fs._stats())
        return self.error(f'Invalid argument: {base[1]}')

    def _help(self, command):
        help_data = {
            "ls": "ls\n    List files and folders in current directory",

            "cd": "cd <path>\n    Change directory\n    cd folder\n    cd ./   (go back)",

            "pwd": "pwd\n    Show current working directory",

            "prd": "prd\n    Show root directory path",

            "refresh": "refresh\n    Refresh current directory\n    refresh --deep  (refresh full filesystem from root)",

            "open": "open <path>\n    Open file with default application",

            "cut": "cut <source> <destination>\n    Move file or folder (not implemented yet)",

            "copy": "copy <source> <destination>\n    Copy file or folder (not implemented yet)",

            "del": "del <path>\n    Delete file or directory",

            "mkdir": "mkdir <path>\n    Create new directory",

            "mkf": "mkf <path> <content>\n    Create file and write content",

            "append": "append <path> <content>\n    Append content to existing file",

            "info": "info <path>\n    Show metadata about file or folder",

            "rename": "rename <old_path> <new_name>\n    Rename file or folder (not implemented yet)",

            "tree": "tree\n    Show directory structure (not implemented yet)",

            "search": "search <name>\n    Search files by name (not implemented yet)",

            "find": "find <path>\n    Find duplicate files using hash",

            "tag": "tag <path>\n    Generate tags for file",

            "verify": "verify <path>\n    Check if file is corrupted",

            "hash": "hash <path>\n    Show file hash",

            "dup": "dup\n    Find duplicate files in filesystem",

            "status": "status\n    Show filesystem status",

            "stats": "stats\n    Show filesystem statistics",

            "help": "help\n    Show all commands\n    help <command>  (show help for one command)"
        }

        base = command.split()

        # show all commands
        if len(base) == 1:
            # text = "Available commands:\n\n"
            # for cmd, desc in help_data.items():
            #     text += f"{desc}\n\n"
            return self.ok([f'{cmd}:{desc}' for cmd, desc in help_data.items()],True)

        # show help for one command
        cmd = base[1]
        if cmd in help_data:
            return self.ok(help_data[cmd])

        return self.error(f"No help available for '{cmd}'")


    def process_user_task(self,command):
        base = command.split()[0]
        
        commands = {
            "ls":self._ls,
            "cd":self._cd,
            "pwd":self._pwd,
            "prd":self._prd,
            "refresh":self._refresh,
            "open":self._open,
            "cut":self._cut,
            "copy":self._copy,
            "del":self._del,
            "mkdir":self._mkdir,
            "mkf":self._mkf,
            "append":self._append,
            "info":self._info,
            "rename":self._rename,
            "tree":self._tree,
            "search":self._search,
            "find":self._find,
            "tag":self._tag,
            "verify":self._verify,
            "hash":self._hash,
            "dup":self._dup,
            "status":self._status,
            "stats":self._stats,
            "help":self._help
        }
        output = commands.get(base, lambda c: f'{c} not found')(command)

        if output is not None:
            return output 
        return self.error('output is not catch! error in inbuild methods')


    def run_command(self,command):
            logger.info(f"[INPUT CAPTURED] -> {command}")
            self.last_input = command
            return self.process_user_task(command)

