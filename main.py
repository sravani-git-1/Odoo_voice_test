from fastapi import FastAPI
from pydantic import BaseModel
from odoo_service import OdooService

app = FastAPI()
odoo = OdooService()

class PartnerCreate(BaseModel):
    name: str
    phone: str | None = None
    type: str  # customer / vendor

class PartnerUpdate(BaseModel):
    id: int
    name: str | None = None
    phone: str | None = None

@app.post("/partner/create")
def create_partner(data: PartnerCreate):
    is_vendor = data.type == "vendor"
    pid = odoo.create_partner(data.name, data.phone, is_vendor)
    return {"message": f"Created with ID {pid}"}

@app.get("/partner/read")
def read_partner(type: str):
    is_vendor = type == "vendor"
    return odoo.get_partners(is_vendor)

@app.put("/partner/update")
def update_partner(data: PartnerUpdate):
    odoo.update_partner(data.id, data.name, data.phone)
    return {"message": "Updated"}

@app.delete("/partner/delete/{partner_id}")
def delete_partner(partner_id: int):
    odoo.delete_partner(partner_id)
    return {"message": "Deleted"}