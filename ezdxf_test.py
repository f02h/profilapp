import sys
import ezdxf

try:
    doc = ezdxf.readfile("plosca.dxf")
except IOError:
    print(f"Not a DXF file or a generic I/O error.")
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f"Invalid or corrupted DXF file.")
    sys.exit(2)

    # helper function
def print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)
# iterate over all entities in modelspace
msp = doc.modelspace()

holes = []
for e in msp.query("CIRCLE"):
    ocs = e.ocs()
    wcs_center = ocs.to_wcs(e.dxf.center)
    x = wcs_center.x
    y = wcs_center.y
    tmp = []
    tmp.append(round(x,3))
    tmp.append(round(y,3))
    holes.append(tmp)

pieces = []

for e in msp.query("LWPOLYLINE"):
    print(e)
    with e.points("xy") as points:
        #print(points)
        tmp = []
        if points[0][1] > points[3][1]:
            tmp.append(round(points[3][1],3))
            tmp.append(round(points[0][1],3))
            tmp.append(round(points[0][1],3)  - round(points[3][1],3))
        else:
            tmp.append(round(points[0][1],3))
            tmp.append(round(points[3][1],3))
            tmp.append(round(points[3][1],3) - round(points[0][1],3))
            
        pieces.append(tmp)


holePer = [None] * len(pieces)

idx = 0
for p in pieces:
    for h in holes:
        if p[1] > h[1] and p[0] < h[1]:
            holePer[idx].append(h)
    idx += 1


print(pieces)
print(holePer)



    