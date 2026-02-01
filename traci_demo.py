import os
import sys
sys.path.append(os.path.join('C:',os.sep,'Program Files (x86)',os.sep,'Eclipse',os.sep,'Sumo',os.sep,'tools'))
import traci

def run_simulation(edge_id: int | None = None) -> str:

    sumoBinary = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
    output_file_name = f"stats{f"_{edge_id}" if edge_id is not None else "_no_blocks"}.xml"
    sumoCmd = [sumoBinary, "-c", 
            "hw_401.sumocfg", 
            "--start", 
            "--ignore-route-errors", "true",
            "--statistic-output", output_file_name]




    traci.start(sumoCmd)
    if edge_id is not None:
        traci.edge.setDisallowed(str(edge_id), ["passenger"])

    step = 0
    while step < 10000:
        traci.simulationStep()
        
        curr_time = traci.simulation.getTime()
        # print(curr_time)
        if curr_time > 3600 and edge_id is not None:
            traci.edge.setAllowed(str(edge_id), ["passenger"])
        step += 1

    traci.close()

    return output_file_name