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

    # ---------- READ ----------
    def get_partner_dynamic(self, partner_type, filters):
        domain = []

        if partner_type == "customer":
            domain.append(["customer_rank", ">", 0])
        elif partner_type == "vendor":
            domain.append(["supplier_rank", ">", 0])

        for k, v in filters.items():
            domain.append([k, "=", v])

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search_read",
            [domain],
            {"fields": ["id", "name", "phone", "email", "mobile", "city"], "limit": 10}
        )

    # ---------- UPDATE ----------
    def update_partner_dynamic(self, partner_type, filters, update_fields):
        domain = []

        if partner_type == "customer":
            domain.append(["customer_rank", ">", 0])
        elif partner_type == "vendor":
            domain.append(["supplier_rank", ">", 0])

        for k, v in filters.items():
            domain.append([k, "=", v])

        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [domain]
        )

        if not ids:
            return False

        result = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "write",
            [ids, update_fields]   # IMPORTANT: ids must be list
        )

        return result  # True / False

    # ---------- DELETE ----------
    def delete_partner_dynamic(self, partner_type, filters):
        domain = []

        if partner_type == "customer":
            domain.append(["customer_rank", ">", 0])
        elif partner_type == "vendor":
            domain.append(["supplier_rank", ">", 0])

        for k, v in filters.items():
            domain.append([k, "=", v])

        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [domain]
        )

        if not ids:
            return False

        result = self.models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "unlink",
            [ids]
        )

        return result  # True / False