# -*- coding: utf-8 -*-
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
Rattail -> Rattail data import for Wave integration
"""

from rattail.importing import rattail as base
from rattail_wave import importing as rattail_wave_importing


class FromRattailToRattailWaveMixin(object):
    """
    Add default registration of custom importers
    """

    def add_wave_importers(self, importers):
        importers['WaveCacheCustomer'] = WaveCacheCustomerImporter
        importers['WaveCacheInvoice'] = WaveCacheInvoiceImporter
        importers['WaveCustomer'] = WaveCustomerImporter
        return importers


##############################
# cache models
##############################

class WaveCacheCustomerImporter(base.FromRattail, rattail_wave_importing.model.WaveCacheCustomerImporter):
    pass

class WaveCacheInvoiceImporter(base.FromRattail, rattail_wave_importing.model.WaveCacheInvoiceImporter):
    pass


##############################
# integration models
##############################

class WaveCustomerImporter(base.FromRattail, rattail_wave_importing.model.WaveCustomerImporter):
    pass
