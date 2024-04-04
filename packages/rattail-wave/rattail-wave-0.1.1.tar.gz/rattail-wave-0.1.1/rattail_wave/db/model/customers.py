# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Wave integration data models
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class WaveCustomer(model.Base):
    """
    Wave-specific extension to Customer model
    """
    __tablename__ = 'wave_customer'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['customer.uuid'],
                                name='wave_customer_fk_customer'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)
    customer = orm.relationship(
        model.Customer,
        doc="""
        Reference to the actual customer record, which this one extends.
        """,
        backref=orm.backref(
            '_wave',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Reference to the Wave extension record for this customer.
            """))

    wave_id = sa.Column(sa.String(length=100), nullable=False, doc="""
    ``id`` value for the customer, within Wave.
    """)

    def __str__(self):
        return str(self.customer)


WaveCustomer.make_proxy(model.Customer, '_wave', 'wave_id')
