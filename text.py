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
        self._index_head = self.HeadCell(None, '')
        self._index = []
        self._header = []
        self._table = []
        self._sep = sep
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt
        self.is_partp = is_partp

        for i, (key, title) in enumerate(heads):
            self._header.append(self.HeadCell(key, title))

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
        key       column hash key.
        title     column title.
        col_size  column width.                     (default=0)
        align     title align for table print.      (default=Align.TL)
        is_sep    string separate by the separator. (default=True)

        If col_size is 0, use the maximum length of data or title as the column 
        size when print the table.
        """
        key:      Any
        title:    str
        col_size: int   = 0
        align:    Align = Align.TL
        is_sep:   bool  = True

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
            """ Return a single entry or sub-table."""
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
            """Set the entry value."""
            if type(index) is tuple:
                self._array[index[0]][index[1]].value = value
            else:
                self._array[index].value = value

        def extend(self, array):
            """Return the extend array."""
            return Array(self._array + array._array)

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
    def head_cid(self) -> dict:
        """Return header column IDs."""
        head_dict = {}
        for i, cell in enumerate(self._header):
            key = cell.key
            if key is None:
                raise KeyError(f"None type can be a direction key (cid={i}).")
            elif key in head_dict:
                msg = f"Hash key repeat (cid1={head_dict[key]}, cid2={i})."
                raise KeyError(msg)
            else:
                head_dict[key] = i
        return head_dict

    @property
    def header(self) -> list:
        """Return the head list."""
        return self._header.copy()

    @property
    def index_head(self) -> HeadCell:
        """Return the index head cell."""
        return self._index_head

    @property
    def index_rid(self) -> dict:
        """Return index row IDs."""
        index_dict = {}
        for i, cell in enumerate(self._index):
            key = cell.key
            if key is None:
                raise KeyError(f"None type can be a direction key (rid={i}).")
            elif key in index_dict:
                msg = f"Hash key repeat (rid1={index_dict[key]}, rid2={i})."
                raise KeyError(msg)
            else:
                index_dict[key] = i
        return index_dict

    @property
    def index(self) -> list:
        """Return the index list."""
        return self._index.copy()

    @property
    def max_row(self) -> int:
        """Return the row number of the table."""
        return len(self._table)

    @property
    def max_col(self) -> int:
        """Return the column number of the table."""
        return len(self._header)

    def __getitem__(self, index):
        """Return a entry or sub-table."""
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

    def update_head_key(self, cur_key, new_key):
        """Update the hash key of the header."""
        if new_key in self.head_cid:
            raise IndexError("The new key is existed.")
        self._header[self.head_cid[cur_key]].key = new_key

    def update_index_key(self, cur_key, new_key):
        """Update the hash key of the index."""
        if new_key in self.index_rid:
            raise IndexError("The new key is existed.")
        self._index[self.index_rid[cur_key]].key = new_key

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
        self._index.append(self.HeadCell(key, title))
        self._table.append(row:=[])
        for i in range(self.max_col):
            if self.max_row == 1:
                align_ = Align.TL
            elif align == Align.NONE:
                align_ = self._table[-2][i].align
            else:
                align_ = align
            value = data[i] if i < data_size else init
            row.append(self.Cell(value, align=align_))

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
        self._header.append(self.HeadCell(key, title))
        for i in range(self.max_row):
            value = data[i] if i < data_size else init
            self._table[i].append(self.Cell(value, align=align))

    def swap_row(self, index1, index2):
        """
        Swap two specific rows.

        Arguments
        ---------
        index1  row1 hash key or ID.
        index2  row2 hash key or ID.
        """
        rid1 = self.index_rid[index1] if type(index1) is str else index1
        rid2 = self.index_rid[index2] if type(index2) is str else index2
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
        cid1 = self.head_cid[index1] if type(index1) is str else index1
        cid2 = self.head_cid[index2] if type(index2) is str else index2
        self._header[cid1], self._header[cid2] = (
            self._header[cid2], self._header[cid1])
        for i in range(self.max_row):
            self._table[i][cid1], self._table[i][cid2] = (
                self._table[i][cid2], self._table[i][cid1])

    def del_row(self, index: int):
        """
        Delete the specific row.

        Arguments
        ---------
        index  row hash key or ID.
        """
        if self.max_row > 0:
            rid = self.index_rid[index] if type(index) is str else index
            del self._index[rid]
            del self._table[rid]

    def del_col(self, index):
        """
        Delete the specific column.

        Arguments
        ---------
        index  column hash key or ID.
        """
        cid = self.head_cid[index] if type(index) is str else index
        del self._header[cid]
        for i in range(self.max_row):
            del self._table[i][cid]
        if self.max_col == 0:
            self._header.append(self.HeadCell('title1', 'Title1'))

    def set_head_attr(self, col_size: int=None, align: Align=None, 
                      is_sep: bool=None):
        """
        Change head attribute over all head cells.

        Arguments
        ---------
        col_size  column width.
        align     title align for table print.
        is_sep    string separate by the separator.
        """
        for cell in self._header:
            if col_size is not None:
                cell.col_size = col_size
            if align is not None:
                cell.align = align
            if is_sep is not None:
                cell.is_sep = is_sep

    def set_index_attr(self, col_size: int=None, align: Align=None, 
                       is_sep: bool=None):
        """
        Change index attribute over all index cells.

        Arguments
        ---------
        col_size  column width.
        align     title align for table print.
        is_sep    string separate by the separator.
        """
        if col_size is not None:
            self._index_head.col_size = col_size
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

    def set_col_attr(self, index, col_size: int=None, align: Align=None, 
                     is_sep: bool=None, fs: str=None):
        """
        Set cell attribute for one data column.

        Arguments
        ---------
        index     column hash key or ID.
        col_size  column width.
        align     data align for table print.
        is_sep    string separate by the separator.
        fs        format string for table print.

        If col_size is 0, use the maximum length of data or title as the column 
        size when print the table. If the specific size is small than the 
        length of title, use the title length as the column width.
        """
        cid = self.head_cid[index] if type(index) is str else index
        if col_size is not None:
            self._header[cid].col_size = col_size
        for i in range(self.max_row):
            if align is not None:
                self._table[i][cid].align = align
            if is_sep is not None:
                self._table[i][cid].is_sep = is_sep
            if fs is not None:
                self._table[i][cid].fs = fs 

    def get_head_keys(self) -> list:
        """Get hash keys of the table header."""
        return [x.key for x in self._header]

    def get_head_titles(self) -> list:
        """Get titles of the table header."""
        return [x.title for x in self._header]

    def get_index_keys(self) -> list:
        """Get hash keys of the table index."""
        return [x.key for x in self._index]

    def get_index_titles(self) -> list:
        """Get titles of the table index."""
        return [x.title for x in self._index]

    def get_values(self) -> list:
        """Get data values of the table."""
        table = []
        for r in range(self.max_row):
            table.append(row:=[])
            for c in range(self.max_col):
                row.append(self._table[r][c].value)
        return table

    def get_row(self, index: int) -> list:
        """
        Get the value list of the specific row.

        Argument
        --------
        index  row hash key or ID.
        """
        rid = self.index_rid[index] if type(index) is str else index
        return [cell.value for cell in self._table[rid]]

    def get_col(self, index) -> list:
        """
        Get the value list of the specific column.

        Argument
        --------
        index  column hash key or ID.
        """
        cid = self.head_cid[index] if type(index) is str else index
        col = []
        for i in range(self.max_row):
            col.append(self._table[i][cid].value)
        return col

    def print_table(self, fp=None, sid: int=1, column: list=None, 
                    row: list=None):
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
            size2 = self._header[c].col_size
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
                if self._header[c].col_size == 0:
                    size = max([len(x) for x in row_data[-1]])
                    if size > csize_list[i]:
                        csize_list[i] = size

        ## divider print
        str_div = f"{div_edg}"
        for col_size in csize_list:
            str_div += "-{}-{}".format('-' * col_size, div_sep) 
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


