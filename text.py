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
class Border:
    top:    bool = True
    bottom: bool = True
    left:   bool = True
    right:  bool = True


@dataclass
class HeadAttr:
    """
    Parameters
    ----------
    key : Any
        Column hash key.
    title : str
        Column title.
    width : int, optional
        Column width. Default is 0 means use the maximum length of the header 
        title or table values as the column width when table printing.
    align : Align, optional
        Title align for table printing. Default is Align.TL.
    is_sep : bool, optional
        String separate by the separator. Default is True.
    border : Border, optional
        Border display setting. Default is true for all edges. 
    lofs : int, optional
        Number of blanks on the left side of the value string. Default is 1.
    rofs : int, optional
        Number of blanks on the right side of the value string. Default is 1.
    """
    key:    Any
    title:  str
    width:  int    = 0
    align:  Align  = Align.TL
    is_sep: bool   = True
    border: Border = field(default_factory=Border)
    lofs:   int    = 1
    rofs:   int    = 1


class Index:
    """Header wrapper."""
    def __init__(self, array: list[HeadAttr]):
        """
        Parameters
        ----------
        array : list[HeadAttr]
            Initial array.
        """
        self._array = array

    def __repr__(self):
        return f"{self.__class__.__name__}({self._array})"

    def _set_attr(self, attr: str, vlist: list[None|str]):
        if len(self._array) != len(vlist):
            msg = f"Shapes difference. (self:{ax1}, vlist:{ax2})"
            raise ValueError(msg)
        for c, cell in enumerate(self._array):
            cell.__dict__[attr] = vlist[c]

    @property
    def shape(self) -> tuple[int]:
        """shape of the array."""
        return len(self._array)

    @property
    def key(self) -> list[None|str]:
        """hash keys of the header."""
        return [x.key for x in self._array]

    @key.setter
    def key(self, vlist: list[None|str]):
        """hash keys of the header."""
        self._set_attr('key', vlist)

    @property
    def title(self) -> list[str]:
        """titles of the header."""
        return [x.title for x in self._array]

    @title.setter
    def title(self, vlist: list[str]):
        """titles of the header."""
        self._set_attr('title', vlist)

    @property
    def width(self) -> list[int]:
        """column width."""
        return [x.width for x in self._array]

    @width.setter
    def width(self, vlist: list[int]):
        """column width."""
        self._set_attr('width', vlist)

    @property
    def align(self) -> list[Align]:
        """title align for table printing."""
        return [x.align for x in self._array]

    @align.setter
    def align(self, vlist: list[Align]):
        """title align for table printing."""
        self._set_attr('align', vlist)

    @property
    def is_sep(self) -> list[bool]:
        """title separation enable for table printing."""
        return [x.is_sep for x in self._array]

    @is_sep.setter
    def is_sep(self, vlist: list[bool]):
        """title separation enable for table printing."""
        self._set_attr('is_sep', vlist)

    @property
    def border(self) -> list[Border]:
        """border type for table printing."""
        return [x.border for x in self._array]

    @border.setter
    def border(self, vlist: list[Border]):
        """border type for table printing."""
        self._set_attr('border', vlist)


@dataclass
class TableAttr:
    """
    Parameters
    ----------
    align : Align, optional
        Data align for table printing. Default is Align.TL.
    is_sep : bool, optional
        String separate by the separator. Default is False.
    fs : str, optional
        Format string for table printing. Default is "{}".
    border: Border, optional
        Border display setting. Default is true for all edges. 
    """
    align:  Align  = Align.TL
    is_sep: bool   = False
    fs:     str    = "{}"
    border: Border = field(default_factory=Border)


class AttrArray:
    """Table attribute wrapper."""
    def __init__(self, init_array: list[TableAttr]):
        """
        Parameters
        ----------
        init_array : list[TableAttr]
            Initial array (only support 1D/2D array).
        """
        self._array = init_array
        if len(init_array) and type(init_array[0]) is list:
            self._ndim = 2
        else:
            self._ndim = 1
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._array})"

    def _shape(self, array: list[Any|list[Any]]) -> tuple[int]:
        """shape of the array."""
        if (ax1:=len(array)) and type(array[0]) is list:
            return (ax1, len(array[0]))
        else:
            return (ax1,)

    def _get_attr(self, attr: str) -> list[Align|list[Align]]:
        if self._ndim == 2:
            return [[cell.__dict__[attr] for cell in row] for row in self._array]
        else:
            return [cell.__dict__[attr] for cell in self._array]

    def _set_attr(self, attr: str, vlist: list[Align|list[Align]]):
        if type(vlist) is not list:
            msg = f"Input need be a list."
            raise ValueError(msg)
        if (ax1:=self.shape) != (ax2:=self._shape(vlist)):
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)
        if self._ndim == 2:
            for r in range(ax1[0]):
                for c in range(ax1[1]):
                    self._array[r][c].__dict__[attr] = vlist[r][c]
        else:
            for r in range(ax1[0]):
                self._array[r].__dict__[attr] = vlist[r]

    @property
    def shape(self) -> tuple[int]:
        """shape of the array."""
        return self._shape(self._array)

    @property
    def ndim(self) -> int:
        """dimensions of the array."""
        return self._ndim

    @property
    def align(self) -> list[Align|list[Align]]:
        """align for table printing."""
        return self._get_attr('align')

    @align.setter
    def align(self, vlist: list[Align|list[Align]]):
        """align for table printing."""
        self._set_attr('align', vlist)

    @property
    def is_sep(self) -> list[Align|list[Align]]:
        """separation enable for table printing."""
        return self._get_attr('is_sep')

    @is_sep.setter
    def is_sep(self, vlist: list[Align|list[Align]]):
        """separation enable for table printing."""
        self._set_attr('is_sep', vlist)

    @property
    def fs(self) -> list[Align|list[Align]]:
        """f-string for table printing."""
        return self._get_attr('fs')

    @fs.setter
    def fs(self, vlist: list[Align|list[Align]]):
        """f-string for table printing."""
        self._set_attr('fs', vlist)

    @property
    def border(self) -> list[Align|list[Align]]:
        """border type for table printing."""
        return self._get_attr('border')

    @border.setter
    def border(self, vlist: list[Align|list[Align]]):
        """border type for table printing."""
        self._set_attr('border', vlist)


class Array:
    """Table wrapper."""
    def __init__(self, init_array: list[Any]):
        """
        Parameters
        ----------
        init_array : list[Any]
            Initial array (only support 1D/2D array).
        """
        self._array = init_array
        if len(init_array) and type(init_array[0]) is list:
            self._ndim = 2
        else:
            self._ndim = 1
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._array})"

    def __add__(self, that: 'Array') -> 'Array':
        if (ax1:=self.shape) != (ax2:=that.shape):
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)
        if self._ndim == 2:
            new = [[self._array[r][c] + that._array[r][c] 
                    for c in range(ax1[1])] 
                    for r in range(ax1[0])]
        else:
            new = [self._array[i] + that._array[i] 
                   for i in range(ax1[0])]
        return self.__class__(new)

    def __sub__(self, that: 'Array') -> 'Array':
        if (ax1:=self.shape) != (ax2:=that.shape):
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)
        if self._ndim == 2:
            new = [[self._array[r][c] - that._array[r][c] 
                    for c in range(ax1[1])] 
                    for r in range(ax1[0])]
        else:
            new = [self._array[i] - that._array[i] 
                   for i in range(ax1[0])]
        return self.__class__(new)

    def __mul__(self, that: 'Array') -> 'Array':
        if (ax1:=self.shape) != (ax2:=that.shape):
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)
        if self._ndim == 2:
            new = [[self._array[r][c] * that._array[r][c] 
                    for c in range(ax1[1])] 
                    for r in range(ax1[0])]
        else:
            new = [self._array[i] * that._array[i] 
                   for i in range(ax1[0])]
        return self.__class__(new)

    def __truediv__(self, that: 'Array') -> 'Array':
        if (ax1:=self.shape) != (ax2:=that.shape):
            msg = f"Shapes difference. (self:{ax1}, that:{ax2})"
            raise ValueError(msg)
        if self._ndim == 2:
            new = [[self._array[r][c] / that._array[r][c] 
                    for c in range(ax1[1])] 
                    for r in range(ax1[0])]
        else:
            new = [self._array[i] / that._array[i] 
                   for i in range(ax1[0])]
        return self.__class__(new)

    def __getitem__(self, index) -> 'Array':
        if type(index) is tuple:
            rs, cs = index
            if type(rs) is slice:
                new = [row[cs] for row in self._array[rs]]
            else:
                new = self._array[rs][cs]
        else:
            new = copy.deepcopy(self._array[index])
        return self.__class__(new) if type(new) is list else new

    def __setitem__(self, index, that):
        if type(that) is self.__class__:
            that = that._array
        if self._ndim == 2:
            mr, mc = self.shape
            if type(index) is tuple:
                rs, cs = index
                if type(rs) is slice:
                    for i, r in enumerate(range(*rs.indices(mr))):
                        if type(cs) is slice:
                            for j, c in enumerate(range(*cs.indices(mc))):
                                self._array[r][c] = that[i][j]
                        else:
                            self._array[r][cs] = that[i]
                elif type(cs) is slice:
                    for i, c in enumerate(range(*cs.indices(mc))):
                        self._array[rs][c] = that[i]
                else:
                    self._array[rs][cs] = that
            elif type(index) is slice:
                for i, r in enumerate(range(*index.indices(mr))):
                    for c in range(self.shape[1]):
                        self._array[r][c] = that[i][c]
            else:
                for c in range(self.shape[1]):
                    self._array[index][c] = that[c]
        elif type(index) is slice:
            for i, r in enumerate(range(*index.indices(self.shape[0]))):
                self._array[r] = that[i]
        else:
            self._array[index] = that

    @property
    def shape(self) -> tuple[int]:
        """shape of the array."""
        if (ax1:=len(self._array)) and type(self._array[0]) is list:
            return (ax1, len(self._array[0]))
        else:
            return (ax1,)

    @property
    def ndim(self) -> int:
        """dimensions of the array."""
        return self._ndim

    def tolist(self) -> list[Any]:
        """array to list."""
        return copy.deepcopy(self._array)


class SimpleTable:
    """A Simple Text Table Generator."""
    def __init__(self, 
                 heads: list[tuple[str]], 
                 sep: str = '.', 
                 rdiv_cnt: int = 0, 
                 is_partp: bool = True, 
                 border: None|Border = None,
                 lsh:  int = 0,
                 hpat: str = '-', 
                 hcpat: str = '+', 
                 vpat: str = '-', 
                 vcpat: str = '+', 
                 spat: str = '|',
                 cpat_alon: bool = False):
        """
        Arguments
        ---------
        heads : list[tuple[str]]
            The header list of the table, format is bellow:
            [(key1, title1), (key2, title2), ...]
            Key & Title must be string type.
        sep : str, optional
            Separator used to split the string. Default is '.'.
        rdiv_cnt : int, optional
            Number of rows between two data row dividers. Default is 0 means 
            inifite.
        is_partp : bool, optional
            Partial value print if the length of the table value is greater 
            than the column width. Default is True.
            If any cell's attribute 'is_sep' is True, force to True.
        border : {None, Border}, optional
            Set the border around the table is hide or reveal. Default is all 
            borders reveal.
        lsh : int, optional
            left shift offset for table printing. Default is 0.
        hpat : str, optional
            Header divider pattern for table printing. Default is '-'.
        hcpat : str, optional
            Cross corner pattern of the header for table printing. 
            Default is '+'.
        vpat : str, optional
            Content divider for table printing. Default is '-'.
        vcpat : str, optional
            Cross corner pattern of the content for table printing. 
            Default is '+'.
        spat : str, optional
            Column separate pattern for table printing. Default is '|'.
        cpat_alon : bool, optional
            Always show the cross corner pattern for table printing.
            Default is False.
        """
        self._sep = sep
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt
        self.is_partp = is_partp
        self.border = Border() if border is None else border
        self.lsh = lsh
        self.hpat = hpat
        self.hcpat = hcpat
        self.vpat = vpat 
        self.vcpat = vcpat
        self.spat = spat 
        self.cpat_alon = cpat_alon

        self._max_row = 0
        self._index_head = HeadAttr(None, '')
        self._index = []
        self._header = []
        self._table = []
        self._attr = []
        for i, (key, title) in enumerate(heads):
            self._header.append(HeadAttr(key, title))

    class _IndexLocation:
        def __init__(self, head: list[HeadAttr]):
            self._head = head

        def __repr__(self):
            return f"{self.__class__.__name__}({self._head})"

        def __getitem__(self, index: int|str|slice) -> Index:
            index = (self._get_index(index, 2) if type(index) is slice
                        else self._get_index(index, 1))
            new = self._head[index]
            return Index(new) if type(new) is list else new 

        def _get_index(self, index: int|str|slice, itype: int) -> int|slice:
            if itype == 1:
                return index if type(index) is int else self.id[index]
            elif itype == 2:
                st = (0 if index.start is None
                        else index.start if type(index.start) is int
                        else self.id[index.start])
                ed = (len(self._head) if index.stop is None
                        else index.stop if type(index.stop) is int
                        else self.id[index.stop]+1)
                return slice(st, ed)

        @property
        def id(self) -> dict[str, int]:
            """key/id pair of the header."""
            vdict = {}
            for i, cell in enumerate(self._head):
                if type(key:=cell.key) is not str:
                    msg = f"Hash key must be the string type (id[{i}]={key})."
                    raise KeyError(msg)
                elif key in vdict:
                    msg = f"Hash key repeat (id[{vdict[key]}]==id[{i}])."
                    raise KeyError(msg)
                else:
                    vdict[key] = i
            return vdict 

    class _AttrLocation:
        def __init__(self, head: list[HeadAttr], index: list[HeadAttr], 
                     attr: list[TableAttr]):
            self._head = head
            self._index = index 
            self._attr = attr 

        def __repr__(self):
            return f"{self.__class__.__name__}({self._attr})"

        def __getitem__(self, index: int|str|slice|tuple) -> AttrArray:
            cidx = lambda x,y: self._get_index(self._head, x, y)
            ridx = lambda x,y: self._get_index(self._index, x, y)
            if type(index) is tuple:
                rs, cs = index
                if type(rs) is slice:
                    rs = ridx(rs, 2)
                    cs = cidx(cs, 2) if type(cs) is slice else cidx(cs, 1)
                    new = [row[cs] for row in self._attr[rs]]
                elif type(cs) is slice:
                    new = self._attr[ridx(rs, 1)][cidx(cs, 2)]
                else:
                    new = self._attr[ridx(rs, 1)][cidx(cs, 1)]
            elif type(index) is slice:
                new = copy.deepcopy(self._attr[ridx(index, 2)])
            else:
                new = copy.deepcopy(self._attr[ridx(index, 1)])
            return AttrArray(new) if type(new) is list else new

        def _get_index(self, idata: list, index: int|str|slice, itype: int) \
                       -> int|slice:
            if itype == 1:
                return (index if type(index) is int
                            else self._get_id(idata)[index])
            elif itype == 2:
                st = (0 if index.start is None
                        else index.start if type(index.start) is int
                        else self._get_id(idata)[index.start])
                ed = (len(idata) if index.stop is None
                        else index.stop if type(index.stop) is int
                        else self._get_id(idata)[index.stop]+1)
                return slice(st, ed)

        def _get_id(self, idata: list) -> dict[str, int]:
            """key/id pair of the header or index."""
            vdict = {}
            for i, cell in enumerate(idata):
                if type(key:=cell.key) is not str:
                    msg = f"Hash key must be the string type (id[{i}]={key})."
                    raise KeyError(msg)
                elif key in vdict:
                    msg = f"Hash key repeat (id[{vdict[key]}]==id[{i}])."
                    raise KeyError(msg)
                else:
                    vdict[key] = i
            return vdict 

    @property
    def sep(self) -> str:
        """string separator."""
        return self._sep

    @property
    def rdiv_cnt(self) -> int:
        """row count between two data dividers."""
        return 0 if self._rdiv_cnt == math.inf else self._rdiv_cnt

    @rdiv_cnt.setter
    def rdiv_cnt(self, rdiv_cnt: int):
        """row count between two data dividers."""
        self._rdiv_cnt = math.inf if rdiv_cnt == 0 else rdiv_cnt

    @property
    def max_row(self) -> int:
        """row number of table."""
        return self._max_row

    @property
    def max_col(self) -> int:
        """column number of table."""
        return len(self._header)

    @property
    def header(self) -> _IndexLocation:
        """column header information."""
        return self._IndexLocation(self._header)

    @property
    def index(self) -> _IndexLocation:
        """row index information."""
        return self._IndexLocation(self._index)

    @property
    def attr(self) -> _AttrLocation:
        """table attribute information"""
        return self._AttrLocation(self._header, self._index, self._attr)

    @property
    def index_head(self) -> HeadAttr:
        """column header of the row index."""
        return self._index_head

    def _get_index(self, idata: list, index: int|str|slice, itype: int) \
                   -> int|slice:
        if itype == 1:
            return (index if type(index) is int
                        else self._get_id(idata)[index])
        elif itype == 2:
            st = (0 if index.start is None
                    else index.start if type(index.start) is int
                    else self._get_id(idata)[index.start])
            ed = (len(idata) if index.stop is None
                    else index.stop if type(index.stop) is int
                    else self._get_id(idata)[index.stop]+1)
            return slice(st, ed)

    def _get_id(self, idata: list) -> dict[str, int]:
        """key/id pair of the header or index."""
        vdict = {}
        for i, cell in enumerate(idata):
            if type(key:=cell.key) is not str:
                msg = f"Hash key must be the string type (id[{i}]={key})."
                raise KeyError(msg)
            elif key in vdict:
                msg = f"Hash key repeat (id[{vdict[key]}]==id[{i}])."
                raise KeyError(msg)
            else:
                vdict[key] = i
        return vdict 

    def __getitem__(self, index: int|str|slice|tuple) -> Array:
        cidx = lambda x,y: self._get_index(self._header, x, y)
        ridx = lambda x,y: self._get_index(self._index, x, y)
        if type(index) is tuple:
            rs, cs = index
            if type(rs) is slice:
                rs = ridx(rs, 2)
                cs = cidx(cs, 2) if type(cs) is slice else cidx(cs, 1)
                new = [row[cs] for row in self._table[rs]]
            elif type(cs) is slice:
                new = self._table[ridx(rs, 1)][cidx(cs, 2)]
            else:
                new = self._table[ridx(rs, 1)][cidx(cs, 1)]
        elif type(index) is slice:
            new = copy.deepcopy(self._table[ridx(index, 2)])
        else:
            new = copy.deepcopy(self._table[ridx(index, 1)])
        return Array(new) if type(new) is list else new

    def __setitem__(self, index: int|str|slice|tuple, that: Any):
        cidx = lambda x,y: self._get_index(self._header, x, y)
        ridx = lambda x,y: self._get_index(self._index, x, y)
        mr, mc = self.max_row, self.max_col
        if type(that) is Array:
            that = that._array
        if type(index) is tuple:
            rs, cs = index
            if type(rs) is slice:
                rrs = range(*ridx(rs, 2).indices(mr))
                for i, r in enumerate(rrs):
                    if type(cs) is slice:
                        rcs = range(*cidx(cs, 2).indices(mc))
                        for j, c in enumerate(rcs):
                            self._table[r][c] = that[i][j]
                    else:
                        self._table[r][cidx(cs, 1)] = that[i]
            elif type(cs) is slice:
                r, rcs = ridx(rs, 1), range(*cidx(cs, 2).indices(mc))
                for i, c in enumerate(rcs):
                    self._table[r][c] = that[i]
            else:
                self._table[ridx(rs, 1)][cidx(cs, 1)] = that
        elif type(index) is slice:
            rrs = range(*ridx(index, 2).indices(mr))
            for i, r in enumerate(rrs):
                for c in range(mc):
                    self._table[r][c] = that[i][c]
        else:
            r = ridx(index, 1)
            for c in range(mc):
                self._table[r][c] = that[c]

    def add_row(self, key: None|str, title: str, data: list[Any], 
                init: Any = '', loc: None|str|int = None,
                align: Align = Align.NONE,
                is_sep: None|bool = None,
                fs: None|str = None,
                border: None|Border = None):
        """
        Add a new row to the table.

        Parameters
        ----------
        key : {None, str}
            Row hash key.
        title : str
            Row title.
        data : list[Any] 
            Value list.
        init : Any, optional
            Initial value used if number of columns of a row is smaller than 
            the length of the value list. Default is ''.
        loc : {None, str, int}
            Insert new row before the row specificed by row hash key or ID.
            Default is None means append new row to table.
        align : Align, optional
            Data align for table printing. Default is Align.NONE.
        is_sep : {None, bool}, optional
            String separate by the separator. Default is None.
        fs : {None, str}, optional
            Format string for table printing. Default is None.
        border: {None, Border}, optional
            Border display setting. Default is None. 

        Notes
        -----
        If the value of an attribute is None, copy the setting from 
        the above row.
        """
        if loc is None:
            rid = self.max_row
        else:
            rid = self.index.id[loc] if type(loc) is str else loc
        data_size = len(data)
        self._index.insert(rid, HeadAttr(key, title))
        self._table.insert(rid, row:=[])
        self._attr.insert(rid, attr:=[])
        self._max_row += 1
        for i in range(self.max_col):
            if self.max_row == 1:
                align_ = align if align != Align.NONE else Align.TL
                is_sep_ = is_sep if is_sep is not None else False
                fs_ = fs if fs is not None else "{}"
                border_ = border if border is not None else Border()
            else:
                align_ = align if align != Align.NONE \
                            else self._attr[rid-1][i].align
                is_sep_ = is_sep if is_sep is not None \
                            else self._attr[rid-1][i].is_sep
                fs_ = fs if fs is not None \
                            else self._attr[rid-1][i].fs
                border_ = border if border is not None \
                            else copy.copy(self._attr[rid-1][i].border)

            row.append(data[i] if i < data_size else init)
            attr.append(TableAttr(align=align_, 
                                  is_sep=is_sep_,
                                  fs=fs_,
                                  border=border_))

    def add_col(self, key: None|str, title: str, data: list[Any], 
                init: Any = '', loc: None|str|int = None,
                align: Align = Align.TL,
                is_sep: bool = False,
                fs: str = "{}",
                border : None|Border = None):
        """
        Add a new column to the table.

        Parameters
        ----------
        key : {None, str}
            Column hash key.
        title : str
            Column title.
        data : list[Any]
            Value list.
        init : Any, optional
            Initial value used if number of rows of a column is smaller than 
            the length of the value list. Default is ''.
        loc : {None, str, int}
            Insert new column before the column specificed by column hash key 
            or ID. Default is None means append new column to table.
        align : Align, optional
            Data align for table printing. Default is Align.NONE.
        is_sep : bool, optional
            String separate by the separator. Default is False.
        fs : str, optional
            Format string for table printing. Default is "{}".
        border: Border, optional
            Border display setting. Default is true for all edges. 
        """
        if loc is None:
            cid = self.max_col
        else:
            cid = self.header.id[loc] if type(loc) is str else loc
        data_size = len(data)
        self._header.insert(cid, HeadAttr(key, title))
        for i in range(self.max_row):
            value = data[i] if i < data_size else init
            self._table[i].insert(cid, value)
            self._attr[i].insert(cid, TableAttr(align=align,
                                                is_sep=is_sep,
                                                fs=fs,
                                                border=border))

    def swap_row(self, index1: str|int, index2: str|int):
        """
        Swap two specific rows.

        Parameters
        ----------
        index1 : {str, int}
            Row1 hash key or ID.
        index2 : {str, int}
            Row2 hash key or ID.
        """
        rid1 = self.index.id[index1] if type(index1) is str else index1
        rid2 = self.index.id[index2] if type(index2) is str else index2
        self._index[rid1], self._index[rid2] = (
            self._index[rid2], self._index[rid1])
        self._table[rid1], self._table[rid2] = (
            self._table[rid2], self._table[rid1])
        self._attr[rid1], self._attr[rid2] = (
            self._attr[rid2], self._attr[rid1])

    def swap_col(self, index1: str|int, index2: str|int):
        """
        Swap two specific columns.

        Parameters
        ----------
        index1 : {str, int}
            Column1 hash key or ID.
        index2 : {str, int}
            Column2 hash key or ID.
        """
        cid1 = self.header.id[index1] if type(index1) is str else index1
        cid2 = self.header.id[index2] if type(index2) is str else index2
        self._header[cid1], self._header[cid2] = (
            self._header[cid2], self._header[cid1])
        for i in range(self.max_row):
            self._table[i][cid1], self._table[i][cid2] = (
                self._table[i][cid2], self._table[i][cid1])
            self._attr[i][cid1], self._attr[i][cid2] = (
                self._attr[i][cid2], self._attr[i][cid1])

    def del_row(self, index: str|int):
        """
        Delete the specific row.

        Parameters
        ----------
        index : {str, int}
            Row hash key or ID.
        """
        if self.max_row > 0:
            rid = self.index.id[index] if type(index) is str else index
            del self._index[rid]
            del self._table[rid]
            del self._attr[rid]
            self._max_row -= 1

    def del_col(self, index: str|int):
        """
        Delete the specific column.

        Parameters
        ----------
        index : {str, int}
            Column hash key or ID.
        """
        cid = self.header.id[index] if type(index) is str else index
        del self._header[cid]
        for i in range(self.max_row):
            del self._table[i][cid]
            del self._attr[i][cid]
        if self.max_col == 0:
            self._header.append(HeadAttr('title1', 'Title1'))

    def set_head_attr(self, width: None|int = None, align: None|Align = None,
                      is_sep: None|bool = None, border: None|Border = None,
                      lofs: None|int = None, rofs: None|int = None):
        """
        Change head attribute over all head cells.

        Parameters
        ----------
        width : {None, int}, optional
            Column width.
        align : {None, Align}, optional
            Title align for table printing. 
        is_sep : {None, bool}, optional
            String separate by the separator.
        border : {None, Border}, optional
            Border setting.
        lofs : int, optional
            Number of blanks on the left side of the value string. 
        rofs : int, optional
            Number of blanks on the right side of the value string. 

        Notes
        -----
        Default None means no change.
        """
        for cell in self._header:
            if width is not None:
                cell.width = width
            if align is not None:
                cell.align = align
            if is_sep is not None:
                cell.is_sep = is_sep
            if border is not None:
                cell.border = copy.copy(border)
            if lofs is not None:
                cell.lofs = lofs
            if rofs is not None:
                cell.rofs = rofs

    def set_index_attr(self, width: None|int = None, align: None|Align = None,
                       is_sep: None|bool = None, border: None|Border = None,
                       lofs: None|int = None, rofs: None|int = None):
        """
        Change index attribute over all index cells.

        Parameters
        ----------
        width : {None, int}, optional
            Column width.  If width is 0 means use the maximum length of 
            the header title or table values as the column width when table 
            printing.
        align : {None, Align}, optional
            Title align for table printing.
        is_sep : {None, bool}, optional
            String separate by the separator.
        border : {None, Border}, optional
            Border setting.
        lofs : int, optional
            Number of blanks on the left side of the value string. 
        rofs : int, optional
            Number of blanks on the right side of the value string. 

        Notes
        -----
        Default None means no change.
        """
        if width is not None:
            self._index_head.width = width
        if lofs is not None:
            self._index_head.lofs = lofs
        if rofs is not None:
            self._index_head.rofs = rofs
        for cell in self._index:
            if align is not None:
                cell.align = align
            if is_sep is not None:
                cell.is_sep = is_sep
            if border is not None:
                cell.border = copy.copy(border)

    def set_row_attr(self, index: int, align: None|Align = None, 
                     is_sep: None|bool = None, fs: None|str = None, 
                     border: None|Border = None):
        """
        Set cell attribute for one data row.

        Parameters
        ----------
        index : int
            Row ID.
        align : {None, Align}, optional
            Title align for table printing. Default is None means no change.
        is_sep : {None, bool}, optional
            String separate by the separator. Default is None means no change.
        fs : {None, str}, optional
            Format string for table print. Default is None means no change.
        border : {None, Border}, optional
            Border setting. Default is None means no change.

        Notes
        -----
        Native table doesn't support cell attribute setting.
        """
        msg = "Native table doesn't support cell attribute setting."
        for i in range(self.max_col):
            if align is not None:
                self._attr[index][i].align = align
            if is_sep is not None:
                self._attr[index][i].is_sep = is_sep
            if fs is not None:
                self._attr[index][i].fs = fs
            if border is not None:
                self._attr[index][i].border = copy.copy(border)

    def set_col_attr(self, index: str|int, width: None|int = None, 
                     align: None|Align = None, is_sep: None|bool = None, 
                     fs: None|str = None, border: None|Border = None):
        """
        Set cell attribute for one data column.

        Parameters
        ----------
        index : {str, int}
            Column hash key or ID.
        width : {None, int}, optional
            Column width. Default is None means no change.
            If width is 0 means use the maximum length of the header title 
            or table values as the column width when table printing.
        align : {None, Align}, optional
            Title align for table printing. Default is None means no change.
        is_sep : {None, bool}, optional
            String separate by the separator. Default is None means no change.
        fs : {None, str}, optional
            Format string for table print. Default is None means no change.
        border : {None, Border}, optional
            Border setting. Default is None means no change.

        Notes
        -----
        Native table doesn't support cell attribute setting.
        """
        msg = "Native table doesn't support cell attribute setting."
        cid = self.header.id[index] if type(index) is str else index
        if width is not None:
            self._header[cid].width = width
        for i in range(self.max_row):
            if align is not None:
                self._attr[i][cid].align = align
            if is_sep is not None:
                self._attr[i][cid].is_sep = is_sep
            if fs is not None:
                self._attr[i][cid].fs = fs
            if border is not None:
                self._attr[i][cid].border = copy.copy(border)

    def get_head_width(self) -> list[int]:
        """
        Get title width of head cells.  
        """
        tlist = []
        for cell in self._header:
            if cell.is_sep:
                toks = cell.title.split(self.sep)
                tlist.append(max([len(x) for x in toks]))
            else:
                tlist.append(len(cell.title))
        return tlist

    def get_col_width(self, index: str|int) -> int:
        """
        Get a width of the spedific data column.

        Parameters
        ----------
        index : {str, int}
            Column hash key or ID.
        """
        cid = self.header.id[index] if type(index) is str else index
        title = self._header[cid].title
        tlist = title.split(self._sep) if self._header[cid].is_sep else [title]
        size = self._header[cid].width
        if (size2:=max([len(x) for x in tlist])) > size:
            size = size2

        if self._header[cid].width == 0:
            for r in range(self.max_row):
                str_ = self._attr[r][cid].fs.format(self._table[r][cid])
                if self._attr[r][cid].is_sep:
                    vlist = str_.split(self._sep)
                else:
                    vlist = [str_]
                if (size2:=max([len(x) for x in vlist])) > size:
                    size = size2
        return size

    def _div_gen(self, wlist: list[int], alist: list[TableAttr], 
                 hlist: list[HeadAttr], cpat: str, dpat: str, 
                 palist: None|list[TableAttr] = None, 
                 is_bottom: bool = False) -> str:
        """
        Print table divider.

        Parameters
        ----------
        wlist : list[int]
            list of column width.
        alist : list[TableAttr]
            list of cell attributes.
        hlist : list[HeadAttr]
            list of header cells.
        cpat : str
            cross corner pattern for table printing.
        dpat : str
            divider pattern for table printing.
        palist : {None, list[TableAttr]}, optional
            list of cell attributes of the abover row. If palist is not None, 
            border check will reference it. Default is None.
        is_bottom : bool, optional
            Generate bottom divider. Default is False.
        """
        div_str = ' ' * self.lsh
        for i in range(len(wlist)):
            is_cor = self.cpat_alon
            is_cor |= alist[i].border.left
            is_cor |= alist[i-1].border.right if i > 0 else False
            if is_bottom:
                is_bor = alist[i].border.bottom
            else:
                is_bor = alist[i].border.top
                if palist:
                    is_cor |= palist[i].border.left
                    is_cor |= palist[i-1].border.right if i > 0 else False
                    is_bor |= palist[i].border.bottom
            if i > 0 or self.border.left:
                div_str += (cpat if is_cor else ' ')
            div_str += ((dpat if is_bor else ' ') * 
                        (wlist[i] + hlist[i].lofs + hlist[i].rofs))
        is_cor = self.cpat_alon
        is_cor |= alist[-1].border.right
        is_cor |= palist[-1].border.right if palist else False
        if self.border.right:
            div_str += cpat if is_cor else ' '
        return div_str

    def print(self, fp = None, column: None|list[str|int] = None, 
              row: None|list[str|int] = None):
        """
        Print the table.

        Parameters
        ----------
        fp : IO wrapper, optional      
            Set I/O wrapper to print(). Default is None.
        column : None|list[str|int], optional
            Specify columns by column hash key or ID. Default is None means 
            print all columns.
        row : None|list[str|int], optional
            Specify rows by row hash key or ID. Default is None means print 
            all rows.
        """
        sep, head = self._sep, self._header
        table, attr = self._table, self._attr

        if column is not None:
            col_list = column.copy()
            if type(col_list[0]) is str:
                col_list = [self.header.id[x] for x in col_list]
        else:
            col_list = list(range(self.max_col))

        if row is not None:
            row_list = row.copy()
            if type(row_list[0]) is str:
                row_list = [self.index.id[x] for x in row_list]
        else:
            row_list = list(range(self.max_row))

        csize_list = []
        hdata_list, hrow_cnt = [], []
        vdata_list, vrow_cnt = [], []

        ## get head data
        for c in col_list:
            if head[c].is_sep:
                hdata_list.append(head[c].title.split(sep))
            else:
                hdata_list.append([head[c].title])
            hrow_cnt.append(len(hdata_list[-1]))
            size = max([len(x) for x in hdata_list[-1]])
            size2 = head[c].width
            csize_list.append(size if size > size2 else size2)

        ## get value data
        is_force_partp = False
        for r in row_list:
            vdata_list.append(row:=[])
            vrow_cnt.append(row_cnt:=[])
            for i, c in enumerate(col_list):
                str_val = attr[r][c].fs.format(table[r][c])
                if attr[r][c].is_sep:
                    row.append(str_val.split(sep))
                else:
                    row.append([str_val])
                if (rcnt:=len(row[-1])) > 1:
                    is_force_partp = True
                row_cnt.append(rcnt)
                if head[c].width == 0:
                    size = max([len(x) for x in row[-1]])
                    if size > csize_list[i]:
                        csize_list[i] = size

        ## divider print
        if self.border.top:
            str_ = self._div_gen(wlist=csize_list, 
                                 alist=[head[c] for c in col_list],
                                 hlist=[head[c] for c in col_list],
                                 cpat=self.hcpat, dpat=self.hpat)
            print(str_, file=fp)

        ## header print
        max_row, row_st, row_ed = max(hrow_cnt), [], []
        for i, c in enumerate(col_list):
            match (align:=head[c].align):
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

        ofs = [(' ' * head[c].lofs, ' ' * head[c].rofs) for c in col_list]
        for r in range(max_row):
            str_ = ' ' * self.lsh
            for i, c in enumerate(col_list):
                if row_st[i] <= r < row_ed[i]:
                    str_val = hdata_list[i][r-row_st[i]]
                    match (align:=head[c].align):
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
                is_sep = head[col_list[i]].border.left
                is_sep |= head[col_list[i-1]].border.right if i > 0 else False
                if i > 0 or self.border.left:
                    str_ += self.spat if is_sep else ' '
                str_ += "{}{}{}".format(ofs[i][0], str_mdy, ofs[i][1])
            if self.border.right:
                str_ += self.spat if head[col_list[-1]].border.right else ' '
            print(str_, file=fp)

        ## table print
        row_cnt = 0
        for j, r in enumerate(row_list):
            ## header divider
            if j == 0:
                str_ = self._div_gen(
                        wlist=csize_list, 
                        alist=[attr[r][c] for c in col_list],
                        hlist=[head[c] for c in col_list],
                        cpat=self.hcpat, 
                        dpat=self.hpat,
                        palist=[head[c] for c in col_list])
                print(str_, file=fp)

            ## table divider print
            if row_cnt == self._rdiv_cnt:
                str_ = self._div_gen(
                        wlist=csize_list, 
                        alist=[attr[r][c] for c in col_list],
                        hlist=[head[c] for c in col_list],
                        cpat=self.vcpat, 
                        dpat=self.vpat,
                        palist=[attr[row_list[j-1]][c] for c in col_list])
                print(str_, file=fp)
                row_cnt = 1
            else:
                row_cnt = row_cnt + 1

            max_row, row_st, row_ed = max(vrow_cnt[j]), [], []
            for i, c in enumerate(col_list):
                match (align:=attr[r][c].align):
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
                str_ = ' ' * self.lsh
                acc_col_sz = 0 
                for i, c in enumerate(col_list):
                    if row_st[i] <= r2 < row_ed[i]:
                        str_val = vdata_list[j][i][r2-row_st[i]]
                        acc_col_sz += csize_list[i] \
                                        + head[c].lofs + head[c].rofs \
                                        + int(self.border.left)
                        match (align:=attr[r][c].align):
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
                                str_mdy = "{}{}{}".format(
                                            ofs[i][0],
                                            f"{str_mdy[:csize_list[i]-1]}>",
                                            ofs[i][1])
                            else:
                                str_mdy = "{}{}".format(
                                            ofs[i][0],
                                            f"{str_mdy}\n{' '*acc_col_sz}")
                        else:
                            str_mdy = "{}{}{}".format(ofs[i][0],
                                                      str_mdy,
                                                      ofs[i][1])
                    else:
                        str_mdy = "{}{}{}".format(ofs[i][0],
                                                  ' ' * csize_list[i],
                                                  ofs[i][1])

                    is_sep = attr[r][col_list[i]].border.left
                    if i > 0:
                        is_sep = attr[r][col_list[i-1]].border.right
                    if i > 0 or self.border.left:
                        str_ += (self.spat if is_sep else ' ') + str_mdy
                    else:
                        str_ += str_mdy

                is_sep = attr[r][col_list[-1]].border.right
                if self.border.right:
                    str_ += self.spat if is_sep else ' '
                print(str_, file=fp)

        ## divider print
        if not self.border.bottom:
            pass
        elif len(row_list) == 0:
            str_ = self._div_gen(
                    wlist=csize_list, 
                    alist=[head[c] for c in col_list], 
                    hlist=[head[c] for c in col_list],
                    cpat=self.hcpat, 
                    dpat=self.hpat)
            print(str_, file=fp)
            print(str_, file=fp)
        else:
            str_ = self._div_gen(
                    wlist=csize_list, 
                    alist=[attr[row_list[-1]][c] for c in col_list],
                    hlist=[head[c] for c in col_list],
                    cpat=self.hcpat, 
                    dpat=self.hpat,
                    is_bottom=True)
            print(str_, file=fp)


