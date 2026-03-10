"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from typing import List,Any
class Stack:
    def __init__(self):
        self.container:List[Any] = []
    
    def push(self,value:Any)->Any:
        self.container.append(value)
        return value
    
    def pop(self)-> Any:
        return self.container.pop(-1)
    
    def top(self)->Any:
        return self.container[-1]

    def empty(self)->bool:
        return True if not self.container else False

