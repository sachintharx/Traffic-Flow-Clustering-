import traci
import csv

sumoBinary = "sumo-gui"
sumoCmd = [sumoBinary, "-c", "city.sumocfg"]
traci.start(sumoCmd)

edges_to_track = [edge for edge in traci.edge.getIDList() if not edge.startswith(":")]
vehicle_counts = {edge: 0 for edge in edges_to_track}

csv_file = "vehicle_counts_with_traffic.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestep"] + edges_to_track)

    timestep = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        timestep += 1

        current_counts = {}

        for edge in edges_to_track:
            count = traci.edge.getLastStepVehicleNumber(edge)
            current_counts[edge] = count
            vehicle_counts[edge] += count

        row = [timestep] + [current_counts[edge] for edge in edges_to_track]
        writer.writerow(row)

traci.close()
print(f"Vehicle counts and traffic levels saved to {csv_file}")