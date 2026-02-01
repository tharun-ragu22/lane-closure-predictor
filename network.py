# create_network.py
import xml.etree.ElementTree as ET

# Create a simple straight road network
root = ET.Element("net", version="1.0")

# Add location
location = ET.SubElement(root, "location", 
    netOffset="0,0", 
    convBoundary="0,0,200,100", 
    origBoundary="0,0,200,100",
    projParameter="!"  # Required but can be empty
)

# Add junctions
junctions = [
    ("A", "0", "50", "dead_end"),
    ("B", "100", "50", "priority"),
    ("C", "200", "50", "dead_end")
]

for jid, x, y, jtype in junctions:
    ET.SubElement(root, "junction", 
        id=jid, x=x, y=y, type=jtype, 
        incLanes="", intLanes=""
    )

# Add edges (roads)
edges = [
    ("edge1", "A", "B"),
    ("edge2", "B", "C")
]

for eid, from_j, to_j in edges:
    edge = ET.SubElement(root, "edge", id=eid, from=from_j, to=to_j)
    ET.SubElement(edge, "lane", 
        id=f"{eid}_0",
        index="0",
        speed="13.89",
        length="100",
        shape=f"{int(from_j=='A')*100},{50} {int(to_j=='C')*200},{50}"
    )

# Save
tree = ET.ElementTree(root)
tree.write("manual.net.xml", encoding="UTF-8", xml_declaration=True)
print("Created manual.net.xml")

# Create route file
with open("manual.rou.xml", "w") as f:
    f.write("""<?xml version="1.0"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5.0" maxSpeed="13.89"/>
    <route id="route1" edges="edge1 edge2"/>
</routes>""")
print("Created manual.rou.xml")

# Test with SUMO
import subprocess
print("\nTesting SUMO...")
result = subprocess.run([
    "sumo", 
    "--net-file", "manual.net.xml",
    "--route-files", "manual.rou.xml",
    "--duration-log.statistics",
    "--no-warnings"
], capture_output=True, text=True)
print("SUMO output:", result.stdout)
if result.stderr:
    print("Errors:", result.stderr)