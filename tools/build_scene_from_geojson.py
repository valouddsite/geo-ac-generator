# Script de départ Blender : rubans de route et bâtiments extrudés.
# Prototype de visualisation, PAS un export KN5 ni une piste prête à jouer.
import bpy, json, math, os
from mathutils import Vector
GEOJSON_PATH = r"C:\CHANGE_ME\export.geojson"
ROAD_WIDTH_M = 7.0
DEFAULT_HOUSE_HEIGHT_M = 6.5

def material(name, color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m

def xy(lon,lat,lon0,lat0):
    return ((lon-lon0)*111320*math.cos(math.radians(lat0)),(lat-lat0)*110540)

def mesh_obj(name, verts, faces, mat):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    return ob

def make_road(coords, origin, width, mat):
    pts=[Vector((*xy(c[0],c[1],*origin),0.12)) for c in coords]
    if len(pts)<2: return
    verts=[]
    for i,p in enumerate(pts):
        d=(pts[1]-p).normalized() if i==0 else ((p-pts[i-1]).normalized() if i==len(pts)-1 else (pts[i+1]-pts[i-1]).normalized())
        side=Vector((-d.y,d.x,0))*width/2
        verts.extend([tuple(p-side),tuple(p+side)])
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)]
    mesh_obj("Road",verts,faces,mat)

def make_building(ring, origin, height, mat):
    pts=[xy(c[0],c[1],*origin) for c in ring[:-1]]
    if len(pts)<3: return
    n=len(pts); verts=[(x,y,0) for x,y in pts]+[(x,y,height) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    mesh_obj("Building_OSM_or_estimated",verts,faces,mat)

def main():
    if not os.path.isfile(GEOJSON_PATH): raise FileNotFoundError("Modifie GEOJSON_PATH dans le script.")
    with open(GEOJSON_PATH,encoding="utf-8") as f: data=json.load(f)
    coords=[]
    for feature in data.get("features",[]):
        g=feature.get("geometry") or {}; c=g.get("coordinates")
        if g.get("type")=="LineString": coords.extend(c)
        elif g.get("type")=="Polygon" and c: coords.extend(c[0])
    if not coords: raise ValueError("Aucune géométrie exploitable.")
    lon0=sum(c[0] for c in coords)/len(coords); lat0=sum(c[1] for c in coords)/len(coords)
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    asphalt=material("Asphalt",(0.07,0.075,0.08)); wall=material("Building",(0.55,0.52,0.46)); ground=material("TemporaryGround",(0.18,0.23,0.16))
    local=[xy(c[0],c[1],lon0,lat0) for c in coords]; xs=[p[0] for p in local]; ys=[p[1] for p in local]; margin=30
    mesh_obj("TEMP_flat_ground",[(min(xs)-margin,min(ys)-margin,-0.2),(max(xs)+margin,min(ys)-margin,-0.2),(max(xs)+margin,max(ys)+margin,-0.2),(min(xs)-margin,max(ys)+margin,-0.2)],[(0,1,2,3)],ground)
    for feature in data.get("features",[]):
        g=feature.get("geometry") or {}; p=feature.get("properties") or {}; c=g.get("coordinates")
        if g.get("type")=="LineString" and "highway" in p: make_road(c,(lon0,lat0),ROAD_WIDTH_M,asphalt)
        elif g.get("type")=="Polygon" and "building" in p:
            try: h=float(str(p.get("height","")).replace(" m",""))
            except: h=float(p.get("estimated_height_m") or DEFAULT_HOUSE_HEIGHT_M)
            if not 1<=h<=300: h=float(p.get("estimated_height_m") or DEFAULT_HOUSE_HEIGHT_M)
            make_building(c[0],(lon0,lat0),h,wall)
    bpy.context.scene.unit_settings.system='METRIC'
    print("Scène prototype créée. Ajouter un DEM réel, traiter les polygones complexes et finaliser le pipeline AC.")

main()
