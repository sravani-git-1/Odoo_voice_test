import xmlrpc.client


class OdooService:
    def __init__(self):
        self.url = "https://odoo.avowaldatasystems.in"
        self.db = "odooKmmDb"
        self.username = "rajugenai@gmail.com"
        self.password = "P@$$W0rd&$@"

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(
            self.db, self.username, self.password, {}
        )

        if not self.uid:
            raise Exception("Odoo Authentication Failed")

        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    # ---------- CREATE ----------
    def create_partner(self, name, phone=None, is_vendor=False):
        data = {
            "name": name,
            "phone": phone
        }

        if is_vendor:
            data["supplier_rank"] = 1
        else:
            data["customer_rank"] = 1

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "create",
            [data]
        )

    # ---------- READ ----------
    def get_partners(self, is_vendor=False):
        domain = [["supplier_rank", ">", 0]] if is_vendor else [["customer_rank", ">", 0]]

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search_read",
            [domain],
            {"fields": ["name", "phone", "email", "mobile", "city", "zip"], "limit": 10}
        )

    # ---------- UPDATE ----------
    def update_partner(self, partner_id, name=None, phone=None):
        vals = {}

        if name:
            vals["name"] = name
        if phone:
            vals["phone"] = phone

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "write",
            [[partner_id], vals]
        )

    # ---------- DELETE ----------
    def delete_partner(self, partner_id):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "unlink",
            [[partner_id]]
        )

    # ================= AI METHODS =================

    # CREATE (Dynamic)
    def create_partner_dynamic(self, partner_type, data):
        if partner_type == "customer":
            data["customer_rank"] = 1
        elif partner_type == "vendor":
            data["supplier_rank"] = 1

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "create",
            [data]
        )

    # READ (Dynamic)
    def get_partner_dynamic(self, partner_type, filters):
        domain = []

        if partner_type == "customer":
            domain.append(["customer_rank", ">", 0])
        elif partner_type == "vendor":
            domain.append(["supplier_rank", ">", 0])

        for key, value in filters.items():
            domain.append([key, "=", value])

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search_read",
            [domain],
            {"fields": ["name", "phone", "email"], "limit": 10}
        )

    # UPDATE (Dynamic)
    def update_partner_dynamic(self, filters, update_fields):
        domain = [[k, "=", v] for k, v in filters.items()]

        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [domain]
        )

        if not ids:
            return {"message": "No record found"}

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "write",
            [ids, update_fields]
        )

    # DELETE (Dynamic)
    def delete_partner_dynamic(self, filters):
        domain = [[k, "=", v] for k, v in filters.items()]

        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [domain]
        )

        if not ids:
            return {"message": "No record found"}

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "unlink",
            [ids]
        )