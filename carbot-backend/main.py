from fastapi import FastAPI, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from db import get_connection
from PIL import Image
import io
import base64

app = FastAPI()

# =====================
# MODELS
# =====================

class UserCreate(BaseModel):
    telegram_id: int
    name: str = ""
    telegram_username: str = ""

class UserUpdate(BaseModel):
    telegram_id: int
    name: str

class CarCreate(BaseModel):
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    price: int = Field(..., gt=0)
    mileage: int = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    user_id: int

class CarUpdate(BaseModel):
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    price: int = Field(..., gt=0)
    mileage: int = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    telegram_id: int

# =====================
# USERS
# =====================

@app.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT id FROM users WHERE telegram_id=%s",
            (user.telegram_id,)
        )
        existing = cur.fetchone()

        if existing:
            return {"id": existing[0]}

        cur.execute(
            """
            INSERT INTO users (telegram_id, name, telegram_username)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (user.telegram_id, user.name, user.telegram_username)
        )

        user_id = cur.fetchone()[0]
        conn.commit()

        return {"id": user_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.put("/users")
def update_user(user: UserUpdate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE users
            SET name=%s
            WHERE telegram_id=%s
            """,
            (user.name, user.telegram_id)
        )

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        conn.commit()
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


# =====================
# CARS
# =====================

@app.post("/cars")
def add_car(car: CarCreate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO cars (make, model, year, price, mileage, description, latitude, longitude, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                car.make,
                car.model,
                car.year,
                car.price,
                car.mileage,
                car.description,
                car.latitude,
                car.longitude,
                car.user_id
            )
        )

        new_id = cur.fetchone()[0]
        conn.commit()

        return {"id": new_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/cars")
def get_cars(limit: int = 100, offset: int = 0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM cars LIMIT %s OFFSET %s;", (limit, offset))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Return structured JSON instead of raw tuples
    return [
        {
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "price": row[4],
            "mileage": row[5],
            "description": row[6],
            "created_at": str(row[7]),
            "latitude": row[8],
            "longitude": row[9],
            "user_id": row[10]
        }
        for row in rows
    ]


@app.get("/cars/search")
def search(q: str, limit: int = 100, offset: int = 0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM cars
        WHERE make ILIKE %s OR model ILIKE %s
        LIMIT %s OFFSET %s;
        """,
        (f"%{q}%", f"%{q}%", limit, offset)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Return structured JSON
    return [
        {
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "price": row[4],
            "mileage": row[5],
            "description": row[6],
            "created_at": str(row[7]),
            "latitude": row[8],
            "longitude": row[9],
            "user_id": row[10]
        }
        for row in rows
    ]


@app.get("/cars/brands")
def get_brands():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT make FROM cars;")
    brands = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return brands


@app.get("/cars/user/{telegram_id}")
def get_user_cars(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT cars.*
        FROM cars
        JOIN users ON cars.user_id = users.id
        WHERE users.telegram_id = %s
        """,
        (telegram_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "price": row[4],
            "mileage": row[5],
            "description": row[6],
            "created_at": str(row[7]),
            "latitude": row[8],
            "longitude": row[9],
            "user_id": row[10]
        }
        for row in rows
    ]


@app.delete("/cars/{car_id}")
def delete_car(car_id: int, telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Verify ownership
        cur.execute(
            """
            SELECT cars.id FROM cars
            JOIN users ON cars.user_id = users.id
            WHERE cars.id = %s AND users.telegram_id = %s
            """,
            (car_id, telegram_id)
        )

        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Not authorized or car not found")

        cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        conn.commit()

        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.put("/cars/{car_id}")
def update_car(car_id: int, car: CarUpdate):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Verify ownership
        cur.execute(
            """
            SELECT cars.id FROM cars
            JOIN users ON cars.user_id = users.id
            WHERE cars.id = %s AND users.telegram_id = %s
            """,
            (car_id, car.telegram_id)
        )

        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Not authorized or car not found")

        cur.execute(
            """
            UPDATE cars
            SET make=%s, model=%s, year=%s, price=%s, mileage=%s,
                description=%s, latitude=%s, longitude=%s
            WHERE id = %s
            """,
            (
                car.make,
                car.model,
                car.year,
                car.price,
                car.mileage,
                car.description,
                car.latitude,
                car.longitude,
                car_id
            )
        )

        conn.commit()
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

# =====================
# CAR IMAGES
# =====================

@app.post("/cars/{car_id}/images")
async def upload_car_image(car_id: int, telegram_id: int, file: UploadFile = File(...)):
    """Upload an image for a car listing"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Verify ownership
        cur.execute(
            """
            SELECT cars.id FROM cars
            JOIN users ON cars.user_id = users.id
            WHERE cars.id = %s AND users.telegram_id = %s
            """,
            (car_id, telegram_id)
        )

        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Not authorized or car not found")

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and compress image
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Resize if too large (max 1024x1024)
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to JPEG and compress
        output = io.BytesIO()
        img.convert("RGB").save(output, format="JPEG", quality=85, optimize=True)
        compressed_data = output.getvalue()

        # Check image count (max 5 per car)
        cur.execute("SELECT COUNT(*) FROM car_images WHERE car_id = %s", (car_id,))
        count = cur.fetchone()[0]
        
        if count >= 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images per car")

        # Insert image
        cur.execute(
            """
            INSERT INTO car_images (car_id, image_data, image_order)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (car_id, compressed_data, count)
        )

        image_id = cur.fetchone()[0]
        conn.commit()

        return {"id": image_id, "order": count}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/cars/{car_id}/images")
def get_car_images(car_id: int):
    """Get all images for a car"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, image_data, image_order
            FROM car_images
            WHERE car_id = %s
            ORDER BY image_order
            """,
            (car_id,)
        )

        images = []
        for row in cur.fetchall():
            images.append({
                "id": row[0],
                "image_data": base64.b64encode(row[1].tobytes()).decode("utf-8"),
                "order": row[2]
            })

        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.delete("/cars/{car_id}/images/{image_id}")
def delete_car_image(car_id: int, image_id: int, telegram_id: int):
    """Delete a car image"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Verify ownership
        cur.execute(
            """
            SELECT cars.id FROM cars
            JOIN users ON cars.user_id = users.id
            WHERE cars.id = %s AND users.telegram_id = %s
            """,
            (car_id, telegram_id)
        )

        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Not authorized or car not found")

        # Delete image
        cur.execute(
            "DELETE FROM car_images WHERE id = %s AND car_id = %s",
            (image_id, car_id)
        )

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Image not found")

        conn.commit()
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/cars/{car_id}/seller")
def get_seller_info(car_id: int):
    """Get seller information for a car"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT u.telegram_id, u.name, u.telegram_username
            FROM users u
            JOIN cars c ON c.user_id = u.id
            WHERE c.id = %s
            """,
            (car_id,)
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Car or seller not found")

        return {
            "telegram_id": row[0],
            "name": row[1],
            "telegram_username": row[2]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


# =====================
# MESSAGES
# =====================

class MessageCreate(BaseModel):
    car_id: int
    from_telegram_id: int
    to_telegram_id: int
    message_text: str = Field(..., min_length=1, max_length=1000)


@app.post("/messages")
def send_message(message: MessageCreate):
    """Send a message from buyer to seller"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get user IDs from telegram IDs
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_telegram_id,))
        from_user = cur.fetchone()

        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (message.to_telegram_id,))
        to_user = cur.fetchone()

        if not from_user or not to_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Insert message
        cur.execute(
            """
            INSERT INTO messages (car_id, from_user_id, to_user_id, message_text)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (message.car_id, from_user[0], to_user[0], message.message_text)
        )

        message_id = cur.fetchone()[0]
        conn.commit()

        return {"id": message_id, "status": "sent"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/messages/inbox/{telegram_id}")
def get_inbox(telegram_id: int, unread_only: bool = False):
    """Get messages for a user"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get user ID
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = """
            SELECT
                m.id, m.car_id, m.message_text, m.created_at, m.is_read,
                u.name as sender_name, u.telegram_id as sender_telegram_id,
                c.make, c.model
            FROM messages m
            JOIN users u ON m.from_user_id = u.id
            JOIN cars c ON m.car_id = c.id
            WHERE m.to_user_id = %s
        """

        if unread_only:
            query += " AND m.is_read = FALSE"

        query += " ORDER BY m.created_at DESC"

        cur.execute(query, (user[0],))
        rows = cur.fetchall()

        messages = []
        for row in rows:
            messages.append({
                "id": row[0],
                "car_id": row[1],
                "message_text": row[2],
                "created_at": str(row[3]),
                "is_read": row[4],
                "sender_name": row[5],
                "sender_telegram_id": row[6],
                "car_make": row[7],
                "car_model": row[8]
            })

        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.put("/messages/{message_id}/read")
def mark_message_read(message_id: int, telegram_id: int):
    """Mark a message as read"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Verify ownership
        cur.execute(
            """
            SELECT m.id FROM messages m
            JOIN users u ON m.to_user_id = u.id
            WHERE m.id = %s AND u.telegram_id = %s
            """,
            (message_id, telegram_id)
        )

        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("UPDATE messages SET is_read = TRUE WHERE id = %s", (message_id,))
        conn.commit()

        return {"status": "marked_read"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()
