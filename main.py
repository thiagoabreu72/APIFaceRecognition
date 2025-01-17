from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
from PIL import Image
import io
import face_recognition
import os
from typing import List
# uvicorn main:app --reload


class ImgComp(BaseModel):
    img1: str
    img2: str
class ImgCad(BaseModel):
    img: str
    name: str 
    cpf: str
class ImgRec(BaseModel):
    img: str

app = FastAPI()
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


known_faces = []
@app.post("/CadastroImagem")
async def CadastroImagem(images: List[ImgCad]):
    
    for image in images:
        lista = []
        img = base64.b64decode(image.img)
        imag = Image.open(io.BytesIO(img))
        imag.convert('RGB')
        imag.save(f"{image.name}.jpg")
        img2 = cv2.imread(f"{image.name}.jpg")
        rgb_img = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        img_encoding = face_recognition.face_encodings(rgb_img)[0]
        os.remove(f"{image.name}.jpg")
        lista.append(image.name)
        lista.append(image.cpf)
        lista.append(img_encoding)
        # print(lista)
        known_faces.append(lista)
    # print(known_faces)
    # print(len(known_faces))
  


    return {"message": "Imagem cadastrada com sucesso"}

@app.post("/Reconhecimento")
async def Reconhecimento(image: ImgRec):
    imgRec = base64.b64decode(image.img)
    imagRec = Image.open(io.BytesIO(imgRec))
    imagRec.convert('RGB')
    imagRec.save("imagem.jpg")
    img2Rec = cv2.imread("imagem.jpg")
    rgb_img2Rec = cv2.cvtColor(img2Rec, cv2.COLOR_BGR2RGB)
    img_encoding2Rec = face_recognition.face_encodings(rgb_img2Rec)[0]
    os.remove("imagem.jpg")
    if(len(known_faces)==0):
        return {"message": "Nao há pessoas cadastradas"}
    i=0
    # print(known_faces)
    while(i<len(known_faces)):
        result = face_recognition.compare_faces([known_faces[i][2]], img_encoding2Rec)
        if(result[0]):
            return {"message": "Pessoa encontrada",
                    "name": known_faces[i][0],
                    "cpf": known_faces[i][1],
                    } 
            
        
        i+=1
    if not result[0]:
        return {"message": "Pessoa não encontrada"}

@app.post("/ComparaImagens")
async def ComparaImagens(image: ImgComp):
    img = base64.b64decode(image.img1)
    imag = Image.open(io.BytesIO(img))
    imag.convert('RGB')
    imag.save("img1.jpg")
    img2 = cv2.imread("img1.jpg")
    rgb_img = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    img_encoding = face_recognition.face_encodings(rgb_img)[0]
    os.remove("img1.jpg")

    img3 = base64.b64decode(image.img2)
    imag2 = Image.open(io.BytesIO(img3))
    imag2.convert('RGB')
    imag2.save("img2.jpg")
    img4 = cv2.imread("img2.jpg")
    rgb_img2 = cv2.cvtColor(img4, cv2.COLOR_BGR2RGB)
    img_encoding2 = face_recognition.face_encodings(rgb_img2)[0]
    os.remove("img2.jpg")

    result = face_recognition.compare_faces([img_encoding], img_encoding2)
    if(result[0]):
        return {"message": "Mesma pessoa"}
    else:
        return {"message": "Não é a mesma pessoa"}