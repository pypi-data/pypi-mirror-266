# import required libraries
import cv2
import os

# read the input image
 

class FaceCrop:
    def __init__(self, root_folder,destination_folder):
        # self.rootfolder = "../Samples/"
        self.rootfolder = root_folder
        self.destination_folder = destination_folder

    def generate(self):
        self.loadVideos()

 
    def crop_frame(self, frame, user_dir):
        img = frame 
        # convert to grayscale of each frames
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        eye_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_eye.xml")
        # read the haarcascade to detect the faces in an image
        face_cascade = cv2.CascadeClassifier(
            'haarcascades/haarcascade_frontalface_default.xml')

        # detects faces in the input image
        faces = face_cascade.detectMultiScale(gray, 1.3, 5, flags=cv2.CASCADE_SCALE_IMAGE)
        
        #print(user_dir)
        usernameFolder = user_dir.split("_")[0]
        usernameFile = user_dir.split("_")[1]
        #print(usernameFile+" File")

        # loop over all detected faces
        if len(faces) > 0:
            for i, (x, y, w, h) in enumerate(faces): 
                face = img[y:y + h, x:x + w]
                roi_gray = img[y:y + h, x:x + w]
                roi_color = img[y:y+h, x:x+w]
                
                eyes = eye_cascade.detectMultiScale(roi_gray)
                #print(f"Eyes Count{len(eyes)}")
                for (ex,ey,ew,eh) in eyes:
                    face = img[y:y + h, x:x + w]
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    if not os.path.exists(f"{self.destination_folder}/{usernameFolder}"): 
                        os.makedirs(f'{self.destination_folder}/{usernameFolder}', exist_ok=True)
                    #Save Images    
                    cv2.imwrite(
                        f'{self.destination_folder}/{usernameFolder}/{usernameFile}.jpg', face)  

    def loadVideos(self):
        #videorootfolder = "../Samples/Videos"
        videorootfolder = self.rootfolder
        for dir in os.listdir(videorootfolder):
            # set video file path of input video with name and extension
            print(f"{videorootfolder}/{dir}")
            vid = cv2.VideoCapture(f"{videorootfolder}/{dir}")
 
            # for frame identity
            index = 0
            while (True):
                # Extract images
                ret, frame = vid.read()
                # end of frames
                if not ret:
                    break
                 
                self.crop_frame(frame, f"{dir.split('.')[0]}_{index}")
                # next frame
                index += 1
