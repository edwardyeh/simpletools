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
                 col_len: list[int],
                 border: None|str = None,
                 cross: None|list[str] = None,
                 bound: None|Bound = None, 
                 lsh: None|Lsh = None):
        """
        Arguments
        ---------
        col_len: list[int]
            length of each column.
        border: {None, str}, optional
            Set the border symbols for each column. Default is '-'
        cross: {None, list[str]}, optional
            Set the cross symbols between 2 columns. Default is '-+-'.
        bound: {None, Bound}, optional
            Set left/right boundary symbols. Default is left='+-', right='-+'.
        lsh: {None, Lsh}, optional
            Shift object to insert shift symbols before draw left bound.
            Default is w/o left shift.
        """
        num = len(col_len)
        self.col_len = col_len
        self.border = '-' * num if border is None else border
        self.cross = ['-+-'] * (num-1) if cross is None else cross
        self.bound = Bound('+-', '-+') if bound is None else bound
        self.lsh = Lsh() if lsh is None else lsh

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
                 data: list[list[Any]], 
                 col_len: None|list[int] = None, 
                 fs: None|list[str] = None,
                 align: None|str = None, 
                 fill: None|str = None,
                 cross: None|list[str] = None,
                 bound: None|Bound = None, 
                 lsh: None|Lsh = None, 
                 divider: None|Divider=None,
                 div_cnt: int=1):
        """
        Arguments
        ---------
        data: list[list[Any]]
            2D data list
        col_len: {None, list[int]}, optional
            length of each column. Default is 1.
        fs: {None, list[str]}, optional
            Set format string for each column. Default is '{}'.
        align: {None, str}, optional
            Numerical string to set cell align. Default if left align.
        fill: {None, str}, optional
            Set fill char for each column. Default is ' '.
        cross: {None, list[str]}, optional
            Set the cross symbols between 2 columns. Default is ' | '.
        bound: {None, Bound}, optional
            Set left/right boundary symbols. Default is left='| ', right=' |'.
        lsh: {None, Lsh} optional
            Shift object to insert shift symbols before draw left bound.
            Default is w/o left shift.
        divider: {None, Divider}, optional
            Draw a divider between rows. Default is None which means no divider.
        div_cnt: int, optional
            Number of rows between divider. Default is 1.
        """
        num = len(data[0])
        self.data = data
        self.col_len = [1] * num if col_len is None else col_len
        self.fs = ['{}'] * num if fs is None else fs
        self.align = 'l' * num if align is None else align
        self.fill = ' ' * num if fill is None else fill
        self.cross = [' | '] * (num-1) if cross is None else cross
        self.bound = Bound('| ', ' |') if bound is None else bound
        self.lsh = Lsh() if lsh is None else lsh
        self.divider = divider
        self.div_cnt = div_cnt

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

    def _fprint(self, data: Any, clen: int, fs: str, align: str, fill: str,
                end='\n', file=None):
        """Formatted print."""
        if align == 'c':
            print(fs.format(data).center(clen, fill), end=end, file=file)
        elif align == 'r':
            print(fs.format(data).rjust(clen, fill), end=end, file=file)
        else:
            print(fs.format(data).ljust(clen, fill), end=end, file=file)

    def draw(self, file=None):
        """
        Draw divider.

        Arguments
        ---------
        file: {None, file}, optional
            A file-like object (stream) for print(). Default is None.
        """
        clen, fs, align, fill = self.col_len, self.fs, self.align, self.fill
        cross, bound, lsh = self.cross, self.bound, self.lsh
        divider, dcnt = self.divider, 1
        fprint, last_row = self._fprint, len(self.data)-1

        for r, row in enumerate(self.data):
            if len(row) == 0:
                continue
            print(lsh.sym * lsh.dist, end='', file=file)
            print(bound.l, end='', file=file)
            fprint(row[0], clen[0], fs[0], align[0], fill[0], '', file)
            for c, va in enumerate(row[1:], 1):
                print(cross[c-1], end='', file=file)
                fprint(va, clen[c], fs[c], align[c], fill[c], '', file)
            print(bound.r, file=file)
            if divider is not None:
                if dcnt == self.div_cnt and r != last_row:
                    dcnt = 1
                    divider.draw(file=file)
                else:
                    dcnt += 1


class SimpleTable:
    """A Simple Text Table Generator."""
    def __init__(self, data: list[Divider|Block]=None):
        self.table = [] if data is None else data

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


