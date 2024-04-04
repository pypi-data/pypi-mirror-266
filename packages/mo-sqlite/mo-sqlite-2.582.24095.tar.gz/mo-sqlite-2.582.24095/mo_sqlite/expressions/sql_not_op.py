# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import NotOp as _NotOp
from mo_sql import SQL_NOT, SQL_OP, SQL_CP
from mo_sqlite.expressions._utils import SQL


class NotOp(_NotOp, SQL):
    def __iter__(self):
        yield from SQL_NOT
        yield from SQL_OP
        yield from self.term
        yield from SQL_CP
