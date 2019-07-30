# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

CANCEL_MOVE_STATE = 'cancel'
DONE_PICKING_STATE = 'done'
INCOMING_PICKING_TYPE = 'incoming'

from . import mixins
from . import models
from . import wizard
