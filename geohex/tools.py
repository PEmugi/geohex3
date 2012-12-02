import sys
import os
import argparse

from .core import *
try:
    from osgeo import ogr
    from osgeo import osr
except:
    print("ERROR: please install gdal module")
    sys.exit(1)



def gen_hex():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--extent", nargs=4, type=float, default=None, help="extent (degrees)", metavar=("minx", "miny", "maxx", "maxy"))
    parser.add_argument("-o", "--output", type=str, required=True)
    parser.add_argument("-l", "--level", type=int, default=0)
    parser.add_argument("-c", "--center", nargs=2, type=float, default=None, metavar=("x", "y"))
    parser.add_argument("-d", "--distance", type=int, default=0)
    parser.add_argument("-of", "--outputformat", type=str, default="ESRI Shapefile")
    parser.add_argument("-u", "--unit", type=str, default="m", metavar="m|d")
    args = parser.parse_args()

    outputname = args.output
    
    #drv = ogr.GetDriverByName("ESRI Shapefile")
    drv = ogr.GetDriverByName(args.outputformat)

    srs = osr.SpatialReference()
    if args.unit == "m":
        srs.ImportFromProj4("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs")
    else:
        srs.ImportFromEPSG(4326)

    ds = drv.CreateDataSource(outputname)
    lyr = ds.CreateLayer(os.path.basename(outputname).replace(".shp", ""), srs, 3)
    x_no_defn = ogr.FieldDefn()
    x_no_defn.SetName("x")
    x_no_defn.SetType(ogr.OFTInteger)
    lyr.CreateField(x_no_defn)
    y_no_defn = ogr.FieldDefn()
    y_no_defn.SetName("y")
    y_no_defn.SetType(ogr.OFTInteger)
    lyr.CreateField(y_no_defn)
    level_defn = ogr.FieldDefn()
    level_defn.SetName("level")
    level_defn.SetType(ogr.OFTInteger)
    lyr.CreateField(level_defn)
    code_defn = ogr.FieldDefn()
    code_defn.SetName("code")
    code_defn.SetType(ogr.OFTString)
    lyr.CreateField(code_defn)

    if args.extent != None:
        zones = create_zones_by_extent(args.level, *args.extent)
    else:
        center = create_zone(args.level, *args.center)
        zones = [center]
        zones += center.get_movable_zones(args.distance)

    f_defn = ogr.FeatureDefn()
    f_defn.SetGeomType(3)
    f_defn.AddFieldDefn(x_no_defn)
    f_defn.AddFieldDefn(y_no_defn)
    f_defn.AddFieldDefn(level_defn)
    f_defn.AddFieldDefn(code_defn)
    for zone in zones:
        f = ogr.Feature(f_defn)
        if args.unit == "m":
            geom = ogr.CreateGeometryFromWkt(zone.get_wkt())
        else:
            geom = ogr.CreateGeometryFromWkt(zone.get_wkt_deg())
        #geom.AssignSpatialReference(srs)
        f.SetGeometry(geom)
        f.SetField("x", zone.hex_x_no)
        f.SetField("y", zone.hex_y_no)
        f.SetField("level", zone.level)
        f.SetField("code", zone.code)
        lyr.CreateFeature(f)

    ds.Destroy()

