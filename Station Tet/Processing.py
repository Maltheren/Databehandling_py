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


    def Errordistance(self):
        errors = []
        for i in range(0, len(self.data)):
            row = self.data.iloc[i]
            errors.append(((self.real_pos[0]-row["X"])**2+(self.real_pos[1]-row["Y"])**2+(self.real_pos[2]-row["Z"])**2)**(1/2))
        return pd.DataFrame(errors)


    def Errordistance2mean(self):
        errors = []
        mean_pos = self.median()
        for i in range(0, len(self.data)):
            row = self.data.iloc[i]
            errors.append(((mean_pos[0]-row["X"])**2+(mean_pos[1]-row["Y"])**2+(mean_pos[2]-row["Z"])**2)**(1/2))
        return pd.DataFrame(errors, columns=['Error'])

    def std(self):
        sum_std = self.data["X"].std()**2+ self.data["Y"].std()**2 +self.data["Z"].std()**2
        return (sum_std/len(self.data))**(1/2)
        
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


def filter_outlier(measurement: Measurement, sd=10):
    errors = measurement.Errordistance2mean()
    data = measurement.data
    std = measurement.std()
    mean = measurement.mean()
    thres = (sd*std)
    keep = [False for i in range(len(errors))] 
    for i in range(0, len(measurement.data)):
        if(errors.iloc[i]["Error"] < 2*thres):
            keep[i] = True
    measurement.data = measurement.data.loc[keep]
    return measurement
        

    
def filter_outliers(measurements: list[Measurement], sd=10):
    results: list[Measurement] = []
    for measurement in measurements:
        results.append(filter_outlier(measurement, sd))
    return results





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


def plot_single(measurement: Measurement, sats, lines=False, iterations=True):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")

    if(iterations):
        mark = subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        subplt.plot(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', markersize=6, alpha=0.6, linewidth=0.4, color=mark[0].get_color(), linestyle="dashed")

    else:
        mark = subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', s=6,  color=mark[0].get_color())



    median = measurement.median()

    std = measurement.std()
    subplt.plot_wireframe(*WireframeSphere(centre=median, radius=std*2), color="r", alpha=0.2, linestyle="dashed")
    colortable = ["r", "g", "b"]

    if lines:
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

    plt.show(block=False)


def plot_all_nosats(measurements: list[Measurement]):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")
    for measurement in measurements:
        mark = subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        subplt.scatter(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.', s=3, color=mark[0].get_color())

def plot_all(measurements: list[Measurement], sats, lines=False, points=False):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")

    colortable = ["r", "g", "b"]

    for measurement in measurements:
        mark= subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x', markersize=10, linewidth=0)
        subplt.plot(measurement.data["X"], measurement.data["Y"], measurement.data["Z"], marker='.',  alpha=0.6, linewidth=0.4, color=mark[0].get_color(), linestyle="dashed")
        if(lines):
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
        subplt.plot(sat["x"],sat["y"],sat["z"], marker='X', color=colortable[i])
        subplt.text(sat["x"],sat["y"],sat["z"]+0.1, "sat[{}]".format(i), color=colortable[i])

    subplt.set_xlim(0-2, 0+2)
    subplt.set_ylim(0-2, 0+2)
    subplt.set_zlim(0, 2.25)
    subplt.set_xlabel("x [m]")
    subplt.set_ylabel("y [m]")
    subplt.set_zlabel("z [m]")
    subplt.set_aspect("equal")
    subplt.legend(['Position to be tested', 'Postional estimates by the system'])



def plot_errors_hist(measurement: Measurement):
    #plt.rcParams['text.usetex'] = True
    errors2 = measurement.Errordistance2mean()
    
    vals, bins = np.histogram(errors2, bins=500)
    cum_vals = np.cumsum(vals)/len(errors2)
    
    
    fig = plt.figure()
    subplt1 = fig.add_subplot()
    subplt2 = subplt1.twinx()  
    subplt1.axvline(x= measurement.std()*2,  label = '2std', color='red', linestyle="dashed")
    
    subplt1.stairs(vals, bins, label = 'Observations')
    subplt2.stairs(cum_vals, bins, linestyle='dashed', label = 'cumulative errors')
    

    subplt2.set_ylim(0,1)
    subplt2.set_ylabel('cummulative probability')
    subplt1.set_ylim(0, max(vals*2))
    subplt1.set_xlabel('Distance, [m]')
    subplt1.set_xlim(0, 0.3)
    subplt1.set_ylabel('Density')
    subplt1.set_title('Distance-error to the tested point')
    fig.legend(loc='lower right')
    plt.show()



def plot_hist_all(measurements: list[Measurement]):
    fig = plt.figure()
    subplt1 = fig.add_subplot()
    subplt2 = subplt1.twinx()  
    
    
    for measurement in measurements:
        errors2 = measurement.Errordistance2mean()
        vals, bins = np.histogram(errors2, bins=600)
        bins = np.append(bins, [10])
        vals = np.append(vals, [vals[len(vals)-1]])
        cum_vals = np.cumsum(vals)/len(errors2)
        subplt1.stairs(vals, bins)
        subplt2.stairs(cum_vals, bins, linestyle='dashed')



    subplt2.set_ylim(0,2)
    subplt2.set_ylabel('Cummulative probability [Dotted]')
    subplt1.set_ylim(0, max(vals*2))
    subplt1.set_xlabel('Distance to most median[m]')
    subplt1.set_xlim(0, 4)
    subplt1.set_ylabel('Observations [Solid]')
    subplt1.set_title('Euclidean positional error')
    subplt1.legend()
    plt.show()



def plot_CI(measurements: list[Measurement], sats):
    fig = plt.figure()
    subplt = fig.add_subplot(projection="3d")
    for measurement in measurements:
        meanpoint = subplt.plot(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2],  marker='x')
        ##subplt.text(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2], "({}, {}, {})".format(measurement.real_pos[0],measurement.real_pos[1],measurement.real_pos[2]))
        median = measurement.median()
        std = measurement.std()
        subplt.plot_wireframe(*WireframeSphere(centre=median, radius=std*2), color=meanpoint[0].get_color(), alpha=0.2)
    colortable = ["r", "g", "b"]
    for i in range(0, len(sats)):
        sat = sats.iloc[i]
        subplt.plot(sat["x"],sat["y"],sat["z"], marker='X', color=colortable[i])
        subplt.text(sat["x"],sat["y"],sat["z"]+0.1, "sat[{}]".format(i), color=colortable[i])


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

def get_measurements():
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
    return measurements_raw




if __name__ == "__main__":

    #measurements_raw.append(load_values("X1545Y2475Z07.log",(1.54, 2.47,0.72)))

    measurements_raw = get_measurements()
    measurents_fixed_z = fix_zval(measurements_raw)
    i = 0

    filtered = filter_outliers(measurents_fixed_z, sd=10)
 
    #plot_CI(measurents_fixed_z, satellites)
    #plot_errors_hist(measurents_fixed_z[10])

    plot_single(measurents_fixed_z[7], satellites, lines=False)
    #plot_errors_hist(measurents_fixed_z[3])
    #plot_hist_all(measurents_fixed_z)

    plot_all(measurents_fixed_z, satellites)

    plt.show()
    toterror =0
    for measurement in measurents_fixed_z:
        median = measurement.median()
        realpos = measurement.real_pos
        error = ((median[0]-realpos[0])**2 + (median[1]-realpos[1])**2 + (median[2]- realpos[2])**2)**(1/2)
        print("{}: \t SD: {:.3f}, offset: {:.3f}".format(i, measurement.std()*2, error))
        toterror += error
        i += 1
    print(toterror/i)

