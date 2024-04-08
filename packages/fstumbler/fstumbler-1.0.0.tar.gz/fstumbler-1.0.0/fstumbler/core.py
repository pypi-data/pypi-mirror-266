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

import shutil
from typing import Optional
from node import Node
from util import fast_forward


def tumble(root_directory: str) -> Optional[Node]:
    if not os.path.exists(root_directory):
        return None
    
    full_path = os.path.abspath(root_directory)
    name = os.path.basename(full_path)
    root = Node(os.path.dirname(full_path), name)
    pointer = root
    
    for rootname, dirnames, filenames in os.walk(full_path):
        for filename in filenames:
            node = Node(rootname, filename, False)
            pointer.next = node
            pointer = node
        
        for dirname in dirnames:
            node = Node(rootname, dirname)
            pointer.next = node
            pointer = node
    
    return root


def tree(node: Node):
    print(node.full_path)
    if node.next:
        tree(node.next)


def dry_cp(source: Node, destination: Node):
    if not source.directory:
        select = fast_forward(destination, True)
        keep = select.next
        select.next = source.copyWith(select.parent, select.name, False)
        select.next.next = keep
        return
    
    pSrc, pDst = source, fast_forward(destination)
    while pSrc:
        pDst.next = pSrc.copyWith(pDst.full_path if pDst.directory else pDst.parent,
                                  pSrc.name, pSrc.directory)
        pSrc, pDst = pSrc.next, pDst.next


def cp(source: Node, destination: Node):
    if not source.directory:
        select = fast_forward(destination, True)
        keep = select.next
        select.next = source.copyWith(select.parent, select.name, False)
        select.next.next = keep
        shutil.copy(source.full_path, select.next.full_path)
        return
    
    pSrc, pDst = source, fast_forward(destination)
    while pSrc:
        pDst.next = pSrc.copyWith(pDst.full_path if pDst.directory else pDst.parent,
                                  pSrc.name, pSrc.directory)
        
        if pSrc.directory:
            os.makedirs(pDst.next.full_path, exist_ok=True)
        else:
            shutil.copy(pSrc.full_path, pDst.next.full_path)
        pSrc, pDst = pSrc.next, pDst.next
    
