# Debug script
import subprocess
import xml.etree.ElementTree as ET

# Generate and examine network
subprocess.run(["netgenerate", "--grid", "--grid.number", "1", "--output-file", "debug.net.xml"])

tree = ET.parse("debug.net.xml")
print("Network nodes:")
for junction in tree.findall('.//junction'):
    print(f"  {junction.get('id')}: ({junction.get('x')}, {junction.get('y')})")

print("\nNetwork edges:")
for edge in tree.findall('.//edge'):
    edge_id = edge.get('id')
    if not edge_id.startswith(':'):
        print(f"  {edge_id}: {edge.get('from')} -> {edge.get('to')}")

# Test SUMO directly
print("\nTesting SUMO directly...")
result = subprocess.run([
    "sumo", 
    "--net-file", "debug.net.xml",
    "--duration-log.statistics"
], capture_output=True, text=True)
print(result.stdout)