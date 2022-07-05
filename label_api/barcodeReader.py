import io
import re
import os
from dotenv import load_dotenv
from pathlib import Path

import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64
import fitz
import datetime
import pymongo

dotenv_path = Path('label_api/passwd.env')
load_dotenv(dotenv_path=dotenv_path)
DATABASE_PASSWORD=os.getenv('DATABASE_PASSWORD')
client = pymongo.MongoClient("mongodb+srv://admin:" + DATABASE_PASSWORD +"@menuasoftware.fkxp9.mongodb.net/test")
db = client["smfu-db"]
errorlog = db["errorlog"]
labeled = db["labeled"]

index = 1
zoom_x = 2.0
zoom_y = 2.0
mat = fitz.Matrix(zoom_x, zoom_y)
list_barcodes = []

class convert2PNG:
    zoom_x = 2.0
    zoom_y = 2.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    saved_file = ""

    def __init__(self,filename):
        self.file = filename

    def convert(self):
        doc = fitz.open(stream=self.file,filetype="pdf")
        pix = doc[0].get_pixmap(matrix=self.mat)
        # pix.save("pdf_file.png")
        # self.saved_file = "pdf_file.png"
        imdata = pix.tobytes("png")
        np_ar = np.frombuffer(imdata,np.uint8)
        return np_ar


def readBarcode(pdf):
    cp = convert2PNG(pdf)
    image = cp.convert()
    # image = cp.saved_file

    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    detectedBarcodes = decode(img)
    if not detectedBarcodes:
        return None
    else:
        for barcode in detectedBarcodes:
            if barcode.data != "" and re.match("CODE*", barcode.type):
                brcd = barcode.data.decode("utf-8")
                return str(brcd)



def trimString(p_string):
    string = p_string[28:]
    return string

def getBarcode(json_file,labeled_id):
    list = []
    for i in json_file:
        ss = trimString(i["pdf"])
        try:
            pdf_file = io.BytesIO(base64.b64decode(str(ss)))
            bar_data = readBarcode(pdf_file)
            list.append(bar_data)
        except:
            #toevoegen ERRORLOG
            date = datetime.datetime.now()
            dict = {"errorlog_date": date,"errorlog_data": i,"errorlog_labeled_id": str(labeled_id)}
            _id = errorlog.insert_one(dict).inserted_id
    return list