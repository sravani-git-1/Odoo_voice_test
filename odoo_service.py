import xmlrpc.client

class OdooService:
    def __init__(self):
        self.url = "https://odoo.avowaldatasystems.in/"
        self.db = "odooKmmDb"
        self.username = "rajugenai@gmail.com"
        self.password = "P@$$W0rd&$@"

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})

        if not self.uid:
            raise Exception("Odoo Authentication Failed")

        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    # CREATE
    def create_partner(self, name, phone=None, is_vendor=False):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            'res.partner', 'create',
            [{
                'name': name,
                'phone': phone,
                'supplier_rank': 1 if is_vendor else 0
            }]
        )

    # READ
    def get_partners(self, is_vendor=False):
        domain = [['supplier_rank', '>', 0]] if is_vendor else [['supplier_rank', '=', 0]]

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            'res.partner', 'search_read',
            [domain],
            {'fields': ['name', 'phone', 'mobile', 'email', 'city', 'zip'], 'limit': 10}
        )

    # UPDATE
    def update_partner(self, partner_id, name=None, phone=None):
        vals = {}
        if name:
            vals['name'] = name
        if phone:
            vals['phone'] = phone

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            'res.partner', 'write',
            [[partner_id], vals]
        )

    # DELETE
    def delete_partner(self, partner_id):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            'res.partner', 'unlink',
            [[partner_id]]
        )