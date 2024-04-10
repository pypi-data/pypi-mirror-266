# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal

from trytond.model import ModelSQL, ModelView, fields
from trytond.modules.currency.fields import Monetary
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval, Id
from trytond.transaction import Transaction


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'
    volume_uom = fields.Many2One('product.uom', 'Volume Uom',
        domain=[('category', '=', Id('product', 'uom_cat_volume'))],
        states={
            'invisible': Eval('carrier_cost_method') != 'weight_volume',
            'required': Eval('carrier_cost_method') == 'weight_volume',
            'readonly': Bool(Eval('volume_price_list', [])),
            })
    volume_uom_digits = fields.Function(fields.Integer('Volume Uom Digits'),
        'on_change_with_volume_uom_digits')
    volume_price_list = fields.One2Many('carrier.volume_price_list', 'carrier',
        'Volume Price List',
        states={
            'invisible': Eval('carrier_cost_method') != 'weight_volume',
            'readonly': ~(Eval('volume_uom', 0) & Eval('weight_currency', 0)),
            },
        help="Add price per volume to the carrier service.\n"
        "The first line for which the volume is greater is used.\n"
        "The line with volume of 0 is used as default price."
        )

    @classmethod
    def __setup__(cls):
        super(Carrier, cls).__setup__()
        selection = ('weight_volume', 'Weight Volume Combined')
        if selection not in cls.carrier_cost_method.selection:
            cls.carrier_cost_method.selection.append(selection)
        invisible = Eval('carrier_cost_method') != 'weight_volume'
        required = Eval('carrier_cost_method') == 'weight_volume'
        for fname in ('weight_uom', 'weight_currency', 'weight_price_list'):
            field = getattr(cls, fname)
            field.states['invisible'] = field.states.get('invisible') & invisible
            if field.states.get('required'):
                field.states['required'] = field.states.get('required') | required
        cls.weight_price_list.string = 'Weight Price List'

    @staticmethod
    def default_volume_uom_digits():
        return 2

    @fields.depends('volume_uom')
    def on_change_with_volume_uom_digits(self, name=None):
        if self.volume_uom:
            return self.volume_uom.digits
        return 2

    def compute_volume_price(self, volume):
        "Compute price based on volume"
        for line in reversed(self.volume_price_list):
            if line.volume < volume:
                return line.price
        else:
            if not line.volume and not volume:
                return line.price
        return Decimal(0)

    def _get_volume_price(self):
        volumes = Transaction().context.get('volumes', [])
        if volumes:
            volume_price = sum(
                self.compute_volume_price(v) for v in volumes)
        else:
            volume_price = self.compute_volume_price(0)
        return volume_price, self.weight_currency.id

    def get_sale_price(self):
        if self.carrier_cost_method == 'weight_volume':
            return self._compute_price()
        return super().get_sale_price()

    def get_purchase_price(self):
        if self.carrier_cost_method == 'weight_volume':
            return self._compute_price()
        return super().get_purchase_price()

    def _compute_price(self):
        '''
        The highest match for either weight or volume determines the
        necessary price
        '''
        weight_price, currency_id = self._get_weight_price()
        volume_price, currency_id = self._get_volume_price()
        return max(weight_price, volume_price), currency_id


class VolumePriceList(ModelSQL, ModelView):
    'Carrier Volume Price List'
    __name__ = 'carrier.volume_price_list'
    carrier = fields.Many2One('carrier', 'Carrier', required=True)
    volume = fields.Float('Volume', digits='volume_uom',
        domain=[
            ('volume', '>=', 0),
            ],
        depends={'carrier'})
    price = Monetary('Price', currency='currency', digits='currency')
    currency = fields.Function(fields.Many2One(
            'currency.currency', "Currency"),
        'on_change_with_currency')
    volume_uom = fields.Function(fields.Many2One(
            'product.uom', "Volume UoM",
            help="The Unit of Measure of the volume."),
        'on_change_with_volume_uom')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order.insert(0, ('volume', 'ASC'))

    @fields.depends('carrier', '_parent_carrier.weight_currency')
    def on_change_with_currency(self, name=None):
        if self.carrier and self.carrier.weight_currency:
            return self.carrier.weight_currency.id

    @fields.depends('carrier', '_parent_carrier.volume_uom')
    def on_change_with_volume_uom(self, name=None):
        return self.carrier.volume_uom if self.carrier else None
