import libsumo as traci
import subprocess
import sys

# Generate a 1x2 grid (simpler)
subprocess.run([
    sys.executable.replace("python.exe", "netgenerate.exe"),
    "--grid",
    "--grid.number", "1",  # 1x2 grid = 2 nodes in a line
    "--grid.length", "100",
    "--output-file", "simple.net.xml"
])

# Use the simplest possible route
route_xml = """<?xml version="1.0"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5.0" maxSpeed="13.89"/>
    <!-- In a 1x2 grid, edge should be A0A1 -->
    <route id="route0" edges="A0A1"/>
</routes>"""

with open("simple.rou.xml", "w") as f:
    f.write(route_xml)

print("Starting SUMO with 1x2 grid...")

try:
    traci.start([
        "sumo",
        "--net-file", "simple.net.xml",
        "--route-files", "simple.rou.xml",
        "--no-step-log",
        "--no-warnings",
        "--begin", "0",
        "--end", "100"
    ])
    
    print("SUMO started!")
    
    # Try adding vehicle with try/except
    try:
        traci.vehicle.add("veh0", "route0", depart="0")
        print("Vehicle added successfully")
    except Exception as e:
        print(f"Couldn't add vehicle: {e}")
        # List available routes
        print("Available routes:", traci.route.getIDList())
        # Try creating route dynamically
        edges = traci.edge.getIDList()
        print(f"Available edges: {edges}")
        if edges:
            traci.route.add("dynamic_route", [edges[0]])
            traci.vehicle.add("veh1", "dynamic_route", depart="now")
            print("Added vehicle with dynamic route")
    
    # Run simulation
    for step in range(50):
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()
        if vehicles:
            if step % 10 == 0:
                print(f"Step {step}: {len(vehicles)} vehicles moving")
                for vid in vehicles:
                    pos = traci.vehicle.getPosition(vid)
                    print(f"  {vid} at ({pos[0]:.1f}, {pos[1]:.1f})")
        elif step % 20 == 0:
            print(f"Step {step}: No vehicles yet")
    
    traci.close()
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")