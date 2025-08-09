# Administrative Boundary Lookup API & Frontend

This project provides an API and web-based interface to look up administrative boundaries based on geographic coordinates (latitude & longitude).  
It supports downloading shapefiles or GeoJSONs of administrative areas at different levels (e.g., ADM1, ADM3).  
The project also includes a Next.js frontend for easy interaction and visualization.
* Explore at: https://admin-lookup-api.vercel.app/


<img width="771" height="374" alt="image" src="https://github.com/user-attachments/assets/65488f74-b525-446f-82d5-90796b47356f" />

---

## 📂 Folder Structure
```
.
├── .devcontainer/ # Development container configuration
├── pycache/ # Python cache files
├── adminlookup/ # Next.js frontend (UI)
├── data/ # Geospatial datasets
├── downloads/ # Generated shapefiles & GeoJSONs
├── streamlit_dashboard/ # Old dashboard (no longer in main use)
├── .dockerignore # Docker ignore rules
├── .gitignore # Git ignore rules
├── Dockerfile # Docker build configuration
├── README.md # Project documentation
├── main.py # FastAPI backend entrypoint
├── requirements.txt # Python dependencies
```

---

## 🚀 Features

- Lookup administrative boundaries by latitude & longitude
- Select boundary level (`adm_1`, `adm_2`, `adm_3`, etc.)
- Download results as GeoJSON
- Next.js frontend with tooltips for guidance
- East Africa bounds pre-filled in tooltip for users unfamiliar with coordinates

---

## 🌍 East Africa Bounding Box (Tooltip Reference)

| Coordinate | Value |
|------------|-------|
| **Min Latitude** | -12.0 |
| **Max Latitude** | 5.0 |
| **Min Longitude** | 29.0 |
| **Max Longitude** | 42.0 |

---

## 📌 API Endpoints

### **1. Health Check**
GET /
- Returns: `"API is running"`

---

### **2. Locate Administrative Area**
POST /locate
- Returns administrative area details as JSON.
  
**Body Parameters:**
```json
{
  "latitude": -1.286389,
  "longitude": 36.817223
}
```
### **3. Download Administrative Boundary**
GET /download
- Returns: GeoJSON file download.

**Query Parameters:**
```
latitude (float, required)
longitude (float, required)
level (string, required) — e.g., adm_1, adm_3
```
Example Request:
/download?latitude=-1.286389&longitude=36.817223&level=adm_1

## 🛠 Running the Project
### **1. Clone the Repository**
```
git clone https://github.com/kiprutoYG/admin-lookup-api.git
cd admin-lookup-api
```

### **2. Backend (FastAPI)**
Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Run the API:
```
uvicorn main:app --reload
```
API will be available at:
http://127.0.0.1:8000

### **3. Frontend (Next.js)**
Navigate to frontend folder:
```bash
cd adminlookup
```
Install dependencies:
```
npm install
```
Run the Next.js app:
```
npm run dev
```
Frontend will be available at:
```
(http://localhost:3000)
```

## 🐳 Running with Docker
Build the Docker image:
```
docker build -t admin-lookup-api .
```

Run the container:
```
docker run -p 8000:8000 admin-lookup-api
```
## 📜 License
This project is licensed under the MIT License — you are free to use, modify, and distribute it, provided the license notice is included in copies.




