# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2016  Dominic Krimmer                                         #
#                     Luis Alfredo da Silva (luis.adasilvaf@gmail.com)        #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

from openerp import api, fields, models


from openerp.exceptions import UserError, ValidationError
from openerp.tools.translate import _
from openerp.tools import float_is_zero, float_compare
from openerp.addons.base.ir.ir_sequence import _update_nogap

import pprint
import logging
_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _name = 'ir.sequence'
    _inherit = 'ir.sequence'

    use_dian_control = fields.Boolean('Use DIAN control resolutions')
    remaining_numbers = fields.Integer(default=1, help='Remaining numbers')
    remaining_days = fields.Integer(default=1, help='Remaining days')
    sequence_dian_type = fields.Selection([
        ('invoice_computer_generated', 'Invoice generated from computer'),
        ('pos_invoice', 'POS Invoice')],
        'Type', required=True, default='invoice_computer_generated')
    dian_resolution_ids = fields.One2many('ir.sequence.dian_resolution', 'sequence_id', 'DIAN Resolutions')

    _defaults = {
        'remaining_numbers': 400,
        'remaining_days': 30,
    }

    def _next(self):
        if not self.use_dian_control:
            return super(IrSequence, self)._next()

        seq_dian_actual = self.env['ir.sequence.dian_resolution'].search([('sequence_id','=',self.id),('active_resolution','=',True)], limit=1)
        if seq_dian_actual.exists(): 
            number_actual = seq_dian_actual._next()
            if number_actual > seq_dian_actual['number_to']:
                seq_dian_next = self.env['ir.sequence.dian_resolution'].search([('sequence_id','=',self.id),('active_resolution','=',True)], limit=1, offset=1)
                if seq_dian_next.exists():
                    seq_dian_actual.active_resolution = False
                    return seq_dian_next._next()
            return number_actual
        return super(IrSequence, self)._next()


class IrSequenceDianResolution(models.Model):
    _name = 'ir.sequence.dian_resolution'
    _rec_name = "sequence_id"

    def _get_number_next_actual(self):
        for element in self:
            element.number_next_actual = element.number_next

    def _set_number_next_actual(self):
        for record in self:
            record.write({'number_next': record.number_next_actual or 0})

    @api.depends('number_from')
    def _get_initial_number(self):
        for record in self:
            if not record.number_next:
                record.number_next = record.number_from

    resolution_number = fields.Integer('Resolution number', required=True)
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    number_from = fields.Integer('Initial number', required=True)
    number_to = fields.Integer('Final number', required=True)
    number_next = fields.Integer('Next Number', compute='_get_initial_number', store=True)
    number_next_actual = fields.Integer(compute='_get_number_next_actual', inverse='_set_number_next_actual',
                                 string='Next Number', required=True, default=1, help="Next number of this sequence")
    active_resolution = fields.Boolean('Active resolution', required=False, default=True)
    sequence_id = fields.Many2one("ir.sequence", 'Main Sequence', required=True, ondelete='cascade')

    def _next(self):
        number_next = _update_nogap(self, 1)
        return self.sequence_id.get_next_char(number_next)

    @api.model
    def create(self, values):
        _logger.info(values)
        seq = super(IrSequenceDianResolution, self).create(values)
        return seq
