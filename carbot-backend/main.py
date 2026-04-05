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
            INSERT INTO users (telegram_id, name)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (user.telegram_id, user.name)
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
