#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2023 Yeh, Hsin-Hsien <yhh76227@gmail.com>
#
"""
Simple Table Drawer
"""

from dataclasses import dataclass, field
from typing import Any


##############################################################################
### Class Definition


@dataclass(slots=True)
class Bound:
    """
    Parameters
    ----------
    l: str, optional
        Set left bounday symbol. Default is ''.
    r: str, optional
        Set left bounday symbol. Default is ''.
    """
    l:  str = '' 
    r:  str = ''


@dataclass(slots=True)
class Lsh:
    """
    Parameters
    ----------
    dist: int, optional
        Left shift distance. Default is 0.
    sym: str, optional
        Filler symbol. Default is ' '.
    """
    dist: int = 0
    sym:  str = ' '


class Divider:
    """Table divider."""
    def __init__(self, 
                 lsh: Lsh,
                 bound: Bound, 
                 cross: list[str], 
                 col_len: list[int],
                 border: str):
        """
        Arguments
        ---------
        lsh: Lsh
            Shift object to insert shift symbols before draw left bound.
        bound: Bound
            Set left/right boundary symbols.
        cross: list[str]
            Set the cross symbols between 2 columns.
        col_len: list[int]
            length of each column.
        border: str
            Set the border symbols for each column.
        """
        self.lsh = lsh
        self.bound = bound
        self.cross = cross
        self.col_len = col_len
        self.border = border

    def draw(self, file=None):
        """
        Draw divider.

        Arguments
        ---------
        file: {None, file}, optional
            A file-like object (stream) for print(). Default is None.
        """
        print(self.lsh.sym*self.lsh.dist, end='', file=file)
        print(self.bound.l, end='', file=file)
        print(self.border[0]*self.col_len[0], end='', file=file)
        for cr, bo, sz in zip(self.cross, self.border[1:], self.col_len[1:]):
            print('{}{}'.format(cr, bo*sz), end='', file=file)
        print(self.bound.r, file=file)


class Block:
    """Containter of the table data."""
    def __init__(self, 
                 lsh: Lsh, 
                 bound: Bound, 
                 border: list[str], 
                 col_len: list[int], 
                 align: str, 
                 data: list[list[Any]], 
                 divider: None|Divider=None):
        """
        Arguments
        ---------
        lsh: Lsh
            Shift object to insert shift symbols before draw left bound.
        bound: Bound
            Set left/right boundary symbols.
        border: list[str]
            Set the border symbols between 2 columns.
        col_len: list[int]
            length of each column.
        align: str
            Numerical string to set cell align.
        data: list[list[Any]]
            2D data list
        divider: {None, Divider}, optional
            Draw a divider between rows. Default is None which means no divider.
        """
        self.lsh = lsh
        self.bound = bound
        self.border = border
        self.col_len = col_len
        self.align = align
        self.data = data
        self.divider = divider

    def split(self, sep: str='\n', upd_len: bool=False):
        """
        Data line split.

        Arguments
        ---------
        sep: str, optional
            The separator used to split the string. Default is '\\n'.
        upd_len: bool, optional
            Update column length. Default is false.
        """
        if len(self.data) > 1:
            raise ValueError("only one row data can be splitted.")

        max_rows, tmp_data, self.divider = 0, [], None
        for val in self.data[0]:
            if (size:=len(toks:=str(val).split(sep=sep))) > max_rows:
                max_rows = size
            tmp_data.append(toks)

        self.data = [[''] * len(tmp_data) for i in range(max_rows)]
        for c, col in enumerate(tmp_data):
            for r, val in enumerate(col):
                self.data[r][c] = val

        if upd_len:
            self.col_len = [0] * len(self.data[0])
            for row in self.data:
                for c, val in enumerate(row):
                    if (size:=len(val)) > self.col_len[c]:
                        self.col_len[c] = size

    def update_col_len(self):
        for row in self.data:
            for c, col in enumerate(row):
                if (new_len:=len(str(col))) > self.col_len[c]:
                    self.col_len[c] = new_len

    def _fprint(self, data: Any, align: str, col_len, end='\n', file=None):
        """Formatted print."""
        if align == 'c':
            print(str(data).center(col_len), end=end, file=file)
        elif align == 'r':
            print(str(data).rjust(col_len), end=end, file=file)
        else:
            print(str(data).ljust(col_len), end=end, file=file)

    def draw(self, file=None):
        """
        Draw divider.

        Arguments
        ---------
        file: {None, file}, optional
            A file-like object (stream) for print(). Default is None.
        """
        border, align, clen = self.border, self.align, self.col_len
        fprint, last_row = self._fprint, len(self.data) - 1

        for r, row in enumerate(self.data):
            print(self.lsh.sym*self.lsh.dist, end='', file=file)
            print(self.bound.l, end='', file=file)
            fprint(row[0], align[0], clen[0], '', file)
            for bo, val, al, sz in zip(border, row[1:], align[1:], clen[1:]):
                print(bo, end='', file=file)
                fprint(val, al, sz, '', file)
            print(self.bound.r, file=file)
            if self.divider is not None and r != last_row:
                self.divider.draw(file=file)


class SimpleTable:
    """A Simple Text Table Generator."""
    def __init__(self):
        self.table = []

    def draw(self, file=None):
        """
        Draw divider.

        Arguments
        ---------
        file: {None, file}, optional
            A file-like object (stream) for print(). Default is None.
        """
        for obj in self.table:
            obj.draw(file=file)

