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
        self._header = []
        # self._index = {'head': self.HeadCell('', '', 0), 'value': []}
        self._table = []
        self._sep = sep
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

        for i, (key, title) in enumerate(heads.items()):
            col_size = max([len(x) for x in title.split(self._sep)])
            self._header.append(self.HeadCell(key, title, col_size))

    @dataclass(slots=True)
    class Cell:
        """
        Attributes
        ----------
        value   cell value.
        align   cell value align for table print.         (default=Align.TL)
        fs      cell value format string for table print. (default="{}")
        """
        value: Any
        align: Align = Align.TL
        fs:    str   = "{}"

    @dataclass(slots=True)
    class HeadCell:
        """
        Attributes
        ----------
        key             column hash key.
        title           column title.
        col_size        column width
        align           title align for table print.      (default=Align.TL)
        is_col_sz_fix   set true to fix the column width. (default=False)
        """
        key:           Any
        title:         str
        col_size:      int
        align:         Align = Align.TL
        is_col_sz_fix: bool  = False

    # @dataclass(slots=True)
    # class IndexCell:
    #     """
    #     Attributes
    #     ----------
    #     key     column hash key.
    #     title   column title.
    #     align   title align for table print. (default=Align.TL)
    #     """
    #     key:   Any
    #     title: str
    #     align: Align = Align.TL

    class Array:
        """Array wrapper."""
        def __init__(self, init_array: list=None):
            """
            Argument
            --------
            init_array  initial array.
            """
            self._array = [] if init_array is None else init_array
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self._array})"

        def __getitem__(self, index):
            """ Return a single entry or the sub-table."""
            if type(index) is tuple:
                rid, cid = index
                if type(rid) is int and type(cid) is int:
                    return self._array[rid][cid]
                else:
                    return Array([rarray[cid] for rarray in self._array[rid]])
            else:
                data = self._array[index]
                return Array(data) if type(data) is list else data

        def __setitem__(self, index, value):
            """Set entry value."""
            if type(index) is tuple:
                self._array[index[0]][index[1]].value = value
            else:
                self._array[index].value = value

        def extend(self, array):
            return Array(self._array + array._array)

    @property
    def sep(self) -> str:
        """Return head title separator."""
        return self._sep

    @property
    def rdiv_cnt(self) -> int:
        """Return row count between row divider."""
        return self._rdiv_cnt

    @rdiv_cnt.setter
    def rdiv_cnt(self, rdiv_cnt: int):
        """Set row count between row divider."""
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

    @property
    def head_cid(self) -> dict:
        """Return header column ID (type: dict)."""
        return {hcell.key: i for i, hcell in enumerate(self._header)}

    @property
    def header(self) -> list:
        """Return the head list (copy)."""
        return [cell for cell in self._header]

    @property
    def max_row(self) -> int:
        """Return the row number of the table."""
        return len(self._table)

    @property
    def max_col(self) -> int:
        """Return the column number of the table."""
        return len(self._header)

    def __getitem__(self, index):
        """ Return a single entry or the sub-table."""
        if type(index) is tuple:
            rid, cid = index
            if type(rid) is int and type(cid) is int:
                return self._table[rid][cid]
            else:
                return self.Array([rarray[cid] for rarray in self._table[rid]])
        else:
            return self.Array(self._table[index])

    def __setitem__(self, index, value):
        """Set entry value."""
        self._table[index[0]][index[1]].value = value

    def update_key(self, cur_key, new_key):
        """Update the key of the header dictionary."""
        if new_key in self.header:
            raise IndexError("The new key is existed.")
        self._header[self.head_cid[cur_key]].key = new_key

    def add_row(self, data: list, align: int=Align.NONE, init: Any=''):
        """
        Add a new row.

        Arguments
        ---------
        data    value list.
        align   cell align.
        init    initial value (set initial value if len(row) > len(data)).
        """
        data_size = len(data)
        self._table.append(row:=[])
        for i in range(self.max_col):
            if self.max_row == 1:
                align_ = Align.TL
            elif align == Align.NONE:
                align_ = self._table[-2][i].align
            else:
                align_ = align

            if i < data_size:
                row.append(self.Cell(data[i], align_))
                size = len(str(data[i]))
                if (not self._header[i].is_col_sz_fix 
                        and size > self._header[i].col_size):
                    self._header[i].col_size = size
            else:
                row.append(self.Cell(init, align=align_))

    def add_col(self, key, title: str, data: list, align: int=Align.TL, 
                init: Any=''):
        """
        Add a new column.

        Arguments
        ---------
        key     column hash key.
        title   column title.
        data    value list.
        align   cell align.
        init    initial value (set initial value if len(row) > len(data)).
        """
        data_size = len(data)
        col_size = max([len(x) for x in title.split(self._sep)])
        self._header.append(self.HeadCell(key, title, col_size))
        for i in range(self.max_row):
            if i < data_size:
                self._table[i].append(self.Cell(data[i], align))
                size = len(str(data[i]))
                if size > self._header[-1].col_size:
                    self._header[-1].col_size = size
            else:
                self._table[i].append(self.Cell(init, align=align))

    def swap_row(self, index1: int, index2: int):
        """
        Swap two specific rows.

        Argument index1, index2 should be row IDs.
        """
        self._table[index1], self._table[index2] = (
            self._table[index2], self._table[index1]
        )

    def swap_col(self, index1, index2):
        """
        Swap two specific columns.

        Argument index1, index2 can be column IDs or keys.
        """
        cid1 = self.head_cid[index1] if type(index1) is str else index1
        cid2 = self.head_cid[index2] if type(index2) is str else index2
        self._header[cid1], self._header[cid2] = (
            self._header[cid2], self._header[cid1])
        for i in range(self.max_row):
            self._table[i][cid1], self._table[i][cid2] = (
                self._table[i][cid2], self._table[i][cid1]
            )

    def del_row(self, index: int):
        """
        Delete the specific row.

        Argument index should be a row ID
        """
        if self.max_row > 0:
            del self._table[index]

    def del_col(self, index):
        """
        Delete the specific column.

        Argument index can be a column ID or key.
        """
        cid = self.head_cid[index] if type(index) is str else index
        del self._header[cid]
        for i in range(self.max_row):
            del self._table[i][cid]
        if self.max_col == 0:
            self._header.append(self.HeadCell('title1', 'Title1', 6))

    def set_head_attr(self, align: Align=None):
        """
        Change head attribute over all head cells.

        Arguments
        ---------
        align   title align for table print.
        """
        for hcell in self._header:
            if align is not None:
                hcell.align = align

    def set_row_attr(self, index: int, align: Align=None, fs: str=None):
        """
        Set cell attribute for one data row.

        Arguments
        ---------
        index   row ID
        align   cell value align for table print.
        fs      cell value format string for table print.
        """
        for i in range(self.max_col):
            if align is not None: 
                self._table[index][i].align = align
            if fs is not None: 
                self._table[index][i].fs = fs

    def set_col_attr(self, index, align: Align=None, fs: str=None):
        """
        Set cell attribute for one data column.

        Arguments
        ---------
        index   column ID or hash key
        align   cell value align for table print.
        fs      cell value format string for table print.
        """
        cid = self.head_cid[index] if type(index) is str else index
        for i in range(self.max_row):
            if align is not None:
                self._table[i][cid].align = align
            if fs is not None:
                self._table[i][cid].fs = fs 

    def set_col_size(self, index, size: int, is_fix: bool):
        """
        Set column size.

        Arguments
        ---------
        index   column ID or hash key
        size    column size (set 0 to use the maximum length of contents).
        is_fix  if is_fix is true, disable auto column size update.

        If size is small than the title size, use title size.
        """
        cid = self.head_cid[index] if type(index) is str else index
        (head:=self._header[cid]).is_col_sz_fix = is_fix
        title_sz = max([len(x) for x in head.title.split(self._sep)])
        
        if (col_size:=size) == 0:
            for i in range(self.max_row):
                if (sz:=len(self._table[i][cid].value)) > col_size:
                    col_size = sz

        head.col_size = col_size if col_size > title_sz else title_sz

    def get_keys(self) -> list:
        """Get the header key of the table."""
        return [x.key for x in self._header]

    def get_titles(self) -> list:
        """Get the header title of the table."""
        return [x.title for x in self._header]

    def get_values(self) -> list:
        """Get the values of the table content."""
        table = []
        for r in range(self.max_row):
            table.append(row:=[])
            for c in range(self.max_col):
                row.append(self._table[r][c].value)
        return table

    def get_row(self, index: int) -> list:
        """
        Get values of the specific row.

        Argument index should be row IDs.
        """
        return [cell.value for cell in self._table[index]]

    def get_col(self, index) -> list:
        """
        Get values of the specific column.

        Argument index can be row IDs or keys.
        """
        cid = self.head_cid[index] if type(index) is str else index
        col = []
        for i in range(self.max_row):
            col.append(self._table[i][cid].value)
        return col

    def print_table(self, fp=None, sid: int=1, 
                    column: list=None, index: list=None):
        """
        Print the table.

        Arguments
        ---------
        fp      file out of print function.               (default=None)
        sid     table style select.                       (default=1)
        column  specify columns by column ID, default all (default=None)
        index   specify indexs by row ID, default all     (default=None)
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

        if column is not None:
            col_list = column.copy()
        else:
            col_list = list(range(self.max_col))

        if index is not None:
            row_list = index.copy()
        else:
            row_list = list(range(self.max_row))

        # divider
        str_div = f"{div_edg}"
        for c in col_list:
            str_div += "-{}-{}".format('-' * self._header[c].col_size, div_sep) 
        str_div = str_div[:-1] + div_edg
        print(str_div, file=fp)

        # header
        data, row_cnt, max_row = [], [], 0
        for c in col_list:
            data.append(self._header[c].title.split(self._sep))
            row_cnt.append(len(data[-1]))
        max_row = max(row_cnt)

        row_st, row_ed = [], []
        for i, c in enumerate(col_list):
            match (align:=self._header[c].align):
                case Align.TL | Align.TC | Align.TR:
                    row_st.append(0)
                    row_ed.append(row_cnt[i])
                case Align.CL | Align.CC | Align.CR:
                    row_st.append(int((max_row-row_cnt[i])/2))
                    row_ed.append(row_st[i]+row_cnt[i])
                case Align.BL | Align.BC | Align.BR:
                    row_st.append(max_row-row_cnt[i])
                    row_ed.append(max_row)
                case _:
                    raise SyntaxError(f"The align ID is undefined (align={align}).")

        for r in range(max_row):
            str_ = f"{val_edg}"
            for i, c in enumerate(col_list):
                if row_st[i] <= r < row_ed[i]:
                    str_val = data[i][r-row_st[i]]
                    match (align:=self._header[c].align):
                        case Align.TL | Align.CL | Align.BL:
                            str_mdy = str_val.ljust(self._header[c].col_size)
                        case Align.TC | Align.CC | Align.BC:
                            str_mdy = str_val.center(self._header[c].col_size)
                        case Align.TR | Align.CR | Align.BR:
                            str_mdy = str_val.rjust(self._header[c].col_size)
                        case _:
                            raise SyntaxError(f"The align ID is undefined (align={align}).")
                else:
                    str_mdy = ' ' * self._header[c].col_size
                str_ += f" {str_mdy} {val_sep}"
            str_ = str_[:-1] + val_edg
            print(str_, file=fp)

        # divider
        print(str_div, file=fp)

        # content
        row_cnt = 0
        for r in row_list:
            if row_cnt == self._rdiv_cnt:
                row_cnt = 1
                # content divider
                print(str_div, file=fp)
            else:
                row_cnt = row_cnt + 1

            str_, acc_col_sz = f"{val_edg}", 0 
            for c in col_list:
                str_val = self._table[r][c].fs.format(self._table[r][c].value)
                acc_col_sz += (col_sz:=self._header[c].col_size) + 3
                match (align:=self._table[r][c].align):
                    case Align.TL | Align.CL | Align.BL:
                        str_mdy = str_val.ljust(col_sz)
                    case Align.TC | Align.CC | Align.BC:
                        str_mdy = str_val.center(col_sz)
                    case Align.TR | Align.CR | Align.BR:
                        str_mdy = str_val.rjust(col_sz)
                    case _:
                        raise SyntaxError(f"The align ID is undefined (align={align}).")
                str_ += f" {str_mdy} "
                if len(str_val) > col_sz:
                    str_ += "\n{}".format(' ' * acc_col_sz)
                str_ += val_sep
            str_ = str_[:-1] + val_edg
            print(str_, file=fp)

        # divider
        print(str_div, file=fp)


