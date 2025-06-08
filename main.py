#prerequisites: fastapi, geopandas, shapely, uvicorn
# This FastAPI application provides an endpoint to check if a point is within a specified polygon.
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from shapely.geometry import Point
import geopandas as gpd
import os
import re

app = FastAPI(title='Kenya Administration Level API') #initialize FASTAPI app

#====Models====
class Coordinates(BaseModel):
    latitude: float
    longitude: float
    
#====Configuration====
EA_GPKG_PATH = 'data/EA_ADM0.gpkg' 
LAYER_MAPPING = {
    "Country": "ADM_0",
    "ADM_1": "ADM_1",
    "ADM_2": "ADM_2",
    "ADM_3": "ADM_3",
    "ADM_4": "ADM_4",
    "ADM_5": "ADM_5"
}


#=====Utility Functions=====
def get_highest_adm_level_gpkg(country_code, base_dir="data/adm_levels"):
    # Match pattern like gadm_41_KEN_ADM3.gpkg
    pattern = re.compile(rf"gadm41_{country_code}_(\d)\.shp")

    highest_adm = -1
    highest_file = None

    for filename in os.listdir(base_dir):
        match = pattern.match(filename)
        if match:
            level = int(match.group(1))
            if level > highest_adm:
                highest_adm = level
                highest_file = os.path.join(base_dir, filename)

    if highest_file:
        print(f"Selected highest ADM level: ADM{highest_adm} for {country_code}")
        return gpd.read_file(highest_file)
    else:
        raise FileNotFoundError(f"No ADM GPKGs found for {country_code}")
    
    
def get_adm_names(lat: float, lon: float) -> dict:
    """
    Get administrative names for a given latitude and longitude.
    """
    point = Point(lon, lat)  # Note: Shapely uses (longitude, latitude)
    names = {}
    
    # Check if the point is within any of the polygons
    try:
        gdf = gpd.read_file(EA_GPKG_PATH)
        gdf = gdf.to_crs("EPSG:4326")  # Ensure CRS is WGS84
        match = gdf[gdf.contains(point)]
        if len(match) > 0:
            gid = match.iloc[0]['GID_0']
            try:
                # Step 2: Load highest ADM level for that country
                gdf = get_highest_adm_level_gpkg(gid)
                # Step 3: Check if the point is within any of the polygons
                match = gdf[gdf.contains(point)]
                names = {}
                if len(match) > 0:
                    # Step 4: Extract the names of the administrative levels
                    row = match.iloc[0]
                    names['Country'] = row['COUNTRY']
                    hierachy = {col: row[col] for col in gdf.columns if col.startswith('NAME_')}
                    names.update(hierachy)
                else:
                    raise HTTPException(status_code=404, detail="No matching polygon found.")
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"No administrative data found.")
        else:
            names = {"error": "No matching polygon found."}
    except Exception as e:
        names = {"error": str(e)}
    return names


def get_geometry_by_point_and_level(lat: float, lon: float, level: str) -> gpd.GeoDataFrame:
    """
    Get the geometry of the administrative area at the specified level for a given latitude and longitude.
    """
    point = Point(lon, lat)
    layer = LAYER_MAPPING.get(level)
    
    gdf = gpd.read_file(EA_GPKG_PATH)
    gdf = gdf.to_crs("EPSG:4326")  # Ensure CRS is WGS84
    country_match = gdf[gdf.contains(point)]
    gid = country_match.iloc[0]['GID_0'] if not country_match.empty else None
    if not gid:
        raise HTTPException(status_code=404, detail="No matching polygon found for the given coordinates.")
    else:
        try:
            #Match the country code to the level entered
            adm_level = int(level.lower().replace("adm_", ""))
            if adm_level < 0 or adm_level > 5:
                raise HTTPException(status_code=400, detail="Invalid administrative level. Must be between ADM_0 and ADM_5.")
            pattern = re.compile(rf"gadm41_{gid}_{adm_level}\.shp")
            for filename in os.listdir("data/adm_levels"):
                if pattern.match(filename):
                    adm_gdf = gpd.read_file(os.path.join("data/adm_levels", filename))
                    adm_gdf = adm_gdf.to_crs("EPSG:4326")
                    match = adm_gdf[adm_gdf.contains(point)]
                    if not match.empty:
                        return match
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")
    return match
    
    
#====API Endpoints====
@app.post("/locate")
def locate_coordinates(coords: Coordinates):
    """
    Endpoint to locate coordinates and return administrative names.
    """
    names = get_adm_names(coords.latitude, coords.longitude)
    return {
        "Longitude" : coords.longitude,
        "Latitude" : coords.latitude,
        "Administrative Levels": names
    }
    

@app.get("/download")
def download(
    latitude: float = Query(...),
    longitude: float = Query(...),
    level: str = Query(...)
):
    try:
        matched = get_geometry_by_point_and_level(latitude, longitude, level)
        outpath = f"downloads/{level}_{latitude}_{longitude}.geojson"
        matched.to_file(outpath, driver="GeoJSON")
        return FileResponse(outpath, filename=os.path.basename(outpath), media_type="application/geo+json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def root():
    """
    Root endpoint to check if the API is running.
    """
    return JSONResponse(content={"message": "Kenya Administration Level API is running."})