# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2016  Dominic Krimmer                                         #
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

# Extended Partner Module
from openerp import models, fields, api, exceptions
import re

class ColombianTaxes(models.Model):

    """ Model to create and manipulate personal taxes"""
    _description=  "Model to create own taxes"
    _name = 'account.invoice'
    _inherit = 'account.invoice'


    # This is a colombian tax named Retenciòn en la fuente
    rfuente = fields.Float('Retencion en la fuente')
    varp = fields.Float(string='variable de prueba')
    resul= fields.Integer(string='resultado',store=True, compute="_resul_pc")

    @api.one
    @api.depends('resul')
    def _resul_pc(self):
        self.resul =  100

    #@api.one
    #@api.onchange('resul')
    #def _onchange_field(self):
        #if self.resul:
            #resultado ="10"
        #self.resul= resultado
