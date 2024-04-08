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

from node import Node

def fast_forward(node: Node, at_edge=False):
    if not at_edge:
        return __fast_forward(node)
    temp = node
    while temp.next and not temp.next.directory:
        temp = temp.next
    return temp

def __fast_forward(node: Node):
    temp = node
    while temp.next:
        temp = temp.next
    return temp
