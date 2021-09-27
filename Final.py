import streamlit as st
import face_recognition
import cv2
import math
import requests
import os
from PIL import Image
from skimage import io

data = requests.get("https://mobilegateway.glcar.ma/glcarapp/test.php")
d = data.json()
url = "https://scontent.glcar.ma/grc/suspects/"

KNOWN_FACES_DIR = 'known_Cropped_imgs'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'cnn'

# print('Loading known faces...')
known_faces = []
known_names = []
unknown_names = []
per = []
List = []

#new_path = 'C:/Users/Achraf/PycharmProjects/Face_id webcum/known_Cropped_imgs/'
new_path = 'known_Cropped_imgs/'


def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8print('Loading known faces...')
    color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
    return color


f = open("DataNumber.txt", "r")
Number = int(f.read())

if (len(d) - Number) > 0:
    n = len(d) - Number

    def save(img, name):
        try:
            imgSave = img
            cv2.imwrite(name, imgSave)
        except:
            pass


    def faces():
        f = []
        for dt in reversed(d):
            f.append(dt["PhotoSuspect"])
        try:
            for i in range(n):
                if f[i] != "":
                    img = io.imread("https://scontent.glcar.ma/grc/suspects/" + f[i])
                    save(img, new_path + f[i])
                    print("done saving")
        except:
            pass


    f = open("DataNumber.txt", "w")
    f.write(str(len(d)))
    f.close()
    faces()


def main():
    """Face ID"""
    # st.title("Face ID")

    # global list, idx, l, results, match

    global results, match
    html_temp = """
    <body style="background-color:red;">
    <div style="background-color:teal ;padding:10px;">
    <h2 style="color:white;text-align:center;">Face ID</h2>
    </div>

    </body>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    user_input = st.text_input("enter the full path of the image using '/' ", "")
    image_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if image_file is not None:
        our_image = Image.open(image_file)
        st.text("Original Image")
        st.image(our_image,
                 width=400, )

    if st.button("Scan Image"):
        if user_input == "":
            st.warning("Please enter image path")
        elif image_file is None:
            st.warning("Please select an image")
        else:
            for name in os.listdir(KNOWN_FACES_DIR):
                try:
                    image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}')
                    encoding = face_recognition.face_encodings(image)[0]
                    known_faces.append(encoding)
                    known_names.append(name)
                except:
                    pass

            image = face_recognition.load_image_file(f'{user_input}/{image_file.name}')
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            for face_encoding, face_location in zip(encodings, locations):
                results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
                face_distance = face_recognition.face_distance(known_faces, face_encoding)
                match = None
                if True in results:
                    match = known_names[results.index(True)]
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])
                    color = name_to_color(match)
                    cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 22)
                    print(top_left)
                    print(bottom_right)
                    for i, f in enumerate(face_distance):
                        if f > TOLERANCE:
                            range = (1.0 - TOLERANCE)
                            linear_val = (1.0 - f) / (range * 2.0)
                            l = linear_val * 100
                            # st.write("{:.2f}".format(l))
                            per.append("{:.2f}".format(l))
                        else:
                            range = TOLERANCE
                            linear_val = 1.0 - (f / (range * 2.0))
                            l = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
                            # st.write("{:.2f}".format(l))
                            per.append("{:.2f}".format(l))

            # if match == None:
            # st.info("No similar face found")

            # else:
            st.info("Resultat")
            for i, r in enumerate(results):
                if results[i] == True:
                    if per[i] >= "90.00":
                        List.append(known_names[i])
                        st.write("Pourcentage de similarity : " + per[i] + "%")

            if len(List):
                for b, i in enumerate(d):
                    for f, n in enumerate(List):
                        if List[f] == d[b]["PhotoSuspect"]:
                            st.write("Nom de suspect : " + d[b]["NomSuspect"])
                            st.write("Prenom de suspect : " + d[b]["PrenomSuspect"])
                            st.write("CIN Suspect : " + d[b]["CINSuspect"])
                            st.image(
                                url + List[f],
                                width=400,  # Manually Adjust the width of the image as per requirement
                            )
            else:
                st.info("No similar face found")


if __name__ == '__main__':
    main()
