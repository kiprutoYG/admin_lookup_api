#prerequisites: fastapi, geopandas, shapely, uvicorn
# This FastAPI application provides an endpoint to check if a point is within a specified polygon.
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from shapely.geometry import Point
import geopandas as gpd
import glob
import re

app = FastAPI(title='East Africa Administration Level API') #initialize FASTAPI app

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
    pattern = f"{base_dir}/gadm41_{country_code}_*.shp"
    matches = glob.glob(pattern)

    highest_level = -1
    highest_file = None

    for filepath in matches:
        level_match = re.search(rf"gadm41_{country_code}_(\d)\.shp", filepath)
        if level_match:
            level = int(level_match.group(1))
            if level > highest_level:
                highest_level = level
                highest_file = filepath

    if highest_file:
        return gpd.read_file(highest_file)
    else:
        raise FileNotFoundError(f"No ADM shapefiles found for {country_code}")

    
    
def get_adm_names(lat: float, lon: float) -> dict:
    """
    Get administrative names for a given latitude and longitude.
    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
    Returns:
        dict: A dictionary containing administrative names at various levels.
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
    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        level (str): Administrative level (e.g., "ADM_0", "ADM_1", etc.).
    Returns:
        gpd.GeoDataFrame: The GeoDataFrame containing the geometry of the administrative area.
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
@app.post("/locate", summary="Get administrative units from coordinates")
def locate_coordinates(coords: Coordinates):
    """
    Endpoint to locate coordinates and return administrative names.
    Args:
        coords (Coordinates): The coordinates to locate.
    Returns:
        dict: A dictionary containing the longitude, latitude, and administrative names.
    """
    names = get_adm_names(coords.latitude, coords.longitude)
    return {
        "Longitude" : coords.longitude,
        "Latitude" : coords.latitude,
        "Administrative Levels": names
    }
    

@app.get("/download",
    summary="Download administrative boundary shapefile",
    description="Provide coordinates and ADM level (e.g., adm_1, adm_3) to download the shapefile where the point falls.")
def download(
    latitude: float = Query(...),
    longitude: float = Query(...),
    level: str = Query(...)
):
    """
    Endpoint to download the geometry of the administrative area at the specified level for given coordinates.
    Args:
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
        level (str): Administrative level (e.g., "ADM_0", "ADM_1", etc.).
    Returns:
        FileResponse: A response containing the GeoJSON file of the administrative area.
    """
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
    Returns:
        JSONResponse: A response indicating that the API is running.
    """
    return JSONResponse(content={"message": "East Africa Administration Level API is running."})