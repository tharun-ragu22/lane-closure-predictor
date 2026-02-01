import math

def get_closest_edge(target_lat, target_lon, file_path) -> int:
    closest_edge = None
    min_dist = float('inf')
    
    current_edge = None
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('edge:'):
                current_edge = line.split(':')[1].strip()
            elif ',' in line:
                try:
                    # File format: longitude, latitude
                    parts = line.split(',')
                    lon = float(parts[0].strip())
                    lat = float(parts[1].strip())
                    
                    # Euclidean distance (sufficient for finding the closest point in a local area)
                    dist = math.sqrt((lat - target_lat)**2 + (lon - target_lon)**2)
                    
                    if dist < min_dist:
                        min_dist = dist
                        closest_edge = current_edge
                except ValueError:
                    continue
    return closest_edge

# target_lat = 43.7913809
# target_lon = -79.207621
# edge = get_closest_edge(target_lat, target_lon, 'edge_locations.txt')
# print(f"Closest edge: {edge}")