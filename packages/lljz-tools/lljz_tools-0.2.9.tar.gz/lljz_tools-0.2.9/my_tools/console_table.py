# coding=utf-8
from typing import Iterable, Any
from my_tools.color import _Color
from my_tools.log_manager import LogManager

logger = LogManager('ConsoleTable').get_logger()


class ConsoleTable:

    def __init__(self, data: Iterable[dict[str, Any]], max_width=100, use_rich_table=False):
        def init_value(val):
            if isinstance(val, str | _Color):
                return val
            if val is None:
                return ''
            return str(val)

        self.data = [{str(k): init_value(v) for k, v in row.items()} for row in data]
        self.header = list(self.data[0].keys()) if data else []
        self.max_width = max_width
        self.col_width = []
        self._table_str = ""
        self.use_rich_table = use_rich_table
        if not self.use_rich_table:
            self.col_width = self._get_widths()
            self._table_str = self._make_table_str()

    def _make_rich_table(self, title: str):
        from rich.table import Table

        def get_value(val):
            if isinstance(val, _Color):
                return f'[{val.name}]{val.raw}[/{val.name}]'
            return val

        tb = Table(
            title=f'{title}' if title else None,
            title_style='b yellow',
            min_width=60)

        for key in self.header:
            tb.add_column(key, justify='center')
        for row in self.data:
            tb.add_row(*[get_value(row.get(key, '')) for key in self.header])
        return tb

    @staticmethod
    def _get_string_width(val: str):
        w = 0
        for v in val:
            if u'\u4e00' <= v <= u'\u9fff' or v in '【】（）—…￥！·、？。，《》：；‘“':
                w += 2
            else:
                w += 1
        return w

    def _get_widths(self):
        """获取列宽度，列宽度为整列数据中的最大数据宽度"""

        col_width = [self._get_string_width(key) for key in self.header]
        for row in self.data:
            for i, key in enumerate(self.header):
                value = row.get(key, '')
                width = min(self._get_string_width(value), self.max_width)
                col_width[i] = max(col_width[i], width)
        return col_width

    def _make_table_str(self):
        def format_str(val, width):
            length = self._get_string_width(val)
            left = (width - length) // 2
            right = (width - length) - left
            return f'{" " * left}{val}{" " * right}'

        header = ' | '.join(format_str(key, w) for w, key in zip(self.col_width, self.header))
        rows = [' | '.join(format_str(row.get(key, ""), w) for w, key in zip(self.col_width, self.header)) for row in
                self.data]
        return '\n'.join([header, '=' * (sum(self.col_width) + (len(self.col_width) - 1) * 3)] + rows)

    def __str__(self):
        if not self.use_rich_table:
            return self._table_str
        else:
            return self.__str__()

    __repr__ = __str__

    def show(self, message=''):
        if self.use_rich_table:
            from rich import print as rprint
            tb = self._make_rich_table(message)
            if tb.columns:
                rprint(tb)
            else:
                rprint(f'[i u yellow]🏃 {(message + " ") if message else ""}Table is Empty 🏃[/i u yellow]')
        else:
            logger.info(message + '\n' + str(self.__str__()))


if __name__ == '__main__':
    pass
