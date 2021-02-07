'''Tbot: a bot that translates speech in english to another language (google APIs) and speak
    and uses opencv to track movement of face'''
import time 
import sys
import os
import cv2
import threading
import serial                           #module for communication with arduino
import speech_recognition as sr         #module for recognizing speech
from googletrans import Translator      #for translation
from gtts import gTTS                   #for text-to-speech conversion
from playsound import playsound         #for playing the output
from mutagen.mp3 import MP3             #for getting the length of the audio output

#COMMUNICATION WITH ARDUINO

arduino = serial.Serial('COM7', 9600)
time.sleep(2)   #give  the connection time to settle
print("Connection to arduino...")

'''The above code will create a new serial object called "ardunio" on "COM7"
with a "9600" baud-rate and a .1 second timeout.
It is extremely important that you keep the chosen baud-rate on hand,
as it must match exactly with the baud-rate on the Ardiuno side of things.'''


listen_cycle = True                         #flag variable to determine if the robot is listening or speaking
stop = False                                #for exiting 

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')#for face detection
if face_cascade.empty():
  raise IOError('Unable to load the face cascade classifier xml file')


r=sr.Recognizer()

#mic=sr.Microphone()
#print(sr.Microphone.list_microphone_names())       USE THE ABOVE TO OBTAIN THE INDEX OF THE DESIRED MICROPHONE
mic = sr.Microphone(device_index=1)             #setting the microphone for use

languages={"Arabic":'ar',"Bengali":'bn',"Dutch":'nl',"French":'fr',
           "German":'de',"Greek":'el',"Gujarati":'gu',"Hindi":'hi',"Italian":'it',
           "Japanese":'ja',"Kannada":'kn',"Korean":'ko',"Latin":'la',
           "Malayalam":'ml',"Marathi":'mr',"Nepali":'ne',"Portuguese":'pt',"Polish":'pl',
           "Russian":'ru',"Spanish":'es',"Swedish":'sv',"Swahili":'sv',
           "Tamil":'ta',"Telugu":'te',"Thai":'th',"urdu":'ur'}

outputlang = 'Kannada'
outputlangCode = 'kn'

def intro_for_speech_rec():
    detected = False
    global outputlang, outputlangCode
    
    print(languages.keys()) 
    while not detected:
        with mic as  source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            outputlang = r.recognize_google(audio,language='en')
            detected = True                     #returns None if language not in dict
            
        except Exception:
            print("No recognizable speech. Try again")
            detected = False
            
        if outputlang not in languages.keys():
            print('Since no language from the list was chosen. Translating to', outputlangCode) 
            playsound("LanguageNotRecognised.mp3") 
            #default is kannada or prev language chosen
        else:
            outputlangCode=languages.get(outputlang)
            
    print(outputlang, outputlangCode)
    playsound("start.mp3")


def speech_rec():
    face_detected = 0
    while not face_detected:                    #while no face is detected keep waiting
            ret, img = cap.read()
            gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3)
            face_detected = len(faces)
            
    global stop
    playsound("intro.mp3")                      #play intro once face is detected
    intro_for_speech_rec()
    
    while 1:
        face_detected = 0
        while not face_detected:                #while no face is detected keep waiting
            ret, img = cap.read()
            gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3)
            face_detected = len(faces)
                
        with mic as  source:                    #now that you have detected a face, start speaking
            print('Speak now...')
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            result = r.recognize_google(audio,language='en')
            if result == 'bye'or result == 'stop':
                print("I hope that I was helpful. Bye.....")
                playsound("bye.mp3")
                break
            if result == 'change language':
                print("Switching language.....")
                playsound("whichlang.mp3")
                intro_for_speech_rec()
                continue                        #language set here so skip to the next cycle
        except Exception:
            print("No recognizable speech")
            continue                            #skip to the next detection of face and then listen cycle
        print(result)

        p=Translator()
        k=p.translate(result,dest=outputlangCode)
    
        transcript=str(k.text)
        print(transcript)
        
        speak = gTTS(text=transcript,lang=outputlangCode)       #text-to-speech
        speak.save("output.mp3")                                #saving the output as an mp3 file
        audio=MP3("output.mp3")                                     
        
        global listen_cycle
        listen_cycle = False                    #Now the robot speaks
        
        playsound("output.mp3")                 #playing the output
        listen_cycle = True
        
        os.remove("output.mp3")                 #deletes the o/p file
        
        

        
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            stop  = True
            break

    stop = True                                 #this will set condition for follow_face to exit
    exit(0)
    
    
        
def choose_face(faces):
    face_with_min_x = 0 
    min_x = faces[0][0]
    for i in range(len(faces)):
        min_x = faces[face_with_min_x][0]
        if listen_cycle:                       #for listen cycle
            if faces[i][0]<min_x:
                face_with_min_x = i
        else:                                  #for talk cycle
            if faces[i][0]>min_x:
                face_with_min_x = i
    return faces[face_with_min_x]



def follow_face():  
    mouth_pos = 0   
    direction = 20
    while 1:
        ret, img = cap.read()
        cv2.resizeWindow('img', 500,500)
        cv2.line(img,(500,250),(0,250),(0,255,0),1)
        cv2.line(img,(250,0),(250,500),(0,255,0),1)
        cv2.circle(img, (250, 250), 5, (255, 255, 255), -1)
        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3)
        
        if len(faces)==0:
            continue
        
        faces = choose_face(faces)
        
        x,y,w,h = faces
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),5)
        
        
        xx = int(int(x+(x+h))/2)
        yy = int(int(y+(y+w))/2)
        
        if listen_cycle:
            mouth_pos = 0  #leave it be
        else:
            if(mouth_pos + direction >40 or mouth_pos + direction < 0):
               direction = -direction
            mouth_pos = mouth_pos + direction
            
            
        data = "X{0:d}Y{1:d}M{2:d}Z".format(xx, yy, mouth_pos)
        
        #print ("output = '" +data+ "'")
        
        try:
            arduino.write(data.encode())
        except PermissionError:
            print("Encoded data : ", data.encode())     #for debugging
            print("Write failed because of permission error")
            
            
        time.sleep(0.1) 
        cv2.imshow('img',img)
        
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            global stop 
            stop = True
            break
        
        if stop:                                        #This happens when you say bye or stop, speech_rec genererally sets this value
            break
            
    arduino.close()
    cv2.destroyAllWindows()
    cap.release()
    exit(0)

face_process = threading.Thread(target=follow_face).start() 
mouth_process = threading.Thread(target=speech_rec).start() 