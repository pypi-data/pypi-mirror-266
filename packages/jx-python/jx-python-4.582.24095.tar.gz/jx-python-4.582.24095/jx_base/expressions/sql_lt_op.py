# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions.base_binary_op import BaseBinaryOp

from mo_json import JX_BOOLEAN


class SqlLtOp(BaseBinaryOp):
    _jx_type = JX_BOOLEAN
