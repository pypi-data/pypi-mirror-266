# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
Wave -> Rattail ("wave cache") data import
"""

import datetime
import decimal
from collections import OrderedDict

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from rattail import importing
from rattail_wave import importing as rattail_wave_importing


class FromWaveToRattail(importing.ToRattailHandler):
    """
    Import handler for data coming from the Wave API
    """
    host_key = 'wave'
    host_title = "Wave (API)"
    generic_host_title = "Wave (API)"

    def get_importers(self):
        importers = OrderedDict()
        importers['WaveCacheCustomer'] = WaveCacheCustomerImporter
        importers['WaveCacheInvoice'] = WaveCacheInvoiceImporter
        return importers


class FromWave(importing.Importer):
    """
    Base class for all Wave importers
    """
    key = 'id'

    @property
    def supported_fields(self):
        fields = list(super(FromWave, self).supported_fields)
        fields.remove('uuid')
        return fields

    def setup(self):
        super(FromWave, self).setup()
        self.setup_wave_api()

    def setup_wave_api(self):
        token = self.config.require('wave', 'api.full_access_token')

        self.wave_transport = RequestsHTTPTransport(
            url="https://gql.waveapps.com/graphql/public",
            headers={'Authorization': 'Bearer {}'.format(token)},
            verify=True,
            retries=3,
        )

        self.wave_client = Client(transport=self.wave_transport,
                                  fetch_schema_from_transport=True)

        self.wave_business_id = self.config.require('wave', 'business.id')

    def date_from_wave(self, value):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()

    def money_from_wave(self, value):
        return decimal.Decimal('{:0.2f}'.format(value['raw'] / 100.0))

    def time_from_wave(self, value):
        # all wave times appear to come as UTC, so no conversion needed
        value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        return value

    def normalize_host_object(self, obj):
        data = dict(obj)

        if 'internal_id' in self.fields:
            data['internal_id'] = data.pop('internalId')

        if 'created_at' in self.fields:
            data['created_at'] = self.time_from_wave(data.pop('createdAt'))

        if 'modified_at' in self.fields:
            data['modified_at'] = self.time_from_wave(data.pop('modifiedAt'))

        return data


class WaveCacheCustomerImporter(FromWave, rattail_wave_importing.model.WaveCacheCustomerImporter):
    """
    Import customer data from Wave
    """

    def get_host_objects(self):
        customers = []
        page = 1
        while True:

            query = gql(
                """
                query {
                  business(id: "%s") {
                    id
                    customers(page: %u, pageSize: 20, sort: [NAME_ASC]) {
                      pageInfo {
                        currentPage
                        totalPages
                        totalCount
                      }
                      edges {
                        node {
                          id
                          internalId
                          name
                          email
                          isArchived
                          createdAt
                          modifiedAt
                        }
                      }
                    }
                  }
                }
                """ % (self.wave_business_id, page)
            )

            result = self.wave_client.execute(query)
            data = result['business']['customers']
            customers.extend([edge['node'] for edge in data['edges']])

            if page >= data['pageInfo']['totalPages']:
                break

            page += 1

        return customers

    def normalize_host_object(self, customer):
        data = super(WaveCacheCustomerImporter, self).normalize_host_object(customer)

        data['is_archived'] = data.pop('isArchived')

        return data


class WaveCacheInvoiceImporter(FromWave, rattail_wave_importing.model.WaveCacheInvoiceImporter):
    """
    Import invoice data from Wave
    """

    def get_host_objects(self):
        invoices = []
        page = 1
        while True:

            query = gql(
                """
                query {
                  business(id: "%s") {
                    id
                    invoices(page: %u, pageSize: 20) {
                      pageInfo {
                        currentPage
                        totalPages
                        totalCount
                      }
                      edges {
                        node {
                          id
                          internalId
                          customer {
                            id
                          }
                          status
                          title
                          subhead
                          invoiceNumber
                          invoiceDate
                          dueDate
                          amountDue {
                            raw
                          }
                          amountPaid {
                            raw
                          }
                          taxTotal {
                            raw
                          }
                          total {
                            raw
                          }
                          discountTotal {
                            raw
                          }
                          createdAt
                          modifiedAt
                        }
                      }
                    }
                  }
                }
                """ % (self.wave_business_id, page)
            )

            result = self.wave_client.execute(query)
            data = result['business']['invoices']
            invoices.extend([edge['node'] for edge in data['edges']])

            if page >= data['pageInfo']['totalPages']:
                break

            page += 1

        return invoices

    def normalize_host_object(self, invoice):
        data = super(WaveCacheInvoiceImporter, self).normalize_host_object(invoice)

        customer = data.pop('customer')
        data['customer_id'] = customer['id']

        data['invoice_number'] = data.pop('invoiceNumber')
        data['invoice_date'] = self.date_from_wave(data.pop('invoiceDate'))
        data['due_date'] = self.date_from_wave(data.pop('dueDate'))
        data['amount_due'] = self.money_from_wave(data.pop('amountDue'))
        data['amount_paid'] = self.money_from_wave(data.pop('amountPaid'))
        data['tax_total'] = self.money_from_wave(data.pop('taxTotal'))
        data['total'] = self.money_from_wave(data.pop('total'))
        data['discount_total'] = self.money_from_wave(data.pop('discountTotal'))

        return data
