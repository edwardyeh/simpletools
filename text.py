#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2023 Yeh, Hsin-Hsien <yhh76227@gmail.com>
#

"""
Library for Text Processing
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


##############################################################################
### Class Definition


class Align(IntEnum):
    TL, TC, TR = 0, 1, 2
    CL, CC, CR = 3, 4, 5
    BL, BC, BR = 6, 7, 8


class SimpleTable:
    """A Simple Text Table Generator."""

    def __init__(self, heads: dict, sep: str):
        """
        Arguments
        ---------
        heads  format={key1: title1, key2: title2, ...}.
        sep    the separator use to split the string.
        """
        self._head_dict = {}
        self._table = [[]]
        self._sep = sep

        for key, title in heads.items():
            col_size = max([len(x) for x in title.split(self._sep)])
            self._table[0].append(self.Head(key, title, col_size))
            self._head_dict[key] = self._table[0][-1]

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
    def max_row(self) -> int:
        return len(self._table)

    @property
    def max_col(self) -> int:
        return len(self._head_dict)

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
        if new_key in self._head_dict:
            raise IndexError("The new key is existed.")
        head = self._head_dict[cur_key]
        head.key = new_key
        self._head_dict[new_key] = head
        del self._head_dict[cur_key]

    def add_row(self, data: list, align: int=Align.TL):
        """
        Add a new row.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        data_size = len(data)
        self._table.append(row:=[])
        for i in range(self.max_col):
            if i < data_size:
                row.append(self.Cell(data[i], align))
                size = len(str(data[i]))
                if size > self._table[0][i].col_size:
                    self._table[0][i].col_size = size
            else:
                row.append(self.Cell(align=align))

    def add_col(self, key, title: str, data: list, align: int=Align.TL):
        """
        Add a new column.
        
        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        data_size = len(data)
        col_size = max([len(x) for x in title.split(self._sep)])
        self._table[0].append(self.Head(key, title, col_size))
        self._head_dict[key] = self._table[0][-1]
        for i in range(1, self.max_row):
            if i < data_size:
                self._table[i].append(self.Cell(data[i-1], align))
                size = len(str(data[i-1]))
                if size > self._table[0][-1].col_size:
                    self._table[0][-1].col_size = size
            else:
                self._table[i].append(self.Cell(align=align))

    def swap_row(self, index1: int, index2: int):
        """Swap two specific rows."""
        if index1 == 0 or index2 == 0:
            raise IndexError("The header row cannot be swapped.")
        self._table[index1], self._table[index2] = (
            self._table[index2], self._table[index1]
        )

    def swap_col(self, index1: int, index2: int):
        """Swap two specific columns."""
        for i in range(self.max_row):
            self._table[i][index1], self._table[i][index2] = (
                self._table[i][index2], self._table[i][index1]
            )

    def del_row(self, index: int):
        """Delete the specific row"""
        if index != 0 and self.max_row > 1:
            del self._table[index]

    def del_col(self, index: int):
        """Delete the specific column."""
        del self._head_dict[self._table[0][index].key]
        for i in range(self.max_row):
            del self._table[i][index]
        if self.max_col == 0:
            self._table = [[self.Head('title1', 'Title1', 6)]]
            self._head_dict['title1'] = self._table[0][-1]

    def set_row_align(self, index: int, align: Align):
        """
        Set the align type of a row.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        for i in range(self.max_col):
            self._table[index][i].align = align

    def set_col_align(self, index: int, align: Align):
        """
        Set the align type of a column.

        The header row support horizontal/vertical align type change.
        The content rows only support horizontal align type change.
        """
        for i in range(1, self.max_row):
            self._table[i][index].align = align

    def get_header(self) -> list:
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
        """Get values of the specific row."""
        if index > 0:
            return [cell.value for cell in self._table[index]]
        else:
            return [head.title for head in self._table[index]]

    def get_col(self, index: int) -> list:
        """Get values of the specific column."""
        col = []
        for i in range(1, self.max_row):
            col.append(self._table[i][index].value)
        return col

    def print_table(self):
        """Print the table."""
        # divider
        print("+", end='')
        for c in range(self.max_col):
            print("-{}-+".format('-' * self._table[0][c].col_size), end='')
        print()

        # header
        data, row_cnt, max_row = [], [], 0
        for c in range(self.max_col):
            data.append(self._table[0][c].title.split(self._sep))
            row_cnt.append(len(data[-1]))
            if row_cnt[-1] > max_row:
                max_row = row_cnt[-1]
        start_row = [int((max_row-x)/2) for x in row_cnt]
        row_cnt = [start_row[x]+row_cnt[x] for x in range(len(row_cnt))]

        for r in range(max_row):
            print("|", end='')
            for c in range(self.max_col):
                if start_row[c] <= r < row_cnt[c]:
                    str_ = data[c][r-start_row[c]]
                    match self._table[0][c].align:
                        case Align.TL | Align.CL | Align.BL:
                            str_ = str_.ljust(self._table[0][c].col_size)
                        case Align.TC | Align.CC | Align.BC:
                            str_ = str_.center(self._table[0][c].col_size)
                        case Align.TR | Align.CR | Align.BR:
                            str_ = str_.rjust(self._table[0][c].col_size)
                        case _:
                            tag = self._table[0][c].align
                            raise SyntaxError(f"The align ID is undefined ({tag}).")
                else:
                    str_ = ' ' * self._table[0][c].col_size
                print(f" {str_} |", end='')
            print()

        # divider
        print("+", end='')
        for c in range(self.max_col):
            print("-{}-+".format('-' * self._table[0][c].col_size), end='')
        print()

        # content
        for r in range(1, self.max_row):
            print("|", end='')
            for c in range(self.max_col):
                str_ = str(self._table[r][c].value)
                match self._table[r][c].align:
                    case Align.TL | Align.CL | Align.BL:
                        str_ = str_.ljust(self._table[0][c].col_size)
                    case Align.TC | Align.CC | Align.BC:
                        str_ = str_.center(self._table[0][c].col_size)
                    case Align.TR | Align.CR | Align.BR:
                        str_ = str_.rjust(self._table[0][c].col_size)
                    case _:
                        tag = self._table[0][c].align
                        raise SyntaxError(f"The align ID is undefined ({tag}).")
                print(f" {str_} |", end='')
            print()

        # divider
        print("+", end='')
        for c in range(self.max_col):
            print("-{}-+".format('-' * self._table[0][c].col_size), end='')
        print()

