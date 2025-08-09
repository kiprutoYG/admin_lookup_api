# Administrative Lookup & Download API

This project provides a **geospatial lookup and download service** that allows users to:
- Input latitude and longitude to find administrative boundaries.
- Query available administrative levels for a location.
- Download shapefiles (GeoJSON) of specific administrative levels.
- Interact via a **Next.js frontend** with an intuitive, map-like interface.

The API is powered by **FastAPI**, while the frontend is built with **Next.js** for responsiveness across all screen sizes.

---

## Features

- **Coordinate-based lookup** — Find administrative boundaries by latitude & longitude.
- **ADM level query** — Check available administrative levels for a given location.
- **Shapefile download** — Download boundary geometry in GeoJSON format.
- **Responsive UI** — Works across desktop, tablet, and mobile.
- **Help tooltips** — Guides users unfamiliar with geospatial terms like latitude and longitude.
- **East Africa Extents** in tooltip help:
  - **Latitude**: `-11.0` to `6.0`
  - **Longitude**: `29.0` to `42.0`

---

## API Endpoints

### 1. Locate Administrative Boundaries
**`POST /locate`**  
Find the administrative boundary containing a point.

**Request Query Parameters:**
- `latitude` (float) — Required.
- `longitude` (float) — Required.

**Example Request:**
POST /locate?latitude=-1.2921&longitude=36.8219


---

### 2. Available Levels
**`GET /levels`**  
Retrieve available administrative levels for a given point.

**Query Parameters:**
- `latitude` (float) — Required.
- `longitude` (float) — Required.

---

### 3. Download Administrative Boundary
**`GET /download`**  
Download the geometry of the administrative area at the specified level for given coordinates.

**Query Parameters:**
- `latitude` (float) — Required.
- `longitude` (float) — Required.
- `level` (string) — e.g., `adm_1`, `adm_2`, `adm_3`.

**Example Request:**
GET /download?latitude=-1.2921&longitude=36.8219&level=adm_1


---

## Project Structure

---

## Installation & Running Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/kiprutoYG/admin-lookup-api.git
cd your-repo-name
```
### 2. Backend Setup (FastAPI)
```
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Run the backend:
```
uvicorn main:app --reload
```

## License
This project is licensed under the MIT License.
