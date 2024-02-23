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

pieces = []

# iterate over all entities in modelspace
msp = doc.modelspace()
idx = 0
for e in msp.query("LWPOLYLINE"):
    print(e)
    with e.points("xyseb") as points:
        #print(points)
        tmp = []
        tmp.append(points[0][1])
        tmp.append(points[0][3])

        pieces.append(tmp)
        
print(pieces)