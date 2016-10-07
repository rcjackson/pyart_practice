
from boto.s3.connection import S3Connection
import pyart
import gzip
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import rcParams
import shutil, os
from datetime import timedelta, datetime
import numpy as np
import tempfile


def nearestDate(dates, pivot):
    return min(dates, key=lambda x: abs(x - pivot))

# Subroutine to get radar data from NEXRAD site
def get_radar_from_aws(site, datetime_t):
    """
    Get the closest volume of NEXRAD data to a particular datetime.
    Parameters
    ----------
    site : string
        four letter radar designation 
    datetime_t : datetime
        desired date time
    """
    
    # First create the query string for the bucket knowing
    # how NOAA and AWS store the data
    
    my_pref = datetime_t.strftime('%Y/%m/%d/') + site
    
    # Connect to the bucket
    
    conn = S3Connection(anon = True)
    bucket = conn.get_bucket('noaa-nexrad-level2')
    
    # Get a list of files 
    
    bucket_list = list(bucket.list(prefix = my_pref))
    # print(bucket_list)
    # we are going to create a list of keys and datetimes to allow easy searching
    
    keys = []
    datetimes = []
    
    # populate the list

    for i in range(len(bucket_list)):
        this_str = str(bucket_list[i].key)
        if 'gz' in this_str:
            endme = this_str[-22:-3]
            fmt = '%Y%m%d_%H%M%S_V06' 
            dt = datetime.strptime(endme, fmt)
            datetimes.append(dt)
            keys.append(bucket_list[i])
            # print(dt)
        if this_str[-3::] == 'V06':  #'LSX20160707_000150_' does not match format '%Y%m%d_%H%M%S_V06'
            # print(this_str)
            # print(this_str[-19::])
            endme = this_str[-19::]
            fmt = '%Y%m%d_%H%M%S_V06'
            dt = datetime.strptime(endme, fmt)
            datetimes.append(dt)
            keys.append(bucket_list[i])

    # function to allow easy searching
    
    def func(x):
        delta = x - datetime_t if x > datetime_t else timedelta.max
        return delta
  
    # find the closest available radar to your datetime

    closest_datetime = nearestDate(datetimes, datetime_t)
    index = datetimes.index(closest_datetime)

    # print(closest_datetime)
    # create a temp file, download radar data to file from S3
    # read into a radar object and return

    localfile = tempfile.NamedTemporaryFile()
    keys[index].get_contents_to_filename(localfile.name)
    radar = pyart.io.read(localfile.name)
    return radar

# get_time_array
#     start_time = datetime class of the start time for animation
#     end_time = datetime class of the end time for animation
#     delta_time = datetime class of the time interval between each scan
# This procedure acquires an array of times between start_time and end_time
def get_time_array(start_time, end_time, delta_time):
    
    cur_time = []
    nxt = start_time
    while(nxt < end_time):
       cur_time.append(nxt)
       nxt += delta_time
    return cur_time       

# get_time_array
#     start_year = Start year of animation
#     start_month = Start month of animation
#     start_day = Start day of animation
#     start_hour = Start hour of animation
#     end_year = End year of animation
#     end_month = End month of animation
#     end_day = End day of animation
#     end_minute = End minute of animation
#     minute_interval = Interval in minutes between scans (default is 5)
#     site = NEXRAD site
# This procedure acquires an array of datetimeclasses between 
# start_time and end_time.
def get_radar_times(start_year, start_month, start_day,
                    start_hour, start_minute, end_year,
                    end_month, end_day, end_hour, 
                    end_minute, site, minute_interval=5):

    # Convert start and end time into datetime class
    
    start_time_dt = datetime(start_year, start_month, start_day,
                             start_hour, start_minute, )
    end_time_dt = datetime(end_year, end_month, end_day,
                           end_hour, end_minute, )
    print start_time_dt
    # Get a directory list of all of the NEXRAD scans in the time interval
    
    delta_time = timedelta(minutes=minute_interval)
    times = get_time_array(start_time_dt, end_time_dt, delta_time)
    
    return times


# Plot the radars from given time.

times = get_radar_times(2016, 10, 6, 19, 00, 
                         2016, 10, 6, 21, 00, 
                         "KAMX", minute_interval=5)
site = "KAMX"


# This is the callback function for the animation.
def plot_radar_frame(frame_number):

    plt.clf()
    
    Radar = get_radar_from_aws(site, times[frame_number])
    print "Downloading scan closest to " + times[frame_number].strftime('%H:%M:%S')
    display = pyart.graph.RadarMapDisplay(Radar)
    display.plot_ppi_map('reflectivity', sweep=0, min_lon=-83, max_lon=-76,
                         min_lat=22, max_lat=30, vmin=-10, vmax=70)
    display.basemap.drawcounties()
    rcParams.update({'font.size': 15})
    



# Plot the animation.
print (len(times))
figure = plt.figure(figsize=(8, 6))
AnimatedGIF = animation.FuncAnimation(figure, plot_radar_frame,
                                      frames=len(times))
AnimatedGIF.save("/home/rjackson/pyart_test/Matthew_animation.gif",
                 writer='imagemagick', fps=3)



