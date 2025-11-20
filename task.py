from fastapi import FastAPI, Depends, HTTPException, Form, Header
from jose import jwt, JWTError
from db.database import get_db

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"



# ------------------ GET CURRENT USER ------------------
def get_current_user(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data.get("user_id")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------ TASK ROUTES ------------------
def register_task_routes(app: FastAPI):

    @app.post("/task/add")
    def add_task(
        token: str = Header(...),
        name: str = Form(...),
        des: str = Form(...),
        size: str = Form(...),
        status: str = Form(...)
    ):
        user_id = get_current_user(token)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO task (user_id, name, des, size, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, des, size, status))

        conn.commit()
        conn.close()

        return {"message": "Task added successfully!"}

    @app.get("/task/list")
    def list_tasks(
        token: str = Header(...),
        limit: int = 10,
        skip: int = 0,
        sort_by: str = "id",
        order: str = "asc"
    ):
        user_id = get_current_user(token)

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        # Allowed columns (to prevent SQL injection)
        allowed_sort = ["id", "name", "size", "status"]
        if sort_by not in allowed_sort:
            sort_by = "id"

        # Allowed order types
        allowed_order = ["asc", "desc"]
        if order.lower() not in allowed_order:
            order = "asc"

        query = f"""
            SELECT * FROM task 
            WHERE user_id = %s
            ORDER BY {sort_by} {order}
            LIMIT %s OFFSET %s
        """

        cur.execute(query, (user_id, limit, skip))
        tasks = cur.fetchall()
        conn.close()

        return {"tasks": tasks}


