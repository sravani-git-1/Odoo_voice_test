from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from odoo_service import OdooService

app = FastAPI()
odoo = OdooService()


class PartnerRequest(BaseModel):
    action: str
    type: Optional[str] = None
    data: Optional[Dict] = {}
    filters: Optional[Dict] = {}
    update_fields: Optional[Dict] = {}
    confirm: Optional[bool] = False


@app.post("/partner")
def handle_partner(request: PartnerRequest):
    try:
        action = request.action.lower()
        partner_type = request.type.lower() if request.type else None

        # ---------- CREATE ----------
        if action == "create":
            if not request.data:
                raise HTTPException(status_code=400, detail="Missing data")

            if "name" not in request.data:
                raise HTTPException(status_code=400, detail="Field 'name' is required")

            pid = odoo.create_partner_dynamic(partner_type, request.data)

            if not pid:
                return {
                    "status": "error",
                    "message": "Create failed"
                }

            return {
                "status": "success",
                "message": f"{partner_type} created successfully",
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
            if not request.filters or not request.update_fields:
                raise HTTPException(status_code=400, detail="Missing filters or update_fields")

            res = odoo.update_partner_dynamic(
                partner_type,
                request.filters,
                request.update_fields
            )

            if not res:
                return {
                    "status": "error",
                    "message": "Update failed or record not found"
                }

            return {
                "status": "success",
                "message": "Updated successfully"
            }

        # ---------- DELETE ----------
        elif action == "delete":
            if not request.confirm:
                return {
                    "status": "warning",
                    "message": "Delete not confirmed"
                }

            if not request.filters:
                raise HTTPException(status_code=400, detail="Missing filters")

            res = odoo.delete_partner_dynamic(
                partner_type,
                request.filters
            )

            if not res:
                return {
                    "status": "error",
                    "message": "Delete failed or record not found"
                }

            return {
                "status": "success",
                "message": "Deleted successfully"
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))