# Gesys
Gesys is an evolving module that provides a high-level API for recognizing hand gestures using a webcam

# Get started
**Install gesys module**
```python
pip install gesys
```
**Run simple example**
```python
from Gesys.gesys import GesysStatic
import cv2

FPS = 10 # choose FPS
gs = GesysStatic(10) # create recognizer
cap = cv2.VideoCapture(0)

while True:
    # 1. get a frame from the camera
    _, frame = cap.read()

    # 2. recognize gesture
    gesture = gs.frame(frame) 
    
    # 3. print the gesture if it is not trash
    if(gesture != 'thrash'):
        print(gesture)

    cv2.imshow('w', frame)
    if(cv2.waitKey(1)>0):
        break
cv2.destroyAllWindows()

```
