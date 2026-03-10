"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from dependencies.useful import filemode_readable,formate_sttime
from fsmanager import FSManager

import os
import logging
from typing  import Dict,Any

logger = logging.getLogger("FS")

def cli_result(success:bool,result:str)->Dict[str,Any]:
    return {
        "success":success,
        "result":result
    }
class CliPerformer:
    def __init__(self,fs:FSManager) -> None:
        logger.info('CliPerformer init...')
        self.fs = fs

    # ------------------------------
    # Helpers
    # ------------------------------
    
    def ok(self, msg:str):
        return cli_result(True, msg)
    
    def error(self, msg:str):
        return cli_result(False, msg)
    
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
            self.fs._open_file_with_default_app(path)
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
            self.fs._write_content_to_file(path, content)
            return self.ok(f'File created: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _append(self, command):
        try:
            _, path, content = command.strip().split(" ", 2)
            self.fs._append_content_to_file(path, content)
            return self.ok(f'Content appended to: {path}')
        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


    def _info(self, command):
        try:
            _, path = command.strip().split(" ", 1)
            data = self.fs.get_node_by_path(path)
            node = data['result']
            msg = data['message']

            if node:
                result = (
                    f'\npath: {node.path}'
                    f'\nname: {node.name}'
                    f'\nchilds: {node.childs}'
                    f'\ntype: {node.type}'
                    f'\nstate: {node.state}'
                    f'\ninner_state: {node.inner_state}'
                    f'\nislocked: {node.islocked}'
                    f'\nlock_hash: {node.lock_hash}'
                    f'\nhash: {node.hash}'
                    f'\nvector: {node.vector}'
                    f'\ntags: {node.tags}'
                    f'\nsize: {node.size}'
                    f'\nmodified_time: {formate_sttime(node.modified_time)}'
                    f'\ncreated_time: {formate_sttime(node.created_time)}'
                    f'\nmode: {filemode_readable(node.mode)}'
                )
                return self.ok(result)

            return self.error(msg)

        except Exception as e:
            logger.error(f'{e}')
            return self.error(str(e))


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
            "stats":self._stats
            # "help":self._help
        }
        output = commands.get(base, lambda c: f'{c} not found')(command)

        if output is not None:
            return output 
        return self.error('output is not catch! error in inbuild methods')


    def run_command(self,command):
            logger.info(f"[INPUT CAPTURED] -> {command}")
            self.last_input = command
            return self.process_user_task(command)

