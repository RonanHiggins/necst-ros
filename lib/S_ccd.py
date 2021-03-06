import datetime
from astropy.time import Time
import math
import time
import pyinterface
import numpy as np
from PIL import Image
import os
#from pyslalib import slalib




class ccd_controller(object):

    error = []
    status = ''
    
    
    def __init__(self):
        #open
        #self.img = pyinterface.create_gpg5520(1)
        return
    
    def print_msg(self,msg):
        print(msg)
        return
    
    def print_error(self,msg):
        self.error.append(msg)
        self.print_msg('!!!!ERROR!!!!' + msg)
        return
    
    def oneshot(self, dirname, filename, frame_no = 1, size=640*480*3, Bufferformat='IFIMG_COLOR_RGB24', StartMode = 'IFIMG_DMACAPTURE_START', framenum = 1):
        """
        # set buffer
        self.img.set_format(frame_no, size, Bufferformat)
        #start cap
        self.img.start_cap(frame_no, StartMode)
        # get status
        status = self.img.get_status()
        # get data
        self.img.get_data(frame_no, framenum, size, dwDataFormat = 'IFIMG_COLOR_RGB24', dwXcoodinates = 0, dwYcoodinates = 0, dwXLength = 640, dwYLength = 480)
        # save data
        self.img.save(fiename, size*3, Bufferformat)
        return status
        """

        #use below in real telescope
        #f = open("/home/nfs/necopt-old/ccd-shot/ccd-shot-command.txt", "w")#tmp
        #f.write(str(dirname) + "/" + str(filename) + ".bmp")#tmp
        #f.close()#tmp
        
        if os.path.exists(str(dirname)):
            pass
        else:
            os.mkdir(str(dirname))
        #simulator part ----------------------------
        array = np.zeros((480,640), dtype=np.uint)
        for x in range(10):
            array[235+x][315:325] = 255
        Image.fromarray(np.uint8(array)).save((str(dirname) + str(filename) + ".bmp"))
        #simulator end -----------------------------
        return
    
    def save_status(self, x, y, number, magnitude, az_star, el_star, mjd, data_name, secofday, status):
        print('save_status')
        #f = open("/home/amigos/data/experiment/opt/"+str(data_name)+"/process.log", "a")#tmp
        if os.path.exists('/home/amigos/s_opt/p_log/'):
            pass
        else:
            os.mkdir('/home/amigos/s_opt/p_log/')
        f = open('/home/amigos/s_opt/p_log/process.log', 'a')#simulator
        
        #geo_status = [x1,x2,y1,y2] #for test
        geo_status = [0,0,0,0]
        geo_x = 0
        geo_y = 0
        #geo_temp = 0#shiotani comment outed
        geo_temp = [0,0]#shiotani added
        
        #write papram
        f.write(str(number)+" "+str(magnitude)+" "+str(mjd)+" "+str(secofday)+" "+str(status.Command_Az)+" "+str(status.Command_El)+" "\
        +str(status.Current_Az)+" "+str(status.Current_El)+" "+str(status.Current_Dome)+" "+str(x)+" "+str(y)+" "+str(status.OutTemp)+" "+str(status.Press)\
        +" "+str(status.OutHumi)+" "+str(az_star)+" "+str(el_star)+" "+str(geo_x)+" "+str(geo_y)+" "+str(geo_status[0])+" "+str(geo_status[1])\
        +" "+str(geo_temp[0])+" "+str(geo_status[2])+" "+str(geo_status[3])+" "+str(geo_temp[1]))
        f.write("\n")
        f.close()
        return
    
    def all_sky_shot(self, number, magnitude, az_star, el_star, data_name, status):
        #shiotani added
        #--------------
        x_mom1 = 0
        y_mom1 = 0
        #--------------

        thr = 80 #threshold of brightness
        
        #status = {"Command_Az":0,"Command_El":0,"Current_Az":0,"Current_El":0,"OutTemp":0,"Press":0,"OutHumi":0}
        
        date = datetime.datetime.today()
        month = str("{0:02d}".format(date.month))
        day = str("{0:02d}".format(date.day))
        hour = str("{0:02d}".format(date.hour))
        minute = str("{0:02d}".format(date.minute))
        second = str("{0:02d}".format(date.second))
        name = str(date.year)+month+day+hour+minute+second
        
        #oneshot
        self.oneshot(data_name,name)
        mjd = Time(date).mjd
        secofday = date.hour*60*60 + date.minute*60 + date.second + date.microsecond*0.000001
        
        #load array
        #path = os.getcwd()
        #com = "mv "+str(path)+"/"+str(name)+".bmp /home/amigos/NECST/soft/data/"+str(data_name)+"/"+str(name)+".bmp"
        #ret = commands.getoutput(com)
        #print(ret)
        
        #in_image = Image.open("/home/nfs/necopt-old/ccd-shot/data/"+str(data_name)+"/"+name+".bmp")#tmp
        in_image = Image.open('/home/amigos/s_opt/image' + "/" + str(name) + ".bmp")#simulator
        image = np.array(in_image.convert('L'))
        ori_image = image
        
        #threshold
        image[image < thr] = 0
        
        #mode
        bins = np.bincount(image.flatten())
        num = np.argmax(bins[1:]) +1
        nmax = np.max(bins[1:])        
        
        if nmax == 0:
            print("CAN'T FIND STAR") #black photograph
            return 1
            
        else:
            #find center
            y, x = (np.sum(np.where(image == num), axis=1) / nmax).astype(np.int)
            f = np.sum(image[y-10:y+10,x-10:x+10])
            if f == 0.: #two or more stars
                print("MANY STARS ARE PHOTOGRAPHED")
                return 2
            else:
                for i, _l in enumerate(image[y-10:y+10,x-10:x+10]):
                    for j, _a in enumerate(_l):
                        x_mom1 += (x+j-10) * _a
                        y_mom1 += (y+i-10) * _a
                xx = x_mom1 / f
                yy = y_mom1 / f
                print(xx)
                print(yy)
        
                self.save_status(xx, yy, number, magnitude, az_star, el_star, mjd, data_name, secofday, status)
                return [xx, yy]
            
    
    
    
    
    
    #for tracking(test)
    def save_track_status(self, x, y, ra, dec, az_star, el_star, mjd, data_name, secofday, status):
        if os.path.exists("/home/amigos/NECST/soft/core/"+str(data_name)):
            pass
        else:
            os.mkdir("/home/amigos/NECST/soft/core/"+str(data_name))
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
        f = open("/home/amigos/NECST/soft/core/"+str(data_name)+"/param.log", "a")
        
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        
        #geo_status = [x1,x2,y1,y2] #for test
        geo_status = self.geo.read_geomech()
        geo_x = (geo_status[0]-geo_status[1])/2
        geo_y = (geo_status[2]-geo_status[3])/2
        geo_temp = self.geo.read_geomech_temp()
        
        #write papram
        f.write(str(ra)+" "+str(dec)+" "+str(mjd)+" "+str(secofday)+" "+str(status.Command_Az)+" "+str(status.Command_El)+" "\
        +str(status.Current_Az)+" "+str(status.Current_El)+" "+str(status.Current_Dome)+" "+str(x)+" "+str(y)+" "+str(status.OutTemp)+" "\
        +str(status.Press)+" "+str(status.OutHumi)+" "+str(az_star)+" "+str(el_star)+" "+str(status.WindDir)+" "+str(status.WindSp)+" "\
        +str(geo_x)+" "+str(geo_y)+" "+str(geo_status[0])+" "+str(geo_status[3])+" "+str(geo_temp[0])+" "+str(geo_status[1])+" "\
        +str(geo_status[3])+" "+str(geo_temp[1]))
        f.write("\n")
        f.close()
        return
    
    
    
    #for tracking(test)
    def onepoint_shot(self, ra, dec, az_star, el_star, data_name, status):
        #shiotani added
        #--------
        x_mom1 = 0
        y_mom1 = 0
        #--------
        
        thr = 80 #threshold of brightness <=?
        
        if os.path.exists("/home/amigos/NECST/soft/data/"+str(data_name)):
            pass
        else:
            os.mkdir("/home/amigos/NECST/soft/data/"+str(data_name))
        
        name = time.strftime('%Y%m%d_%H%M%S')
        
        #oneshot
        self.oneshot(name)
        date = datetime.datetime.today()
        ret = slalib.sla_cldj(date.year, date.month, date.day)
        mjd = ret[0]
        secofday = date.hour*60*60 + date.minute*60 + date.second + date.microsecond*0.000001
        
        path = os.getcwd()
        com = "mv "+str(path)+"/"+str(name)+".bmp /home/amigos/NECST/soft/data/"+str(data_name)+"/"+str(name)+".bmp"
        ret = commands.getoutput(com)
        
        #load array
        print(ret)
        in_image = Image.open("/home/amigos/NECST/soft/data/"+str(data_name)+"/"+name+".bmp")
        image = np.array(in_image.convert('L'))
        ori_image = image
        
        #threshold
        image[image < thr] = 0
        
        #mode
        bins = np.bincount(image.flatten())
        num = np.argmax(bins[1:]) +1
        nmax = np.max(bins[1:])        
        
        if nmax == 0:
            print("CAN'T FIND STAR") #black photograph
            return 1
            
        else:
            #find center
            y, x = (np.sum(np.where(image == num), axis=1) / nmax).astype(np.int)
            f = np.sum(image[y-10:y+10,x-10:x+10])
            if f == 0.: #two or more stars
                print("MANY STARS ARE PHOTOGRAPHED")
                return 2
            else:
                for i, _l in enumerate(image[y-10:y+10,x-10:x+10]):
                    for j, _a in enumerate(_l):
                        x_mom1 += (x+j-10) * _a
                        y_mom1 += (y+i-10) * _a
                xx = x_mom1 / f
                yy = y_mom1 / f
                        
                print("==============================================")
                print("==============================================")
                print("==============================================")
                print(xx)
                print(yy)
                
                self.save_track_status(xx, yy, ra, dec, az_star, el_star, mjd, data_name, secofday, status)
                return
