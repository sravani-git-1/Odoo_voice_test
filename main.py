from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from odoo_service import OdooService

app = FastAPI()
odoo = OdooService()


# ---------- EXISTING MODELS ----------
class PartnerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    type: str  # customer / vendor


class PartnerUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    phone: Optional[str] = None


# ---------- EXISTING APIs ----------
@app.post("/partner/create")
def create_partner(data: PartnerCreate):
    is_vendor = data.type.lower() == "vendor"
    pid = odoo.create_partner(data.name, data.phone, is_vendor)
    return {"message": f"Created with ID {pid}"}


@app.get("/partner/read")
def read_partner(type: str):
    is_vendor = type.lower() == "vendor"
    return odoo.get_partners(is_vendor)


@app.put("/partner/update")
def update_partner(data: PartnerUpdate):
    odoo.update_partner(data.id, data.name, data.phone)
    return {"message": "Updated"}


@app.delete("/partner/delete/{partner_id}")
def delete_partner(partner_id: int):
    odoo.delete_partner(partner_id)
    return {"message": "Deleted"}


# ---------- AI AGENT MODEL ----------
class AgentRequest(BaseModel):
    action: str
    type: Optional[str] = None
    data: Optional[Dict] = {}
    filters: Optional[Dict] = {}
    update_fields: Optional[Dict] = {}
    confirm: Optional[bool] = False


# ---------- AI AGENT ENDPOINT ----------
@app.post("/agent")
def handle_agent(request: AgentRequest):
    try:
        action = request.action.lower()

        if action == "create":
            return odoo.create_partner_dynamic(request.type, request.data)

        elif action == "read":
            return odoo.get_partner_dynamic(request.type, request.filters)

        elif action == "update":
            return odoo.update_partner_dynamic(
                request.filters,
                request.update_fields
            )

        elif action == "delete":
            if not request.confirm:
                return {"message": "Delete not confirmed"}

            return odoo.delete_partner_dynamic(request.filters)

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))