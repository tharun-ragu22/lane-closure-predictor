import sumolib

import sumolib.xml

filename = 'hw_401.net.xml'


# Read the network
net = sumolib.net.readNet(filename)

# Get an edge
edgeID = '1174769405'
edge = net.getEdge(edgeID)

# Iterate through lanes to get shapes (geometry)


with open("edge_locations.txt", "w") as file:
    for edge in net.getEdges(withInternal = False):
        file.write(f"edge: {edge.getID()}\n")
        for lane in edge.getLanes():
            # Get shape (list of x,y tuples)
            shape = lane.getShape()
            for x, y in shape:
                # Convert XY to LonLat
                lon, lat = net.convertXY2LonLat(x, y)
                file.write(f"  {lon}, {lat}\n")


    
