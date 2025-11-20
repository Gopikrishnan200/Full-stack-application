from fastapi import FastAPI, Depends, HTTPException, Form,Header
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from db.database import get_db

app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ------------------ PASSWORD TOOLS ------------------
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# ------------------ JWT TOKENS ------------------
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ------------------ REGISTER ------------------
@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cur = conn.cursor(dictionary=True)
    hashed_pw = hash_password(password)

    # MySQL uses %s placeholders
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed_pw)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User registered successfully!"}

# ------------------ LOGIN ------------------
@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = create_token({"user_id": user["id"]})
    return {"access_token": token, "token_type": "bearer"}



# ------------------ FORGOT PASSWORD ------------------
@app.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Create reset token (valid for resetting password)
    reset_token = create_token({"user_id": user["id"], "action": "reset_password"})

    cur.close()
    conn.close()

    # Normally you send this via email, but now returning for testing
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token
    }


# ------------------ RESET PASSWORD ------------------
@app.post("/reset-password")
def reset_password(
    token: str = Header(...),
    new_password: str = Form(...)
):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("action") != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        user_id = data.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    cur = conn.cursor()

    hashed_pw = hash_password(new_password)

    cur.execute(
        "UPDATE users SET password = %s WHERE id = %s",
        (hashed_pw, user_id)
    )
    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Password updated successfully!"}

# ------------------ PROTECTED ROUTE ------------------
@app.get("/profile")
def profile(token: str = Depends(oauth2_scheme)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = data.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"message": f"Welcome! Your user id is {user_id}"}

# Import task routes
from task import register_task_routes
register_task_routes(app)
