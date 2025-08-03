from fastapi import APIRouter, HTTPException
from auth_db import get_db_connection

router = APIRouter()

@router.post("/save-user")
async def save_user(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE uid = %s", (current_user['uid'],))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (email, uid, display_name) VALUES (%s, %s, %s)",
            (current_user['email'], current_user['uid'], current_user['display_name'])
        )
        conn.commit()
    cur.close()
    conn.close()
    return {"success": True} 