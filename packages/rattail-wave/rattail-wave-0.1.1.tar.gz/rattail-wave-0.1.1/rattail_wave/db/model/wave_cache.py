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
Wave "cache" data models
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class WaveCacheCustomer(model.Base):
    """
    Represents a customer record in Wave.

    https://developer.waveapps.com/hc/en-us/articles/360019968212#customer
    """
    __tablename__ = 'wave_cache_customer'
    __table_args__ = (
        sa.UniqueConstraint('id', name='wave_cache_customer_uq_id'),
    )
    __versioned__ = {}
    model_title = "Wave Customer"

    uuid = model.uuid_column()

    id = sa.Column(sa.String(length=100), nullable=False)
    internal_id = sa.Column(sa.String(length=100), nullable=True)
    name = sa.Column(sa.String(length=255), nullable=True)
    email = sa.Column(sa.String(length=255), nullable=True)
    is_archived = sa.Column(sa.Boolean(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True)
    modified_at = sa.Column(sa.DateTime(), nullable=True)

    def __str__(self):
        return self.name or ""


class WaveCacheInvoice(model.Base):
    """
    Represents an invoice record in Wave.

    https://developer.waveapps.com/hc/en-us/articles/360019968212#invoice
    """
    __tablename__ = 'wave_cache_invoice'
    __table_args__ = (
        sa.UniqueConstraint('id', name='wave_cache_invoice_uq_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['wave_cache_customer.id'],
                                name='wave_cache_invoice_fk_customer'),
    )
    __versioned__ = {}
    model_title = "Wave Invoice"

    uuid = model.uuid_column()

    id = sa.Column(sa.String(length=100), nullable=False)
    internal_id = sa.Column(sa.String(length=100), nullable=True)

    customer_id = sa.Column(sa.String(length=100), nullable=False)
    customer = orm.relationship(WaveCacheCustomer,
                                backref=orm.backref('invoices'))

    status = sa.Column(sa.String(length=10), nullable=False)
    title = sa.Column(sa.String(length=255), nullable=False)
    subhead = sa.Column(sa.String(length=255), nullable=True)
    invoice_number = sa.Column(sa.String(length=10), nullable=False)
    invoice_date = sa.Column(sa.Date(), nullable=False)
    due_date = sa.Column(sa.Date(), nullable=False)
    amount_due = sa.Column(sa.Numeric(precision=9, scale=2), nullable=False)
    amount_paid = sa.Column(sa.Numeric(precision=9, scale=2), nullable=False)
    tax_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=False)
    total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=False)
    discount_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=False)
    # currency_code = sa.Column(sa.String(length=3), nullable=False)
    # exchange_rate = sa.Column(sa.Numeric(precision=10, scale=5), nullable=False)
    created_at = sa.Column(sa.DateTime(), nullable=True)
    modified_at = sa.Column(sa.DateTime(), nullable=True)

    def __str__(self):
        return self.title or ""
