from fastapi import FastAPI, HTTPException
import os
from cloud_orbit_api.models import item
from cloud_orbit_api.db_factory import SQLiteSingleton
from fastapi.middleware.cors import CORSMiddleware

# Define the FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SQLiteSingleton.get_instance()

@app.get("/")
async def root():
    return {"Hello": "Cloud"}


# Endpoint to create an item
@app.post("/items/")
async def create_item(item: item):
    SQLiteSingleton._instance.cursor.execute(''' INSERT INTO items (name, description) VALUES (?, ?)''', (item.name, item.description))
    SQLiteSingleton._instance.conn.commit()
    return {"name": item.name, "description": item.description}

# Delete item by index
@app.delete("/items/{item_index}")
async def delete_item(item_index: int):
    try:
        # Delete the item from the database
        SQLiteSingleton._instance.cursor.execute('''DELETE FROM items WHERE id = ?''', (item_index,))
        SQLiteSingleton._instance.conn.commit()
        return {"message": f"Item at index {item_index} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to retrieve an item by ID
@app.get("/items/all")
async def read_all_items():
    SQLiteSingleton._instance.cursor.execute('''SELECT id, name, description FROM items''')
    items = SQLiteSingleton._instance.cursor.fetchall()
    for item in items:
        print(item)
    return items

# Endpoint to retrieve an item by ID
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    SQLiteSingleton._instance.cursor.execute('''
        SELECT id, name, description FROM items WHERE id=?
    ''', (item_id,))
    item = SQLiteSingleton._instance.cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item[0], "name": item[1], "description": item[2]}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
