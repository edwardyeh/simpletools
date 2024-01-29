#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2023 Yeh, Hsin-Hsien <yhh76227@gmail.com>
#

"""
Library for Text Processing
"""

import copy
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


@dataclass(slots=True)
class Cell:
    """
    Attributes
    ----------
    value   data value.
    align   data align for table print.       (default=Align.TL)
    is_sep  string separate by the separator. (default=False)
    fs      format string for table print.    (default="{}")
    """
    value:  Any
    align:  Align = Align.TL
    is_sep: bool  = False
    fs:     str   = "{}"


@dataclass(slots=True)
class HeadCell:
    """
    Attributes
    ----------
    key     column hash key.
    title   column title.
    width   column width.                     (default=0)
    align   title align for table print.      (default=Align.TL)
    is_sep  string separate by the separator. (default=True)

    If width is 0, use the maximum length of data or title as the column 
    size when print the table.
    """
    key:    Any
    title:  str
    width:  int   = 0
    align:  Align = Align.TL
    is_sep: bool  = True


class Array:
    """Array wrapper."""
    def __init__(self, init_array: list=None, is_pure: bool=False):
        if init_array is None:
            self._array = []
        elif not is_pure:
            self._array = init_array
        else:
            self._array = [Cell(value) for value in init_array]
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._array})"

    def __add__(self, that):
        if (ax1:=self.shape) == (ax2:=that.shape):
            new_array = self.__class__(copy.deepcopy(self._array))
            if len(ax1) == 1:
                for c, cell in enumerate(new_array._array):
                    cell.value += that._array[c].value
            else:
                for r, row in enumerate(new_array._array):
                    for c, cell in enumerate(row):
                        cell.value += that._array[r][c].value
            return new_array 
        else:
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)

    def __sub__(self, that):
        if (ax1:=self.shape) == (ax2:=that.shape):
            new_array = self.__class__(copy.deepcopy(self._array))
            if len(ax1) == 1:
                for c, cell in enumerate(new_array._array):
                    cell.value -= that._array[c].value
            else:
                for r, row in enumerate(new_array._array):
                    for c, cell in enumerate(row):
                        cell.value -= that._array[r][c].value
            return new_array 
        else:
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)

    def __mul__(self, that):
        if (ax1:=self.shape) == (ax2:=that.shape):
            new_array = self.__class__(copy.deepcopy(self._array))
            if len(ax1) == 1:
                for c, cell in enumerate(new_array._array):
                    cell.value *= that._array[c].value
            else:
                for r, row in enumerate(new_array._array):
                    for c, cell in enumerate(row):
                        cell.value *= that._array[r][c].value
            return new_array 
        else:
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)

    def __truediv__(self, that):
        if (ax1:=self.shape) == (ax2:=that.shape):
            new_array = self.__class__(copy.deepcopy(self._array))
            if len(ax1) == 1:
                for c, cell in enumerate(new_array._array):
                    cell.value /= that._array[c].value
            else:
                for r, row in enumerate(new_array._array):
                    for c, cell in enumerate(row):
                        cell.value /= that._array[r][c].value
            return new_array 
        else:
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)

    def _get_array(self, index):
        """ Return an entry or a sub-table."""
        if type(index) is tuple:
            rid, cid = index
            if type(rid) is int:
                return self._array[rid][cid]
            else:
                return [rarray[cid] for rarray in self._array[rid]]
        else:
            return self._array[index]

    def __getitem__(self, index):
        """ Return an entry or a sub-table."""
        array = self._get_array(index)
        return self.__class__(array) if type(array) is list else array

    def __setitem__(self, index, that):
        """Set entry values."""
        array = self._get_array(index)
        if (ax1:=self._shape(array)) == (ax2:=that.shape):
            if len(ax1) == 1:
                for c, cell in enumerate(array):
                    cell.value = that._array[c].value
            else:
                for r, row in enumerate(array):
                    for c, cell in enumerate(row):
                        cell.value = that._array[r][c].value
        else:
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)

    def _shape(self, array: list) -> list:
        """Return the shape of the array. (format=([row,] col))"""
        if type(array[0]) is list:
            return (len(array), len(array[0]))
        else:
            return (len(array), )

    @property
    def shape(self) -> list:
        """Return the shape of the array. (format=(row, col))"""
        return self._shape(self._array)

    @property
    def value(self) -> list:
        """Return the value list."""
        vlist = []
        for a1 in self._array:
            vlist.append([a2.value for a2 in a1] if type(a1) is list 
                         else a1.value)
        return vlist

    @value.setter
    def value(self, vlist: list):
        """Set cell values."""
        if (ax1:=self.shape) == (ax2:=self._shape(vlist)):
            if len(ax1) == 1:
                for c, cell in enumerate(self._array):
                    cell.value = vlist[c]
            else:
                for r, row in enumerate(self._array):
                    for c, cell in enumerate(row):
                        cell.value = vlist[r][c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def align(self) -> list:
        """Return the align list."""
        vlist = []
        for a1 in self._array:
            vlist.append([a2.align for a2 in a1] if type(a1) is list 
                         else a1.align)
        return vlist

    @align.setter
    def align(self, vlist: list):
        """Set cell aligns."""
        if (ax1:=self.shape) == (ax2:=self._shape(vlist)):
            if len(ax1) == 1:
                for c, cell in enumerate(self._array):
                    cell.align = vlist[c]
            else:
                for r, row in enumerate(self._array):
                    for c, cell in enumerate(row):
                        cell.align = vlist[r][c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def is_sep(self) -> list:
        """Return the is_sep list."""
        vlist = []
        for a1 in self._array:
            vlist.append([a2.is_sep for a2 in a1] if type(a1) is list 
                         else a1.is_sep)
        return vlist

    @is_sep.setter
    def is_sep(self, vlist: list):
        """Set cell is_seps."""
        if (ax1:=self.shape) == (ax2:=self._shape(vlist)):
            if len(ax1) == 1:
                for c, cell in enumerate(self._array):
                    cell.is_sep = vlist[c]
            else:
                for r, row in enumerate(self._array):
                    for c, cell in enumerate(row):
                        cell.is_sep = vlist[r][c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def fs(self) -> list:
        """Return the fs list."""
        vlist = []
        for a1 in self._array:
            vlist.append([a2.fs for a2 in a1] if type(a1) is list 
                         else a1.fs)
        return vlist

    @fs.setter
    def fs(self, vlist: list):
        """Set cell fss."""
        if (ax1:=self.shape) == (ax2:=self._shape(vlist)):
            if len(ax1) == 1:
                for c, cell in enumerate(self._array):
                    cell.fs = vlist[c]
            else:
                for r, row in enumerate(self._array):
                    for c, cell in enumerate(row):
                        cell.fs = vlist[r][c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)


class Index:
    """Index wrapper."""
    def __init__(self, init_array: list=None):
        self._array = [] if init_array is None else init_array

    def __repr__(self):
        return f"{self.__class__.__name__}({self._array})"

    def __getitem__(self, index):
        """ Return an entry or a sub-table."""
        array = self._array[index]
        return self.__class__(array) if type(array) is list else array

    @property
    def length(self) -> int:
        """Return the length of the index."""
        return len(self._array)

    @property
    def id(self) -> dict:
        """Return key/ID pair by the dictionary."""
        vdict = {}
        for i, cell in enumerate(self._array):
            key = cell.key
            if type(key) is not str:
                msg = f"Hash key must be the string type (id[{i}]={key})."
                raise KeyError(msg)
            elif key in vdict:
                msg = f"Hash key repeat (id[{vdict[key]}]==id[{i}])."
                raise KeyError(msg)
            else:
                vdict[key] = i
        return vdict 

    @property
    def key(self) -> list:
        """Get hash keys of the index."""
        return [x.key for x in self._array]

    @key.setter
    def key(self, vlist: list):
        """Set index keys"""
        if (sz1:=len(self._array)) == (sz2:=len(vlist)):
            for c, cell in enumerate(self._array):
                cell.key = vlist[c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def title(self) -> list:
        """Get titles of the index."""
        return [x.title for x in self._array]

    @title.setter
    def title(self, vlist: list):
        """Set index titles"""
        if (sz1:=len(self._array)) == (sz2:=len(vlist)):
            for c, cell in enumerate(self._array):
                cell.title = vlist[c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def width(self) -> list:
        """Get titles of the index."""
        return [x.width for x in self._array]

    @width.setter
    def width(self, vlist: list):
        """Set index titles"""
        if (sz1:=len(self._array)) == (sz2:=len(vlist)):
            for c, cell in enumerate(self._array):
                cell.width = vlist[c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def align(self) -> list:
        """Get titles of the index."""
        return [x.align for x in self._array]

    @align.setter
    def align(self, vlist: list):
        """Set index titles"""
        if (sz1:=len(self._array)) == (sz2:=len(vlist)):
            for c, cell in enumerate(self._array):
                cell.align = vlist[c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)

    @property
    def is_sep(self) -> list:
        """Get titles of the index."""
        return [x.is_sep for x in self._array]

    @is_sep.setter
    def is_sep(self, vlist: list):
        """Set index titles"""
        if (sz1:=len(self._array)) == (sz2:=len(vlist)):
            for c, cell in enumerate(self._array):
                cell.is_sep = vlist[c]
        else:
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)


class SimpleTable:
    """A Simple Text Table Generator."""
    def __init__(self, heads: list, sep: str='.', rdiv_cnt: Any=math.inf, 
                 is_partp: bool=True):
        """
        Arguments
        ---------
        heads     format=[(key1, title1), (key2, title2), ...].
                    # The key & title must be the string type.
        sep       the separator use to split the string.
        rdiv_cnt  the number of rows between two data row dividers.
                    # Use default if set 0.
        is_partp  show partial content if the data length is greater than the 
                  column width.
                    # If any data row is separated, force is_partp=True.
        """
        self._index_head = HeadCell(None, '')
        self._index = []
        self._header = []
        self._table = []
        self._sep = sep
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt
        self.is_partp = is_partp

        for i, (key, title) in enumerate(heads):
            self._header.append(HeadCell(key, title))

    @property
    def sep(self) -> str:
        """Return the string separator."""
        return self._sep

    @property
    def rdiv_cnt(self) -> int:
        """Return the row count between two data dividers."""
        return self._rdiv_cnt

    @rdiv_cnt.setter
    def rdiv_cnt(self, rdiv_cnt: int):
        """Set the row count between two data dividers."""
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

    @property
    def header(self) -> list:
        """Return the head list."""
        return Index(self._header.copy())

    @property
    def index(self) -> list:
        """Return the index list."""
        return Index(self._index.copy())

    @property
    def index_head(self) -> HeadCell:
        """Return the index head cell."""
        return self._index_head

    @property
    def max_row(self) -> int:
        """Return the row number of the table."""
        return len(self._table)

    @property
    def max_col(self) -> int:
        """Return the column number of the table."""
        return len(self._header)

    def __getitem__(self, index):
        """ Return an entry or a sub-table."""
        return Array(self._table).__getitem__(index)

    def __setitem__(self, index, that):
        """Set entry values."""
        Array(self._table).__setitem__(index, that)

    def add_row(self, key, title: str, data: list, align: int=Align.NONE, 
                init: Any=''):
        """
        Add a new row.

        Arguments
        ---------
        key    row hash key (must be the string type or None).
        title  row title.
        data   value list.
        align  data align for table print.
        init   initial value (set initial value if len(row) > len(data)).
        """
        data_size = len(data)
        self._index.append(HeadCell(key, title))
        self._table.append(row:=[])
        for i in range(self.max_col):
            if self.max_row == 1:
                align_ = Align.TL
            elif align == Align.NONE:
                align_ = self._table[-2][i].align
            else:
                align_ = align
            value = data[i] if i < data_size else init
            row.append(Cell(value, align=align_))

    def add_col(self, key, title: str, data: list, align: int=Align.TL, 
                init: Any=''):
        """
        Add a new column.

        Arguments
        ---------
        key    column hash key (must be the string type or None).
        title  column title.
        data   value list.
        align  data align for table print.
        init   initial value (set initial value if len(row) > len(data)).
        """
        data_size = len(data)
        self._header.append(HeadCell(key, title))
        for i in range(self.max_row):
            value = data[i] if i < data_size else init
            self._table[i].append(Cell(value, align=align))

    def swap_row(self, index1, index2):
        """
        Swap two specific rows.

        Arguments
        ---------
        index1  row1 hash key or ID.
        index2  row2 hash key or ID.
        """
        rid1 = self.index.id[index1] if type(index1) is str else index1
        rid2 = self.index.id[index2] if type(index2) is str else index2
        self._index[rid1], self._index[rid2] = (
            self._index[rid2], self._index[rid1])
        self._table[rid1], self._table[rid2] = (
            self._table[rid2], self._table[rid1])

    def swap_col(self, index1, index2):
        """
        Swap two specific columns.

        Arguments
        ---------
        index1  column1 hash key or ID.
        index2  column2 hash key or ID.
        """
        cid1 = self.header.id[index1] if type(index1) is str else index1
        cid2 = self.header.id[index2] if type(index2) is str else index2
        self._header[cid1], self._header[cid2] = (
            self._header[cid2], self._header[cid1])
        for i in range(self.max_row):
            self._table[i][cid1], self._table[i][cid2] = (
                self._table[i][cid2], self._table[i][cid1])

    def del_row(self, index):
        """
        Delete the specific row.

        Arguments
        ---------
        index  row hash key or ID.
        """
        if self.max_row > 0:
            rid = self.index.id[index] if type(index) is str else index
            del self._index[rid]
            del self._table[rid]

    def del_col(self, index):
        """
        Delete the specific column.

        Arguments
        ---------
        index  column hash key or ID.
        """
        cid = self.header.id[index] if type(index) is str else index
        del self._header[cid]
        for i in range(self.max_row):
            del self._table[i][cid]
        if self.max_col == 0:
            self._header.append(HeadCell('title1', 'Title1'))

    def set_head_attr(self, width: int=None, align: Align=None,
                      is_sep: bool=None):
        """
        Change head attribute over all head cells.

        Arguments
        ---------
        width   column width.
        align   title align for table print.
        is_sep  string separate by the separator.
        """
        for cell in self._header:
            if width is not None:
                cell.width = width
            if align is not None:
                cell.align = align
            if is_sep is not None:
                cell.is_sep = is_sep

    def set_index_attr(self, width: int=None, align: Align=None,
                       is_sep: bool=None):
        """
        Change index attribute over all index cells.

        Arguments
        ---------
        width   column width.
        align   title align for table print.
        is_sep  string separate by the separator.
        """
        if width is not None:
            self._index_head.width = width
        for cell in self._index:
            if align is not None:
                cell.align = align
            if is_sep is not None:
                cell.is_sep = is_sep

    def set_row_attr(self, index: int, align: Align=None, is_sep: bool=None,
                     fs: str=None):
        """
        Set cell attribute for one data row.

        Arguments
        ---------
        index   row ID.
        align   data align for table print.
        is_sep  string separate by the separator.
        fs      format string for table print.
        """
        for i in range(self.max_col):
            if align is not None:
                self._table[index][i].align = align
            if is_sep is not None:
                self._table[index][i].is_sep = is_sep
            if fs is not None:
                self._table[index][i].fs = fs

    def set_col_attr(self, index, width: int=None, align: Align=None,
                     is_sep: bool=None, fs: str=None):
        """
        Set cell attribute for one data column.

        Arguments
        ---------
        index   column hash key or ID.
        width   column width.
        align   data align for table print.
        is_sep  string separate by the separator.
        fs      format string for table print.

        If width is 0, use the maximum length of data or title as the column
        size when print the table. If the specific size is small than the
        length of title, use the title length as the column width.
        """
        cid = self.header.id[index] if type(index) is str else index
        if width is not None:
            self._header[cid].width = width
        for i in range(self.max_row):
            if align is not None:
                self._table[i][cid].align = align
            if is_sep is not None:
                self._table[i][cid].is_sep = is_sep
            if fs is not None:
                self._table[i][cid].fs = fs

    def print(self, fp=None, sid: int=1, column: list=None, row: list=None):
        """
        Print the table.

        Arguments
        ---------
        fp      set the file path to export the table.
        sid     table style select.
        column  specify columns by column ID, set None to display all.
        row     specify rows by row ID, set None to display all.
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

        if row is not None:
            row_list = row.copy()
        else:
            row_list = list(range(self.max_row))

        csize_list = []
        hdata_list, hrow_cnt = [], []
        vdata_list, vrow_cnt = [], []

        ## get head data
        for c in col_list:
            if self._header[c].is_sep:
                hdata_list.append(self._header[c].title.split(self._sep))
            else:
                hdata_list.append([self._header[c].title])
            hrow_cnt.append(len(hdata_list[-1]))
            size = max([len(x) for x in hdata_list[-1]])
            size2 = self._header[c].width
            csize_list.append(size if size > size2 else size2)

        ## get value data
        is_force_partp = False
        for r in row_list:
            vdata_list.append(row_data:=[])
            vrow_cnt.append(row_cnt:=[])
            for i, c in enumerate(col_list):
                str_val = self._table[r][c].fs.format(self._table[r][c].value)
                if self._table[r][c].is_sep:
                    row_data.append(str_val.split(self._sep))
                else:
                    row_data.append([str_val])
                if (rcnt:=len(row_data[-1])) > 1:
                    is_force_partp = True
                row_cnt.append(rcnt)
                if self._header[c].width == 0:
                    size = max([len(x) for x in row_data[-1]])
                    if size > csize_list[i]:
                        csize_list[i] = size

        ## divider print
        str_div = f"{div_edg}"
        for width in csize_list:
            str_div += "-{}-{}".format('-' * width, div_sep) 
        str_div = str_div[:-1] + div_edg
        print(str_div, file=fp)

        ## header print
        max_row, row_st, row_ed = max(hrow_cnt), [], []
        for i, c in enumerate(col_list):
            match (align:=self._header[c].align):
                case Align.TL | Align.TC | Align.TR:
                    row_st.append(0)
                    row_ed.append(hrow_cnt[i])
                case Align.CL | Align.CC | Align.CR:
                    row_st.append(int((max_row-hrow_cnt[i])/2))
                    row_ed.append(row_st[-1]+hrow_cnt[i])
                case Align.BL | Align.BC | Align.BR:
                    row_st.append(max_row-hrow_cnt[i])
                    row_ed.append(max_row)
                case _:
                    msg = f"The align ID is undefined (align={align})."
                    raise SyntaxError(msg)

        for r in range(max_row):
            str_ = f"{val_edg}"
            for i, c in enumerate(col_list):
                if row_st[i] <= r < row_ed[i]:
                    str_val = hdata_list[i][r-row_st[i]]
                    match (align:=self._header[c].align):
                        case Align.TL | Align.CL | Align.BL:
                            str_mdy = str_val.ljust(csize_list[i])
                        case Align.TC | Align.CC | Align.BC:
                            str_mdy = str_val.center(csize_list[i])
                        case Align.TR | Align.CR | Align.BR:
                            str_mdy = str_val.rjust(csize_list[i])
                        case _:
                            msg = f"The align ID is undefined (align={align})."
                            raise SyntaxError(msg)
                else:
                    str_mdy = ' ' * csize_list[i]
                str_ += f" {str_mdy} {val_sep}"
            str_ = str_[:-1] + val_edg
            print(str_, file=fp)

        ## divider print
        print(str_div, file=fp)

        ## content print
        row_cnt = 0
        for j, r in enumerate(row_list):
            ## content divider print
            if row_cnt == self._rdiv_cnt:
                print(str_div, file=fp)
                row_cnt = 1
            else:
                row_cnt = row_cnt + 1

            max_row, row_st, row_ed = max(vrow_cnt[j]), [], []
            for i, c in enumerate(col_list):
                match (align:=self._table[r][c].align):
                    case Align.TL | Align.TC | Align.TR:
                        row_st.append(0)
                        row_ed.append(vrow_cnt[j][i])
                    case Align.CL | Align.CC | Align.CR:
                        row_st.append(int((max_row-vrow_cnt[j][i])/2))
                        row_ed.append(row_st[-1]+vrow_cnt[j][i])
                    case Align.BL | Align.BC | Align.BR:
                        row_st.append(max_row-vrow_cnt[j][i])
                        row_ed.append(max_row)
                    case _:
                        msg = f"The align ID is undefined (align={align})."
                        raise SyntaxError(msg)

            for r2 in range(max_row):
                str_, acc_col_sz = f"{val_edg}", 0 
                for i, c in enumerate(col_list):
                    if row_st[i] <= r2 < row_ed[i]:
                        str_val = vdata_list[j][i][r2-row_st[i]]
                        acc_col_sz += csize_list[i] + 3
                        match (align:=self._table[r][c].align):
                            case Align.TL | Align.CL | Align.BL:
                                str_mdy = str_val.ljust(csize_list[i])
                            case Align.TC | Align.CC | Align.BC:
                                str_mdy = str_val.center(csize_list[i])
                            case Align.TR | Align.CR | Align.BR:
                                str_mdy = str_val.rjust(csize_list[i])
                            case _:
                                msg = f"The align ID is undefined (align={align})."
                                raise SyntaxError(msg)
                        if len(str_val) > csize_list[i]:
                            if self.is_partp or is_force_partp:
                                str_mdy = f" {str_mdy[:csize_list[i]-1]}> "
                            else:
                                str_mdy = f" {str_mdy}\n{' '*acc_col_sz}"
                        else:
                            str_mdy = f" {str_mdy} "
                    else:
                        str_mdy = " {} ".format(' ' * csize_list[i])
                    str_ += f"{str_mdy}{val_sep}"
                str_ = str_[:-1] + val_edg
                print(str_, file=fp)

        ## divider print
        print(str_div, file=fp)


