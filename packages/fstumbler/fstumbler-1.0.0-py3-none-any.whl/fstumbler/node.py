#
#   This file is part of the fstumbler library.
#   Copyright (C) 2024  Ferit Yiğit BALABAN
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#   
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#   
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#   USA.

import os

from typing import Optional


class Node:  
    def __init__(self, parent: str, name: str, directory=True):
        self.directory = directory
        self.name = name
        self.next: Optional[Node] = None
        self.parent = parent
 
 
    def __str__(self):
        return self.full_path
    
    
    @property
    def full_path(self):
        return os.path.join(self.parent, self.name)
    
    
    def elements(self):
        if self.directory: 
            next = self.next
            count = 0
            while next:
                count += 1
                next = next.next
                if next and next.directory:
                    count += 1
                    break
            return count
        return -1


    def copy(self):
        return Node(self.parent, self.name, self.directory)

    def copyWith(self, parent: str, name: str, directory=True):
        return Node(parent if parent else self.parent,
                    name if name else self.name, directory)
