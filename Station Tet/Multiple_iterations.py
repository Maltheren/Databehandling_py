import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import Processing as pr



def extract_tof(input: pr.Measurement):
    tof_data = input.data[["ID", "TOF"]]
    for i in range(0, len(tof_data)):
        temp =tof_data.iloc[i]["ID"]-1
        if (temp < 0):
            temp = 2
        tof_data.loc[i, "ID"] = temp
    return tof_data



def dist(pos1: list[float], pos2: list[float]):
    return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2)**(1/2)

def get_avg(pos1: list[float], pos2: list[float]):
    avg = []
    for i in range(0, len(pos1)):
        avg.append((pos1[i] +pos2[i]) /2)
    return avg


class TOF_bank:
    buffersize = 32
    def __init__(self):
        self.records = [0] * self.buffersize  # Instance-level attribute
        self.index = 0
        self.primary_sample = 0
        self.std_devs = 3

    def update(self, sample):
        
        self.records[self.index] = sample
        self.index = (self.index+1) % self.buffersize 
        median =self.median()
        std = self.std()
        std_devs = self.std_devs



        if (sample < median+ std_devs*std and sample > median - std_devs *std):
            self.primary_sample = sample ##Det er sansynligves en tof som er ægte
        else:
            print("woah")

        return self.primary_sample


    def median(self):
        return np.median(self.records)
    

    def std(self):
        return np.std(self.records)


class Target:

    pos_est = [1,1,1]
    satellites = pr.satellites
    tof_buffer: list[TOF_bank] = []
    
    def __init__(self):
        self.pos_est = [1,1,1]
        self.tof_buffer= [TOF_bank(), TOF_bank(), TOF_bank()]

    def update(self, tof: int, sat: int):
        ##Opdaterer lookuptable
        self.tof_buffer[sat%3].update(tof) ##primary sample bliver kun overskrevet hvis det giver mening

        ##Den der iterer for at finde vores skæringspunkt
        for i in range(0, 100):
            self.project(self.tof_buffer[i%3].primary_sample, i % 3)
        
        return self.pos_est








    def project(self, tof, i):
                    ##Finder vektor
        dx = self.pos_est[0] - self.satellites["x"][i]
        dy = self.pos_est[1] - self.satellites["y"][i]
        dz = self.pos_est[2] - self.satellites["z"][i]

        distance = tof/(10**5) *343 ##afstanden
        #Normaliserer svinet
        length = (dx**2+dy**2+dz**2)**(1/2)
        dx = dx/length * distance
        dy = dy/length * distance
        dz = dz/length * distance
        
        self.pos_est[0] = dx + self.satellites["x"][i]
        self.pos_est[1] = dy + self.satellites["y"][i]
        self.pos_est[2] = dz + self.satellites["z"][i]
        if(self.pos_est[2] > 2.247):
            self.pos_est[2] = 2*2.247-self.pos_est[2]
        self.pos_est[0] = np.nan_to_num(self.pos_est[0], nan=1)
        self.pos_est[1] = np.nan_to_num(self.pos_est[1], nan=1)
        self.pos_est[2] = np.nan_to_num(self.pos_est[2], nan=1)

def run_sim(tof_data):
    target = Target()
    positions = pd.DataFrame(
        {
            "x": [],
            "y": [],
            "z": []
        }
    )
    for i in range(0, len(tof_data)):
        row = tof_data.iloc[i]
        pos_est_filt  = target.update(row["TOF"], row["ID"])
        row = pd.DataFrame([pos_est_filt], columns=["x","y","z"])
        positions =pd.concat([positions, row],ignore_index=True )
    return positions


def generate_plot(measurements: list[pr.Measurement], show_old=True):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")
    if (show_old):
        i = 0
        for measurement in measurements:

            tof_data = extract_tof(measurement)
            results = run_sim(tof_data)
            mark = subplt.plot(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', markersize=6, alpha=0.6, linewidth=0.4,linestyle="dashed")
            subplt.plot(results["x"], results["y"], results["z"], marker="s", markersize=6, alpha=0.6, linewidth=0.4,linestyle="dashed")
    else:
        i = 0
        for measurement in measurements:
            tof_data = extract_tof(measurement)
            
            results = run_sim(tof_data)
            results.to_csv("Filtered_improved_pos/result{}.csv".format(i))
            subplt.plot(results["x"], results["y"], results["z"], marker=".", markersize=4, alpha=0.6, linewidth=0.4,linestyle="dashed")
            i +=1


    subplt.set_xlim(0-2, 0+2)
    subplt.set_ylim(0-2, 0+2)
    subplt.set_zlim(0, 2.25)
    subplt.set_aspect("equal")
    subplt.set_xlabel("X[m]")
    subplt.set_ylabel("Y[m]")
    subplt.set_zlabel("Z[m]")
    return fig


if __name__ == "__main__":
    
    measurements = pr.fix_zval(pr.get_measurements())
    i=0
    for measurement in measurements:
        measurement.data.to_csv("Old_fgpa/fixed_z{}.csv".format(i))
        i+=1


    generate_plot(measurements,show_old=False)
    pr.plot_all(measurements, pr.satellites, lines=False, points=True)
    plt.show()


