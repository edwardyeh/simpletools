#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2023 Yeh, Hsin-Hsien <yhh76227@gmail.com>
#

"""
Library for Text Processing
"""

import math
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


##############################################################################
### Class Definition


class Align(IntEnum):
    NONE = 0x00
    TL, TC, TR = 0x11, 0x12, 0x13 
    CL, CC, CR = 0x21, 0x22, 0x23
    BL, BC, BR = 0x31, 0x32, 0x33


class SimpleTable:
    """A Simple Text Table Generator."""

    def __init__(self, heads: dict, sep: str='.', rdiv_cnt: Any=math.inf):
        """
        Arguments
        ---------
        heads     format={key1: title1, key2: title2, ...}.
        sep       the separator use to split the string.
        rdiv_cnt  row divider add between the value of rdiv_cnt (ignore if set 0).
        """
        self._head_cid = {}
        self._table = [[]]
        self._sep = sep
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

        for i, (key, title) in enumerate(heads.items()):
            self._head_cid[key] = i
            col_size = max([len(x) for x in title.split(self._sep)])
            self._table[0].append(self.Head(key, title, col_size))

    @dataclass
    class Cell:
        __slot__ = ['value', 'align']
        value: Any
        align: Align = Align.TL

    @dataclass
    class Head:
        __slot__ = ['key', 'title', 'col_size', 'align']
        key: Any
        title: str
        col_size: int
        align: Align = Align.TL

    @property
    def sep(self) -> str:
        return self._sep

    @property
    def rdiv_cnt(self) -> int:
        return self._rdiv_cnt

    @rdiv_cnt.setter
    def rdiv_cnt(self, rdiv_cnt: int):
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

    @property
    def max_row(self) -> int:
        return len(self._table)

    @property
    def max_col(self) -> int:
        return len(self._table[0])

    def __getitem__(self, index):
        """
        Index Format
        ------------
        <row_st>[:row_ed][:row_step], [col_st[:col_ed][:col_step]]

        Return
        ------
        case1:  return an entry with the entry select.
        case2:  return list with array select.
        """
        if type(index) is tuple:
            rid, cid = index
            if type(rid) is int and type(cid) is int:
                return self._table[rid][cid]
            if type(rid) is slice:
                row_st = 0 if rid.start is None else rid.start
                row_ed = self.max_row if rid.stop is None else rid.stop
                row_step = 1 if rid.step is None else rid.step
            else:
                row_st, row_ed, row_step = rid, rid+1, 1
            if type(cid) is slice:
                col_st = 0 if cid.start is None else cid.start
                col_ed = self.max_col if cid.stop is None else cid.stop
                col_step = 1 if cid.step is None else cid.step
            else:
                col_st, col_ed, col_step = cid, cid+1, 1
        else:
            if type(index) is slice:
                row_st = 0 if index.start is None else index.start
                row_ed = self.max_row if index.stop is None else index.stop
                row_step = 1 if index.step is None else index.step
            else:
                row_st, row_ed, row_step = index, index+1, 1
            col_st, col_ed, col_step = 0, self.max_col, 1

        table = []
        for rid in range(row_st, row_ed, row_step):
            table.append(row:=[])
            for cid in range(col_st, col_ed, col_step):
                row.append(self._table[rid][cid])
        return table 

    def __setitem__(self, index, value):
        if index[0] == 0:
            self._table[index[0]][index[1]].title = value
        else:
            self._table[index[0]][index[1]].value = value

    def update_key(self, cur_key, new_key):
        """Update the key of the header dictionary."""
        if new_key in self._head_cid:
            raise IndexError("The new key is existed.")
        self._table[0][self._head_cid[cur_key]].key = new_key
        self._head_cid[new_key] = self._head_cid[cur_key]
        del self._head_cid[cur_key]

    def add_row(self, data: list, align: int=Align.NONE):
        """
        Add a new row.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        data_size = len(data)
        self._table.append(row:=[])
        for i in range(self.max_col):
            if self.max_row == 2:
                align_ = Align.TL
            elif align == Align.NONE:
                align_ = self._table[-2][i].align
            else:
                align_ = align

            if i < data_size:
                row.append(self.Cell(data[i], align_))
                size = len(str(data[i]))
                if size > self._table[0][i].col_size:
                    self._table[0][i].col_size = size
            else:
                row.append(self.Cell("", align=align_))

    def add_col(self, key, title: str, data: list, align: int=Align.TL):
        """
        Add a new column.
        
        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        data_size = len(data)
        self._head_cid[key] = self.max_col
        col_size = max([len(x) for x in title.split(self._sep)])
        self._table[0].append(self.Head(key, title, col_size))
        for i in range(1, self.max_row):
            if i < data_size:
                self._table[i].append(self.Cell(data[i-1], align))
                size = len(str(data[i-1]))
                if size > self._table[0][-1].col_size:
                    self._table[0][-1].col_size = size
            else:
                self._table[i].append(self.Cell(align=align))

    def swap_row(self, index1: int, index2: int):
        """
        Swap two specific rows.

        Argument index1, index2 should be row IDs.
        """
        if index1 == 0 or index2 == 0:
            raise IndexError("The header row cannot be swapped.")
        self._table[index1], self._table[index2] = (
            self._table[index2], self._table[index1]
        )

    def swap_col(self, index1, index2):
        """
        Swap two specific columns.

        Argument index1, index2 can be row IDs or keys.
        """
        cid1 = self._head_cid[index1] if type(index1) == str else index1
        cid2 = self._head_cid[index2] if type(index2) == str else index2
        self._head_cid[self._table[0][cid1].key] = cid2
        self._head_cid[self._table[0][cid2].key] = cid1
        for i in range(self.max_row):
            self._table[i][cid1], self._table[i][cid2] = (
                self._table[i][cid2], self._table[i][cid1]
            )

    def del_row(self, index: int):
        """
        Delete the specific row

        Argument index should be row IDs
        """
        if index != 0 and self.max_row > 1:
            del self._table[index]

    def del_col(self, index):
        """
        Delete the specific column.

        Argument index can be row IDs or keys.
        """
        cid = self._head_cid[index] if type(index) == str else index
        del self._head_cid[self._table[0][cid].key]
        for i in range(self.max_row):
            del self._table[i][cid]
        if self.max_col == 0:
            self._table = [[self.Head('title1', 'Title1', 6)]]
            self._head_cid['title1'] = 0
        else:
            for i, head in enumerate(self._table[0]):
                self._head_cid[head.key] = i

    def set_row_align(self, index: int, align: Align):
        """
        Set the align type of a row.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        Argument index should be row IDs.
        """
        for i in range(self.max_col):
            self._table[index][i].align = align

    def set_col_align(self, index, align: Align):
        """
        Set the align type of a column.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        Argument index can be row IDs or keys.
        """
        cid = self._head_cid[index] if type(index) == str else index
        for i in range(1, self.max_row):
            self._table[i][cid].align = align

    def get_keys(self) -> list:
        """Get the header of the table."""
        return [x.key for x in self._table[0]]

    def get_titles(self) -> list:
        """Get the header of the table."""
        return [x.title for x in self._table[0]]

    def get_values(self) -> list:
        """Get the values of the table content."""
        table = []
        for r in range(1, self.max_row):
            table.append(row:=[])
            for c in range(self.max_col):
                row.append(self._table[r][c].value)
        return table

    def get_row(self, index: int) -> list:
        """
        Get values of the specific row.

        Argument index should be row IDs.
        """
        if index > 0:
            return [cell.value for cell in self._table[index]]
        else:
            return [head.title for head in self._table[index]]

    def get_col(self, index) -> list:
        """
        Get values of the specific column.

        Argument index can be row IDs or keys.
        """
        cid = self._head_cid[index] if type(index) == str else index
        col = []
        for i in range(1, self.max_row):
            col.append(self._table[i][cid].value)
        return col

    def print_table(self, fp=None, sid=1):
        """
        Print the table.

        Arguments
        ---------
        fp      file out of print function. (default=None)
        sid     table style select.         (default=1)
        """
        match sid:
            case 1:
                div_edg, div_sep = '+', '+'
                val_edg, val_sep = '|', '|'
            case 2:
                div_edg, div_sep = '', ' '
                val_edg, val_sep = '', ' '
            case _:
                raise SyntaxError(f"The table style is undefined (sid={sid}).")

        # divider
        str_div = f"{div_edg}"
        for c in range(self.max_col):
            str_div += "-{}-{}".format('-' * self._table[0][c].col_size, div_sep) 
        str_div = str_div[:-1] + div_edg
        print(str_div, file=fp)

        # header
        data, row_cnt, max_row = [], [], 0
        for c in range(self.max_col):
            data.append(self._table[0][c].title.split(self._sep))
            row_cnt.append(len(data[-1]))
        max_row = max(row_cnt)

        row_st, row_ed = [], []
        for c in range(self.max_col):
            match self._table[0][c].align:
                case Align.TL | Align.TC | Align.TR:
                    row_st.append(0)
                    row_ed.append(row_cnt[c])
                case Align.CL | Align.CC | Align.CR:
                    row_st.append(int((max_row-row_cnt[c])/2))
                    row_ed.append(row_st[c]+row_cnt[c])
                case Align.BL | Align.BC | Align.BR:
                    row_st.append(max_row-row_cnt[c])
                    row_ed.append(max_row)
                case _:
                    tag = self._table[0][c].align
                    raise SyntaxError(f"The align ID is undefined ({tag}).")

        for r in range(max_row):
            str_ = f"{val_edg}"
            for c in range(self.max_col):
                if row_st[c] <= r < row_ed[c]:
                    str2 = data[c][r-row_st[c]]
                    match self._table[0][c].align:
                        case Align.TL | Align.CL | Align.BL:
                            str2 = str2.ljust(self._table[0][c].col_size)
                        case Align.TC | Align.CC | Align.BC:
                            str2 = str2.center(self._table[0][c].col_size)
                        case Align.TR | Align.CR | Align.BR:
                            str2 = str2.rjust(self._table[0][c].col_size)
                        case _:
                            tag = self._table[0][c].align
                            raise SyntaxError(f"The align ID is undefined ({tag}).")
                else:
                    str2 = ' ' * self._table[0][c].col_size
                str_ += f" {str2} {val_sep}"
            str_ = str_[:-1] + val_edg
            print(str_, file=fp)

        # divider
        print(str_div, file=fp)

        # content
        row_cnt = 0
        for r in range(1, self.max_row):
            if row_cnt == self._rdiv_cnt:
                row_cnt = 1
                # content divider
                print(str_div, file=fp)
            else:
                row_cnt = row_cnt + 1

            str_ = f"{val_edg}"
            for c in range(self.max_col):
                str2 = str(self._table[r][c].value)
                match self._table[r][c].align:
                    case Align.TL | Align.CL | Align.BL:
                        str2 = str2.ljust(self._table[0][c].col_size)
                    case Align.TC | Align.CC | Align.BC:
                        str2 = str2.center(self._table[0][c].col_size)
                    case Align.TR | Align.CR | Align.BR:
                        str2 = str2.rjust(self._table[0][c].col_size)
                    case _:
                        tag = self._table[0][c].align
                        raise SyntaxError(f"The align ID is undefined ({tag}).")
                str_ += f" {str2} {val_sep}"
            str_ = str_[:-1] + val_edg
            print(str_, file=fp)

        # divider
        print(str_div, file=fp)


