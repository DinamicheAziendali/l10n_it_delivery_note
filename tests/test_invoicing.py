from odoo.addons.link_it_foundation.tests.account_invoice import AccountInvoiceTest


class InvoicingTest(AccountInvoiceTest):
    customer = None

    def setUp(self):
        super().setUp()

        self.customer = self.create_partner("Mario Rossi")

    # ⇒ "Ordine singolo: fatturazione completa"
    def test_complete_invoicing_single_so(self):
        #
        #     SO ┐
        #        └ Picking ┐
        #                  └ DdT
        #
        pass

    # ⇒ "Ordine singolo: fatturazione parziale"
    def test_partial_invoicing_single_so(self):
        #
        #     SO ┐
        #        ├─ Picking ┐
        #        │          └ DdT
        #        └ Picking ┐
        #                  └ DdT
        #
        pass

    # ⇒ "Ordini multipli: fatturazione completa"
    def test_complete_invoicing_multiple_so(self):
        #
        #     SO ┐
        #        └ Picking ┐
        #                  ├ DdT
        #        ┌ Picking ┘
        #     SO ┘
        #
        pass

    # ⇒ "Ordini multipli: fatturazione parziale"
    def test_partial_invoicing_multiple_so(self):
        #
        #     SO ┐
        #        └ Picking ┐
        #                  ├ DdT
        #        ┌ Picking ┘
        #     SO ┤
        #        └ Picking ┐
        #                  └ DdT
        #
        pass
