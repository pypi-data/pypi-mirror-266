# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import carrier, sale, stock

__all__ = ['register']


def register():
    Pool.register(
        carrier.Carrier,
        carrier.VolumePriceList,
        stock.ShipmentIn,
        stock.ShipmentOut,
        sale.Sale,
        module='carrier_weight_volume_combined', type_='model')
