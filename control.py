import sys
import datetime 
from datetime import timedelta
from datetime import datetime
import subprocess as sp
import pandas as pd



args = sys.argv


start_date = args[1]
end_date = args[2]

s_time = datetime.strptime(start_date, '%Y%m%d-%H%M') #Converting into datetimes
e_time = datetime.strptime(end_date, '%Y%m%d-%H%M') #Converting into datetimes
tdelta = timedelta(minutes=10) #Creating a time delta



while s_time < e_time:
   cmd = 'python glm-pull.py '+str(s_time)
   print (cmd)
   p = sp.Popen(cmd,shell=True)
   p.wait()

   s_time += tdelta
