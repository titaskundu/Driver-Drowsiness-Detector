from flask import Flask,render_template,Response
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)
color = (255, 0, 255)
plotY = LivePlot(640, 360, [20, 50], invert=True)
app=Flask(__name__)


idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
ratioList = []
blinkCounter = 0
counter = 0


def generate_frames():
    color = (255, 0, 255)
    idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
    ratioList = []
    blinkCounter = 0
    counter = 0
    while True:
            
        ## read the camera frame
        success,frame=cap.read()
        if not success:
            break
        else:

            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            success, img = cap.read()
            img, faces = detector.findFaceMesh(img, draw=False)

            if faces:
                face = faces[0]
                for id in idList:
                    cv2.circle(img, face[id], 5,color, cv2.FILLED)

                leftUp = face[159]
                leftDown = face[23]
                leftLeft = face[130]
                leftRight = face[243]
                lenghtVer, _ = detector.findDistance(leftUp, leftDown)
                lenghtHor, _ = detector.findDistance(leftLeft, leftRight)

                cv2.line(img, leftUp, leftDown, (0, 200, 0), 3)
                cv2.line(img, leftLeft, leftRight, (0, 200, 0), 3)

                ratio = int((lenghtVer / lenghtHor) * 100)
                ratioList.append(ratio)
                if len(ratioList) > 3:
                    ratioList.pop(0)
                ratioAvg = sum(ratioList) / len(ratioList)

                if ratioAvg >= 35:
                    blinkCounter=0

                if ratioAvg < 35 :
                    blinkCounter += 1
                    color = (0,200,0)
                    if blinkCounter>60:
                        cvzone.putTextRect(img, f'Sleeping', (50, 100),
                                        colorR=color)



                # cvzone.putTextRect(img, f'Blink Count: {ratioAvg}', (0, 100),
                #                    colorR=color)

                imgPlot = plotY.update(ratioAvg, color)
                img = cv2.resize(img, (640, 360))
                frame = cvzone.stackImages([img, imgPlot], 1, 1)
            else:
                img = cv2.resize(img, (640, 360))
                frame = cvzone.stackImages([img, img], 1, 1)

            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(host="0.0.0.0",port =5000)