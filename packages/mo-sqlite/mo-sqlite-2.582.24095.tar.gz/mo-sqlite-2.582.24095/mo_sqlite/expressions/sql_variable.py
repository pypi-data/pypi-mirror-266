# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import SqlVariable as _SqlVariable
from mo_sqlite.expressions._utils import SQLang, SqlScript, SQL
from mo_sqlite.utils import quote_column


class SqlVariable(_SqlVariable, SQL):
    lang = SQLang

    __new__ = object.__new__

    def __iter__(self):
        params = [p for p in self.es_path if p is not None]
        yield from quote_column(*params)

    def to_sql(self, schema):
        return SqlScript(jx_type=self.jx_type, expr=self, frum=self, schema=schema,)
