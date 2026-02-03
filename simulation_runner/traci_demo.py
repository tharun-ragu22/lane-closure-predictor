import os
import sys
# sys.path.append(os.path.join('C:',os.sep,'Program Files (x86)',os.sep,'Eclipse',os.sep,'Sumo',os.sep,'tools'))
import traci
import subprocess

def run_simulation(edge_id: int | None = None) -> str:

    sumoBinary = "sumo"
    output_file_name = f"stats{f"_{edge_id}" if edge_id is not None else "_no_blocks"}.xml"
    sumoCmd = [sumoBinary, "-c", 
            "hw_401.sumocfg", 
            "--start", 
            "--ignore-route-errors", "true",
            "--statistic-output", output_file_name]




    try:
        traci.start(sumoCmd)
    except traci.FatalTraCIError:
        # If it crashes, manually run the command to see the hidden error message
        result = subprocess.run(sumoCmd, capture_output=True, text=True)
        print("SUMO STDERR:", result.stderr)
        print("SUMO STDOUT:", result.stdout)
        raise
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