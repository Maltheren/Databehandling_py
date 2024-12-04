import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from Spheremachine import WireframeSphere


class Measurement:
    data = pd.DataFrame()
    real_pos = (0,0,0)
    def __init__(self, data, real_pos):
        self.data = data
        self.real_pos = real_pos

    def std(self):
        sum_std = self.data["X"].std()**2+ self.data["Y"].std()**2 +self.data["Z"].std()**2
        return (sum_std/len(self.data*3))**(1/2)
        
        # https://math.stackexchange.com/questions/850228/finding-how-spreaded-a-point-cloud-in-3d
        # https://stats.stackexchange.com/questions/13272/2d-analog-of-standard-deviation/13274#13274

    def mean(self):
        return (self.data["X"].mean(), self.data["Y"].mean(),self.data["Z"].mean())
    def median(self):
        return (self.data["X"].median(), self.data["Y"].median(),self.data["Z"].median())


def load_values(filename: str, realpos):
    data = pd.read_csv(filename)
    print("Loaded: \"{}\", available coloums: {}".format(filename, data.columns))
    return Measurement(data, realpos)


def fix_zval(measurements: list[Measurement]):
    z_satellite = 2.249
    for measurement in measurements:
        measurement.data.loc[measurement.data['Z'] > z_satellite, 'Z'] = 2*z_satellite - measurement.data["Z"]

    return measurements


def plot_single(measurement: Measurement):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")


    subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
    subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', s=4)
    median = measurement.median()
    std = measurement.std()
    subplt.plot_wireframe(*WireframeSphere(centre=median, radius=std*2), color="r", alpha=0.2)

    subplt.set_xlim(median[0]-1, median[0]+1)
    subplt.set_ylim(median[1]-1, median[1]+1)
    subplt.set_zlim(0, 2.25)
    subplt.set_aspect("equal")

    plt.show()


def plot_single(measurement: Measurement, sats):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")


    subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
    subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', s=4)
    median = measurement.median()
    std = measurement.std()
    subplt.plot_wireframe(*WireframeSphere(centre=median, radius=std*2), color="r", alpha=0.2)
    colortable = ["r", "g", "b"]
    for i in range(0, len(measurement.data)):
        row = measurement.data.iloc[i]
        sat_ID = int(row["ID"])
        sat = sats.iloc[sat_ID]
        x = (sat["x"], row["X"])
        y = (sat["y"], row["Y"])
        z = (sat["z"], row["Z"])
        subplt.plot(x,y,z, color=colortable[sat_ID], alpha=0.2)

    for i in range(0, len(sats)):
        sat = sats.iloc[i]
        subplt.plot(sat["x"],sat["y"],sat["z"], marker='x', color=colortable[i])
        subplt.text(sat["x"],sat["y"],sat["z"], "sat[{}]".format(i), color=colortable[i])

    subplt.set_xlim(0-2, 0+2)
    subplt.set_ylim(0-2, 0+2)
    subplt.set_zlim(0, 2.25)
    subplt.set_aspect("equal")

    plt.show()


def plot_all(measurements: list[Measurement]):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")
    for measurement in measurements:
        subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', s=3)

def plot_all(measurements: list[Measurement], sats):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")

    colortable = ["r", "g", "b"]

    for measurement in measurements:
        subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.')
        for i in range(0, len(measurement.data)):
            row = measurement.data.iloc[i]
            sat_ID = int(row["ID"])
            sat = sats.iloc[sat_ID]
            x = (sat["x"], row["X"])
            y = (sat["y"], row["Y"])
            z = (sat["z"], row["Z"])
            subplt.plot(x,y,z, color=colortable[sat_ID], alpha=0.2, linewidth=0.8)

        for i in range(0, len(sats)):
            sat = sats.iloc[i]
            subplt.plot(sat["x"],sat["y"],sat["z"], marker='x', color=colortable[i])
            subplt.text(sat["x"],sat["y"],sat["z"], "sat[{}]".format(i), color=colortable[i])

    subplt.set_xlim(0-2, 0+2)
    subplt.set_ylim(0-2, 0+2)
    subplt.set_zlim(0, 2.25)
    subplt.set_aspect("equal")





def plot_CI(measurements: list[Measurement]):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")
    for measurement in measurements:
        meanpoint = subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        ##subplt.text(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2], "({}, {}, {})".format(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2]))
        median = measurement.median()
        std = measurement.std()
        subplt.plot_wireframe(*WireframeSphere(centre=median, radius=std*2), color=meanpoint[0].get_color(), alpha=0.2)



    subplt.set_zlim(0, 2.25)
    subplt.set_aspect("equal")

    plt.show(block = False)



satellites = pd.DataFrame(
    {
    "x": [1.545, -1.696, 0.334],
    "y":[-1.928, -1.929, 2.34],
    "z":[2.247, 2.250, 2.256]
    }
)




if __name__ == "__main__":
    measurements_raw = []
    measurements_raw.append(load_values("X-1Y-1Z07.log",    (-1,  -1,   0.72)))
    measurements_raw.append(load_values("X-1Y-15Z07.log",   (-1,  -1.5, 0.72)))
    measurements_raw.append(load_values("X-1Y15Z07.log",    (-1,   1.5, 0.72)))
    measurements_raw.append(load_values("X-05Y05Z07.log",   (-0.5, 0.5, 0.72)))
    measurements_raw.append(load_values("X-09Y1Z07.log",    (-0.9, 1,   0.72)))
    measurements_raw.append(load_values("X0Y0Z07.log",      (0,    0,   0.72)))
    measurements_raw.append(load_values("X0Y1Z07.log",      (0,    1,   0.72)))
    measurements_raw.append(load_values("X1Y1Z07.log",      (1,    1,   0.72)))
    measurements_raw.append(load_values("X05Y-1Z07.log",    (0.5, -1,   0.72)))
    measurements_raw.append(load_values("X05Y2Z07.log",     (0.5,  2,   0.72)))
    measurements_raw.append(load_values("X05Y05Z07.log",    (0.5,  -0.5, 0.72)))
    #measurements_raw.append(load_values("X1545Y2475Z07.log",(1.54, 2.47,0.72)))




    measurents_fixed_z = fix_zval(measurements_raw)
    
    plot_all(measurents_fixed_z, satellites)
    plot_CI(measurents_fixed_z)
    plot_single(measurents_fixed_z[10], satellites)