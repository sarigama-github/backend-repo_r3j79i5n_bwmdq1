import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Contact, EmailLog

app = FastAPI(title="ZX2APT.EXE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "akashdigitalhub12@gmail.com")

@app.get("/")
def root():
    return {"message": "ZX2APT.EXE backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:120]}"
        else:
            response["database"] = "❌ db is None"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response

@app.post("/contact")
async def create_contact(contact: Contact):
    try:
        # Save contact submission
        contact_id = create_document("contact", contact)
        
        # Log an email attempt (DB-only mode)
        subject = f"New Contact: {contact.name}"
        email_log = EmailLog(
            to=CONTACT_EMAIL,
            subject=subject,
            status="attempted",
            error="DB-only mode: email not sent"
        )
        _ = create_document("emaillog", email_log)

        return {"ok": True, "message": "Thanks! Your message was received.", "id": contact_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts", response_model=List[dict])
async def list_contacts():
    try:
        docs = get_documents("contact", limit=50)
        # Convert ObjectId to str for JSON serialization
        def normalize(doc):
            doc["_id"] = str(doc["_id"]) if "_id" in doc else None
            return doc
        return [normalize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
