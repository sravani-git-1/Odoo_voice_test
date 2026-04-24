from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from odoo_service import OdooService

app = FastAPI()
odoo = OdooService()


# ---------- UNIFIED MODEL ----------
class PartnerRequest(BaseModel):
    action: str                 # create / read / update / delete
    type: Optional[str] = None  # customer / vendor
    data: Optional[Dict] = {}
    filters: Optional[Dict] = {}
    update_fields: Optional[Dict] = {}
    confirm: Optional[bool] = False


# ---------- SINGLE API ----------
@app.post("/partner")
def handle_partner(request: PartnerRequest):
    try:
        action = request.action.lower()
        partner_type = request.type.lower() if request.type else None

        # ---------- CREATE ----------
        if action == "create":
            pid = odoo.create_partner_dynamic(partner_type, request.data)
            return {
                "status": "success",
                "message": f"{partner_type} created",
                "id": pid
            }

        # ---------- READ ----------
        elif action == "read":
            result = odoo.get_partner_dynamic(partner_type, request.filters)

            if not result:
                return {
                    "status": "success",
                    "message": f"No {partner_type}s found",
                    "data": []
                }

            return {
                "status": "success",
                "count": len(result),
                "data": result
            }

        # ---------- UPDATE ----------
        elif action == "update":
            res = odoo.update_partner_dynamic(
                request.filters,
                request.update_fields
            )

            return {
                "status": "success",
                "message": "Updated successfully",
                "result": res
            }

        # ---------- DELETE ----------
        elif action == "delete":
            if not request.confirm:
                return {
                    "status": "warning",
                    "message": "Delete not confirmed"
                }

            res = odoo.delete_partner_dynamic(request.filters)

            return {
                "status": "success",
                "message": "Deleted successfully",
                "result": res
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))