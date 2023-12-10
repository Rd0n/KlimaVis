from time import sleep

from process_file import proc_file
from process_file import calc_anomaly
from video import make_video
import os
import multiprocessing

if __name__ == '__main__':

    ncFiles = [nc for nc in os.listdir('data/tas_yearly') if nc.endswith(".nc")]

    # Calculate anomaly for each file
    #for file in ncFiles:
    #    p = multiprocessing.Process(target=calc_anomaly, args=(
    #        'data/tas_yearly/' + file, 'data/tas_yearly/' + file))
    #    p.start()

    for file in ncFiles:
        # Create process for each file
        p = multiprocessing.Process(target=proc_file, args=('data/tas_yearly/' + file, 'relative', -13.769104, 13.769104))
        p.start()
