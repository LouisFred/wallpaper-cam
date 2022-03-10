import ctypes
from ctypes.wintypes import RGB
from datetime import datetime
from importlib.resources import path
import cv2 as cv
import time
from threading import Thread,Lock
from cv2 import VideoCapture
from cv2 import CAP_FFMPEG
import numpy as np
import os
import logging
from outcome import capture
logging.basicConfig(level=logging.DEBUG)
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import json
import pyowm
import requests


picdir = os.path.join('C:/Users/Louis/Pictures/screen/cam/')
#Place for image storage.

DATEFORMAT = "%a %x"
TIMEFORMAT = "%H:%M"
#Formatting

ut = time.time()
#print(ut)

#open camera and avoid overexposure
capture = cv.VideoCapture() 
capture.open(0)   

#get image
ret,img = capture.read()


class WebcamVideoStream :
    #grab the frame from a stream to avoid overexposure
    def __init__(self, src = 0,width = 1920,height = 1080) :
        self.stream = cv.VideoCapture(src)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self) :
        if self.started :
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()


def setimg(img):
    cv.imwrite('C:\\Users\\Louis\\Pictures\\screen\\cam\\temp.jpg',img)
    print("Image Set")


def set_wallpaper(path):
#set image use windows system api
    SPI_SETDESKWALLPAPER = 20
    path = 'C:\\Users\\Louis\\Pictures\\screen\\cam\\temp.jpg'
    ctypes.windll.user32.SystemParametersInfoW(20,0,path,1)
    return;


def set_alldata():
    with Image.open("C:/Users/Louis/Pictures/screen/cam/temp.jpg").convert("RGBA") as base:

        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

        # get a font you want
        fntb = ImageFont.truetype("C:/Users/Louis/Pictures/screen/cam/Futura Bold Italic font.ttf", 13)
        fnt = ImageFont.truetype("C:/Users/Louis/Pictures/screen/cam/Futura Medium Italic font.ttf", 14)
        fnw = ImageFont.truetype("C:/Users/Louis/Pictures/screen/cam/Futura Bold Italic font.ttf", 28)
        fnw2 = ImageFont.truetype("C:/Users/Louis/Pictures/screen/cam/Futura Bold Italic font.ttf", 125)
        fnj = ImageFont.truetype("C:/Users/Louis/Pictures/screen/cam/simsun.ttc", 12)

        # get a drawing context
        d = ImageDraw.Draw(txt)
        px = base.load()
        rgbpx=px[700,100]
        #select 1 pixel color
        now = datetime.now()
        datestring = now.strftime(DATEFORMAT).capitalize()
        timestring = now.strftime(TIMEFORMAT)

        d.text((800, 226),datestring, font=fnw,fill=(255, 255, 255, 255),align='right')  
        #print(timestring.time)
        
        d.text((795, 230),timestring, font=fnw2,fill=(255, 255, 255, 255),align='right')

        #time set
        logging.info("Clock updated.")
        
        #set city ID
        city_id = 2110683 #Tsukuba City
        owm = pyowm.OWM('')
        mgr = owm.weather_manager()

        obs = mgr.weather_at_id(city_id)
        weather=obs.weather
        temperature = obs.weather.temperature()
        #humidity = obs.weatget_humidity()
        pressure = obs.weather.barometric_pressure()
        #clouds = obs.weather.cloud()
        wind = obs.weather.wind()
        rain = obs.weather.rain
        sunrise = obs.weather.sunrise_time(timeformat='date')
        sunset =  obs.weather.sunset_time(timeformat='date')
        visibility = obs.weather.visibility()
        tempcel = str(temperature)
        tempmax = str('{0:.2f}'.format(temperature['temp_min']-273.15))
        tempmin = str('{0:.2f}'.format(temperature['temp_max']-273.15))
        tempstring ='TEMP@'+tempmax+"°"+'C '+'—'+tempmin+"°"+'C';
        pressurestr = 'AERO'+'@'+str(pressure['press'])+'hPA'
        windstr = 'WIND'+'@'+str(wind['speed'])+'m/s                               '+'Direction'+'@'+str(wind['deg'])+'°'
        desstr = str(weather.detailed_status)
        desstr = desstr.title()
        
        #draw UI
        
        d.text((800, 380), "Tsukuba", font=fnw)
        d.text((800, 406), desstr, font = fnt)
        d.text((800, 435), windstr,font = fntb)
        d.text((800, 450), tempstring,font = fntb)
        d.text((800, 465), pressurestr,font = fntb)
        d.text((800, 480), str('RISE @'+sunrise.strftime('%I:%M')), font =fntb)
        d.text((1030, 480), str('SunSet @'+sunset.strftime('%I:%M')), font = fntb)
    
        
        logging.info("weather Updated")
        
        #set earthquake info, limit = 4 newest
        
        earthquake = requests.get('https://api.p2pquake.net/v1/human-readable?limit=4')
        earthquake_data = earthquake.content.decode('utf-8')
        earthquake_publish_time = []
        earthquake_time = []
        earthquake_coodinates = []  #震源地の緯度経度
        earthquake_scale = []   #最大震度の値
        earthquake_hypocenter = []  #震源地

        indexe = 0
            # str式のjsonデータをdict式のデータへ変換：
        dict_earthquake_data = json.loads(earthquake_data)
        #print(dict_earthquake_data)
        for data in dict_earthquake_data:
            if(data["code"] == 551):
                indexe = dict_earthquake_data.index(data)
                #print(dict_earthquake_data.index(data)) 
                #print(dict_earthquake_data[dict_earthquake_data.index(data)])
                t1 = dict_earthquake_data[dict_earthquake_data.index(data)]
                t2 = t1.get('earthquake')
                time = t1.get('time')

                #print(t2.get('hypocenter'))
                t3 = t2.get('hypocenter')
                center = t3.get('name')
                #center2 = 
                depth = t3.get('depth')
                mag = t3.get('magnitude')
                t4 = t3.get('latitude')+'  '+t3.get('longitude')
                string1 = '-'+str(indexe+1)+'- '+'Time:'+time[5:19]+' @ '+center
                string2 = 'Mag:'+mag+'  @ '+t4
                
            # draw UI
            
                d.text((831, 760+indexe*40), string1, font = fnj,fill=(rgbpx[0],rgbpx[1],rgbpx[2],120))
                d.text((830, 760+indexe*40), string1, font = fnj,fill=(255,255,255,120))
                d.text((831, 780+indexe*40), string2, font = fnj,fill=(rgbpx[0],rgbpx[1],rgbpx[2],120))
                d.text((830, 780+indexe*40), string2, font = fnj,fill=(255,255,255,120))

                #draw.line((5,31+indexe*27, 270, 31+indexe*27), fill = 0)
            else:
                string3 = '-'+str(indexe+2) +'- 尚未确认的地震源'
                string4 = '--- 震源地はまだ確認されていない'
                d.text((831, 760+indexe*40), string3, font = fnj,fill=(rgbpx[0],rgbpx[1],rgbpx[2],120))
                d.text((830, 760+indexe*40), string3, font = fnj,fill=(255,255,255,120))
                d.text((831, 780+indexe*40), string4, font = fnj,fill=(rgbpx[0],rgbpx[1],rgbpx[2],120))
                d.text((830, 780+indexe*40), string4, font = fnj,fill=(255,255,255,120))
                    #draw.line((5,31+(indexe+1)*27, 270, 31+(indexe+1)*27), fill = 0)
            earthquakelog="Earthquake"+str( indexe) +" Updated"
            logging.info(earthquakelog)

        print("PIL img set.")
        out = Image.alpha_composite(base, txt)
        out = out.convert('RGB')
        
        #convert PIL object to OpenCV
        
        opencv_out = np.array(out)
        opencv_out = opencv_out[:, :, ::-1].copy() 
        
        #over write image
        
        cv.imwrite('C:\\Users\\Louis\\Pictures\\screen\\cam\\temp.jpg',opencv_out)
        print("OpenCV img setted.")

#main process

if __name__ == "__main__":
    
    #start cam
    
    vs = WebcamVideoStream().start()
    
    #update period
    
    minute = 15
    s=time.time()
    print(s)
    
    while(True):
        s2 = time.time() 
        img = vs.read()
 
        #wait 2 second and grab frame from cam stream
  
        if(s2-s>2):
            setimg(img)
            set_alldata()
            set_wallpaper(path)
            print('Set Wallpaper!')
            print('Camera Released')    
            time.sleep(minute*60)
            print('Wallpaper Updated!')
            s=s2


