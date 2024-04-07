# -*- coding:utf-8 -*-
from pathlib import Path
from time import sleep

from .base import BaseRecorder
from .setter import RecorderSetter
from .style.cell_style import CellStyleCopier
from .tools import (ok_list, data_to_list_or_dict, process_content, data_to_list_or_dict_simplify, get_css_head, get_wb,
                    get_ws, get_xlsx_head, create_csv)


class Recorder(BaseRecorder):
    _SUPPORTS = ('csv', 'xlsx', 'json', 'txt')

    def __init__(self, path=None, cache_size=None):
        """用于缓存并记录数据，可在达到一定数量时自动记录，以降低文件读写次数，减少开销
        :param path: 保存的文件路径
        :param cache_size: 每接收多少条记录写入文件，0为不自动写入
        """
        super().__init__(path=path, cache_size=cache_size)
        self._delimiter = ','  # csv文件分隔符
        self._quote_char = '"'  # csv文件引用符
        self._follow_styles = False
        self._col_height = None
        self._style = None
        self._fit_head = False

    @property
    def set(self):
        """返回用于设置属性的对象"""
        if self._setter is None:
            self._setter = RecorderSetter(self)
        return self._setter

    @property
    def delimiter(self):
        """返回csv文件分隔符"""
        return self._delimiter

    @property
    def quote_char(self):
        """返回csv文件引用符"""
        return self._quote_char

    def add_data(self, data, table=None):
        """添加数据，可一次添加多条数据
        :param data: 插入的数据，任意格式
        :param table: 要写入的数据表，仅支持xlsx格式。为None表示用set.table()方法设置的值，为bool表示活动的表格
        :return: None
        """
        while self._pause_add:  # 等待其它线程写入结束
            sleep(.1)

        if not isinstance(data, (list, tuple, dict)):
            data = (data,)

        if not data:
            data = ([],)
            self._data_count += 1

        # 一维数组
        elif isinstance(data, dict) or (isinstance(data, (list, tuple))
                                        and not isinstance(data[0], (list, tuple, dict))):
            data = [data_to_list_or_dict(self, data)]
            self._data_count += 1

        else:  # 二维数组
            if self.after or self.before:
                data = [data_to_list_or_dict(self, d) for d in data]
            else:
                data = [data_to_list_or_dict_simplify(d) for d in data]
            self._data_count += len(data)

        if self._type != 'xlsx':
            self._data.extend(data)

        else:
            if table is None:
                table = self._table
            elif isinstance(table, bool):
                table = None

            self._data.setdefault(table, []).extend(data)

        if 0 < self.cache_size <= self._data_count:
            self.record()

    def _record(self):
        """记录数据"""
        if self.type == 'csv':
            self._to_csv()
        elif self.type == 'xlsx':
            self._to_xlsx()
        elif self.type == 'json':
            self._to_json()
        elif self.type == 'txt':
            self._to_txt()

    def _to_xlsx(self):
        """记录数据到xlsx文件"""
        wb, new_file = get_wb(self)
        tables = [i.title for i in wb.worksheets]

        for table, data in self._data.items():
            _row_styles = None
            _col_height = None
            ws, new_sheet = get_ws(wb, table, tables, new_file)

            # ---------处理表头和样式---------
            begin = get_xlsx_head(self, new_file, new_sheet, self._data[table][0], ws)

            max_row = None
            if self._follow_styles:
                max_row = ws.max_row
                _row_styles = [CellStyleCopier(i) for i in ws[max_row]]
                _col_height = ws.row_dimensions[max_row].height

            new_file = False

            # ==============开始写入数据==============
            if self._fit_head and self._head[ws.title]:
                for i in data[begin:]:
                    if isinstance(i, dict):
                        i = [i.get(h, None) for h in self._head[ws.title]]
                    ws.append(ok_list(i, True))
                    if self._follow_styles:
                        max_row += 1
                        _set_style(_col_height, _row_styles, ws, max_row, self)

            else:
                for i in data[begin:]:
                    ws.append(ok_list(i, True))
                    if self._follow_styles:
                        max_row += 1
                        _set_style(_col_height, _row_styles, ws, max_row, self)

        wb.save(self.path)
        wb.close()

    def _to_csv(self):
        """记录数据到csv文件"""
        if self._head is not None and not self._file_exists:
            create_csv(self)
        elif self._head is None:
            get_css_head(self)

        with open(self.path, 'a+', newline='', encoding=self.encoding) as f:
            from csv import writer
            csv_write = writer(f, delimiter=self.delimiter, quotechar=self.quote_char)
            if self._fit_head and self._head:
                for i in self._data:
                    if isinstance(i, dict):
                        i = [i.get(h, None) for h in self._head]
                    csv_write.writerow(ok_list(i))

            else:
                for i in self._data:
                    csv_write.writerow(ok_list(i))

    def _to_txt(self):
        """记录数据到txt文件"""
        with open(self.path, 'a+', encoding=self.encoding) as f:
            all_data = [' '.join(ok_list(i, as_str=True)) for i in self._data]
            f.write('\n'.join(all_data) + '\n')

    def _to_json(self):
        """记录数据到json文件"""
        from json import load, dump
        if self._file_exists or Path(self.path).exists():
            with open(self.path, 'r', encoding=self.encoding) as f:
                json_data = load(f)

        else:
            json_data = []

        for i in self._data:
            if isinstance(i, dict):
                for d in i:
                    i[d] = process_content(i[d])
                json_data.append(i)
            else:
                json_data.append([process_content(d) for d in i])

        self._file_exists = True
        with open(self.path, 'w', encoding=self.encoding) as f:
            dump(json_data, f)


def _set_style(_col_height, _row_styles, ws, max_row, recorder):
    if _col_height is not None:
        ws.row_dimensions[max_row].height = recorder._col_height

    if _row_styles:
        groups = zip(ws[max_row], _row_styles)
        for g in groups:
            g[1].to_cell(g[0])

    elif recorder._style:
        for c in ws[max_row]:
            recorder._style.to_cell(c)
