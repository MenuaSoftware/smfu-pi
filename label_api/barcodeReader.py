import io
import re
import os
from dotenv import load_dotenv
from pathlib import Path
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64
import fitz
import datetime
import pymongo
from label_api.error_log import *

dotenv_path = Path('label_api/passwd.env')
load_dotenv(dotenv_path=dotenv_path)
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
client = pymongo.MongoClient("mongodb+srv://admin:" + DATABASE_PASSWORD + "@menuasoftware.fkxp9.mongodb.net/test")
db = client["smfu-db"]
errorlog = db["errorlog"]
labeled = db["labeled"]

port = 465
MAIL_PASSOWRD = os.getenv('MAIL_PASSWORD')

context = ssl.create_default_context()
MAIL = os.getenv('MAIL')
REC_MAIL = "Menua_HVN@hotmail.com"

index = 1
zoom_x = 2.0
zoom_y = 2.0
mat = fitz.Matrix(zoom_x, zoom_y)
list_barcodes = []
list_errors = []


class convert2PNG:
    zoom_x = 2.0
    zoom_y = 2.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    saved_file = ""

    def __init__(self, filename):
        self.file = filename

    def convert(self):
        doc = fitz.open(stream=self.file, filetype="pdf")
        pix = doc[0].get_pixmap(matrix=self.mat)
        # pix.save("pdf_file.png")
        # self.saved_file = "pdf_file.png"
        imdata = pix.tobytes("png")
        np_ar = np.frombuffer(imdata, np.uint8)
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


def check_error(list):
    message = MIMEMultipart("alternative")
    message["Subject"] = "ERROR_LOG - 0 ERRORS"
    message["From"] = MAIL
    message["To"] = REC_MAIL
    if (len(list) == 0):
        html = """\
                    <html>
                      <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                        <title>Simple Transactional Email</title>
                        <style>
                          /* -------------------------------------
                              GLOBAL RESETS
                          ------------------------------------- */

                          /*All the styling goes here*/

                          img {
                            border: none;
                            -ms-interpolation-mode: bicubic;
                            max-width: 100%; 
                          }

                          body {
                            background-color: #f6f6f6;
                            font-family: sans-serif;
                            -webkit-font-smoothing: antialiased;
                            font-size: 14px;
                            line-height: 1.4;
                            margin: 0;
                            padding: 0;
                            -ms-text-size-adjust: 100%;
                            -webkit-text-size-adjust: 100%; 
                          }

                          table {
                            border-collapse: separate;
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            width: 100%; }
                            table td {
                              font-family: sans-serif;
                              font-size: 14px;
                              vertical-align: top; 
                          }

                          /* -------------------------------------
                              BODY & CONTAINER
                          ------------------------------------- */

                          .body {
                            background-color: #f6f6f6;
                            width: 100%; 
                          }

                          /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
                          .container {
                            display: block;
                            margin: 0 auto !important;
                            /* makes it centered */
                            max-width: 580px;
                            padding: 10px;
                            width: 580px; 
                          }

                          /* This should also be a block element, so that it will fill 100% of the .container */
                          .content {
                            box-sizing: border-box;
                            display: block;
                            margin: 0 auto;
                            max-width: 580px;
                            padding: 10px; 
                          }

                          /* -------------------------------------
                              HEADER, FOOTER, MAIN
                          ------------------------------------- */
                          .main {
                            background: #ffffff;
                            border-radius: 3px;
                            width: 100%; 
                          }

                          .wrapper {
                            box-sizing: border-box;
                            padding: 20px; 
                          }

                          .content-block {
                            padding-bottom: 10px;
                            padding-top: 10px;
                          }

                          .footer {
                            clear: both;
                            margin-top: 10px;
                            text-align: center;
                            width: 100%; 
                          }
                            .footer td,
                            .footer p,
                            .footer span,
                            .footer a {
                              color: #999999;
                              font-size: 12px;
                              text-align: center; 
                          }

                          /* -------------------------------------
                              TYPOGRAPHY
                          ------------------------------------- */
                          h1,
                          h2,
                          h3,
                          h4 {
                            color: #000000;
                            font-family: sans-serif;
                            font-weight: 400;
                            line-height: 1.4;
                            margin: 0;
                            margin-bottom: 30px; 
                          }

                          h1 {
                            font-size: 35px;
                            font-weight: 300;
                            text-align: center;
                            text-transform: capitalize; 
                          }

                          p,
                          ul,
                          ol {
                            font-family: sans-serif;
                            font-size: 14px;
                            font-weight: normal;
                            margin: 0;
                            margin-bottom: 15px; 
                          }
                            p li,
                            ul li,
                            ol li {
                              list-style-position: inside;
                              margin-left: 5px; 
                          }

                          a {
                            color: #3498db;
                            text-decoration: underline; 
                          }

                          /* -------------------------------------
                              BUTTONS
                          ------------------------------------- */
                          .btn {
                            box-sizing: border-box;
                            width: 100%; }
                            .btn > tbody > tr > td {
                              padding-bottom: 15px; }
                            .btn table {
                              width: auto; 
                          }
                            .btn table td {
                              background-color: #ffffff;
                              border-radius: 5px;
                              text-align: center; 
                          }
                            .btn a {
                              background-color: #ffffff;
                              border: solid 1px #3498db;
                              border-radius: 5px;
                              box-sizing: border-box;
                              color: #3498db;
                              cursor: pointer;
                              display: inline-block;
                              font-size: 14px;
                              font-weight: bold;
                              margin: 0;
                              padding: 12px 25px;
                              text-decoration: none;
                              text-transform: capitalize; 
                          }

                          .btn-primary table td {
                            background-color: #3498db; 
                          }

                          .btn-primary a {
                            background-color: #3498db;
                            border-color: #3498db;
                            color: #ffffff; 
                          }

                          /* -------------------------------------
                              OTHER STYLES THAT MIGHT BE USEFUL
                          ------------------------------------- */
                          .last {
                            margin-bottom: 0; 
                          }

                          .first {
                            margin-top: 0; 
                          }

                          .align-center {
                            text-align: center; 
                          }

                          .align-right {
                            text-align: right; 
                          }

                          .align-left {
                            text-align: left; 
                          }

                          .clear {
                            clear: both; 
                          }

                          .mt0 {
                            margin-top: 0; 
                          }

                          .mb0 {
                            margin-bottom: 0; 
                          }

                          .preheader {
                            color: transparent;
                            display: none;
                            height: 0;
                            max-height: 0;
                            max-width: 0;
                            opacity: 0;
                            overflow: hidden;
                            mso-hide: all;
                            visibility: hidden;
                            width: 0; 
                          }

                          .powered-by a {
                            text-decoration: none; 
                          }

                          hr {
                            border: 0;
                            border-bottom: 1px solid #f6f6f6;
                            margin: 20px 0; 
                          }

                          /* -------------------------------------
                              RESPONSIVE AND MOBILE FRIENDLY STYLES
                          ------------------------------------- */
                          @media only screen and (max-width: 620px) {
                            table.body h1 {
                              font-size: 28px !important;
                              margin-bottom: 10px !important; 
                            }
                            table.body p,
                            table.body ul,
                            table.body ol,
                            table.body td,
                            table.body span,
                            table.body a {
                              font-size: 16px !important; 
                            }
                            table.body .wrapper,
                            table.body .article {
                              padding: 10px !important; 
                            }
                            table.body .content {
                              padding: 0 !important; 
                            }
                            table.body .container {
                              padding: 0 !important;
                              width: 100% !important; 
                            }
                            table.body .main {
                              border-left-width: 0 !important;
                              border-radius: 0 !important;
                              border-right-width: 0 !important; 
                            }
                            table.body .btn table {
                              width: 100% !important; 
                            }
                            table.body .btn a {
                              width: 100% !important; 
                            }
                            table.body .img-responsive {
                              height: auto !important;
                              max-width: 100% !important;
                              width: auto !important; 
                            }
                          }

                          /* -------------------------------------
                              PRESERVE THESE STYLES IN THE HEAD
                          ------------------------------------- */
                          @media all {
                            .ExternalClass {
                              width: 100%; 
                            }
                            .ExternalClass,
                            .ExternalClass p,
                            .ExternalClass span,
                            .ExternalClass font,
                            .ExternalClass td,
                            .ExternalClass div {
                              line-height: 100%; 
                            }
                            .apple-link a {
                              color: inherit !important;
                              font-family: inherit !important;
                              font-size: inherit !important;
                              font-weight: inherit !important;
                              line-height: inherit !important;
                              text-decoration: none !important; 
                            }
                            #MessageViewBody a {
                              color: inherit;
                              text-decoration: none;
                              font-size: inherit;
                              font-family: inherit;
                              font-weight: inherit;
                              line-height: inherit;
                            }
                            .btn-primary table td:hover {
                              background-color: #34495e !important; 
                            }
                            .btn-primary a:hover {
                              background-color: #34495e !important;
                              border-color: #34495e !important; 
                            } 
                          }

                        </style>
                      </head>
                      <body>
                        <span class="preheader">Smart fulfilment | </span>
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
                          <tr>
                            <td>&nbsp;</td>
                            <td class="container">
                              <div class="content">

                                <!-- START CENTERED WHITE CONTAINER -->
                                <table role="presentation" class="main">

                                  <!-- START MAIN CONTENT AREA -->
                                  <tr>
                                    <td class="wrapper">
                                      <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                          <td>
                                            <p>NO ERRORS OCCURED</p>
                                          </td>
                                        </tr>
                                      </table>
                                    </td>
                                  </tr>

                                <!-- END MAIN CONTENT AREA -->
                                </table>
                                <!-- END CENTERED WHITE CONTAINER -->

                                <!-- START FOOTER -->
                                <div class="footer">
                                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                    <tr>
                                      <td class="content-block">
                                        <span class="apple-link">Smart Fulfilment | MenuaSoftware</span>
                                      </td>
                                    </tr>
                                  </table>
                                </div>
                                <!-- END FOOTER -->

                              </div>
                            </td>
                            <td>&nbsp;</td>
                          </tr>
                        </table>
                      </body>
                    </html>
                    """
        part2 = MIMEText(html, "html")
        message.attach(part2)
        with smtplib.SMTP_SSL("mail.menua.be", port, context=context) as server:
            server.login(MAIL, MAIL_PASSOWRD)
            server.sendmail(MAIL, REC_MAIL, message.as_string())
    else:
        len_errors = len(list_errors)
        message["Subject"] = "ERROR_LOG - " + str(len_errors) + " ERRORS"
        message["From"] = MAIL
        message["To"] = REC_MAIL
        head = """<html>
          <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Simple Transactional Email</title>
            <style>
              /* -------------------------------------
                  GLOBAL RESETS
              ------------------------------------- */

              /*All the styling goes here*/

              img {{
                border: none;
                -ms-interpolation-mode: bicubic;
                max-width: 100%; 
              }}

              body {{
                background-color: #f6f6f6;
                font-family: sans-serif;
                -webkit-font-smoothing: antialiased;
                font-size: 14px;
                line-height: 1.4;
                margin: 0;
                padding: 0;
                -ms-text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%; 
              }}

              table {{
                border-collapse: separate;
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                width: 100%; }}
                table td {{
                  font-family: sans-serif;
                  font-size: 14px;
                  vertical-align: top; 
              }}
              
              /* Solid border */
                hr.solid {{
                border-top: 3px solid #bbb;
                padding-top: 1px;
                }}

              /* -------------------------------------
                  BODY & CONTAINER
              ------------------------------------- */

              .body {{
                background-color: #f6f6f6;
                width: 100%; 
              }}

              /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
              .container {{
                display: block;
                margin: 0 auto !important;
                /* makes it centered */
                max-width: 580px;
                padding: 10px;
                width: 580px; 
              }}

              /* This should also be a block element, so that it will fill 100% of the .container */
              .content {{
                box-sizing: border-box;
                display: block;
                margin: 0 auto;
                max-width: 580px;
                padding: 10px; 
              }}

              /* -------------------------------------
                  HEADER, FOOTER, MAIN
              ------------------------------------- */
              .main {{
                background: #ffffff;
                border-radius: 3px;
                width: 100%; 
              }}

              .wrapper {{
                box-sizing: border-box;
                padding: 20px; 
              }}

              .content-block {{
                padding-bottom: 10px;
                padding-top: 10px;
              }}

              .footer {{
                clear: both;
                margin-top: 10px;
                text-align: center;
                width: 100%; 
              }}
                .footer td,
                .footer p,
                .footer span,
                .footer a {{
                  color: #999999;
                  font-size: 12px;
                  text-align: center; 
              }}

              /* -------------------------------------
                  TYPOGRAPHY
              ------------------------------------- */
              h1,
              h2,
              h3,
              h4 {{
                color: #000000;
                font-family: sans-serif;
                font-weight: 400;
                line-height: 1.4;
                margin: 0;
                margin-bottom: 30px; 
              }}

              h1 {{
                font-size: 35px;
                font-weight: 300;
                text-align: center;
                text-transform: capitalize; 
              }}

              p,
              ul,
              ol {{
                font-family: sans-serif;
                font-size: 14px;
                font-weight: normal;
                margin: 0;
                margin-bottom: 15px; 
              }}
                p li,
                ul li,
                ol li {{
                  list-style-position: inside;
                  margin-left: 5px; 
              }}

              a {{
                color: #3498db;
                text-decoration: underline; 
              }}

              /* -------------------------------------
                  BUTTONS
              ------------------------------------- */
              .btn {{
                box-sizing: border-box;
                width: 100%; }}
                .btn > tbody > tr > td {{
                  padding-bottom: 15px; }}
                .btn table {{
                  width: auto; 
              }}
                .btn table td {{
                  background-color: #ffffff;
                  border-radius: 5px;
                  text-align: center; 
              }}
                .btn a {{
                  background-color: #ffffff;
                  border: solid 1px #3498db;
                  border-radius: 5px;
                  box-sizing: border-box;
                  color: #3498db;
                  cursor: pointer;
                  display: inline-block;
                  font-size: 14px;
                  font-weight: bold;
                  margin: 0;
                  padding: 12px 25px;
                  text-decoration: none;
                  text-transform: capitalize; 
              }}

              .btn-primary table td {{
                background-color: #3498db; 
              }}

              .btn-primary a {{
                background-color: #3498db;
                border-color: #3498db;
                color: #ffffff; 
              }}

              /* -------------------------------------
                  OTHER STYLES THAT MIGHT BE USEFUL
              ------------------------------------- */
              .last {{
                margin-bottom: 0; 
              }}

              .first {{
                margin-top: 0; 
              }}

              .align-center {{
                text-align: center; 
              }}

              .align-right {{
                text-align: right; 
              }}

              .align-left {{
                text-align: left; 
              }}

              .clear {{
                clear: both; 
              }}

              .mt0 {{
                margin-top: 0; 
              }}

              .mb0 {{
                margin-bottom: 0; 
              }}

              .preheader {{
                color: transparent;
                display: none;
                height: 0;
                max-height: 0;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                mso-hide: all;
                visibility: hidden;
                width: 0; 
              }}

              .powered-by a {{
                text-decoration: none; 
              }}

              hr {{
                border: 0;
                border-bottom: 1px solid #f6f6f6;
                margin: 20px 0; 
              }}

              /* -------------------------------------
                  RESPONSIVE AND MOBILE FRIENDLY STYLES
              ------------------------------------- */
              @media only screen and (max-width: 620px) {{
                table.body h1 {{
                  font-size: 28px !important;
                  margin-bottom: 10px !important; 
                }}
                table.body p,
                table.body ul,
                table.body ol,
                table.body td,
                table.body span,
                table.body a {{
                  font-size: 16px !important; 
                }}
                table.body .wrapper,
                table.body .article {{
                  padding: 10px !important; 
                }}
                table.body .content {{
                  padding: 0 !important; 
                }}
                table.body .container {{
                  padding: 0 !important;
                  width: 100% !important; 
                }}
                table.body .main {{
                  border-left-width: 0 !important;
                  border-radius: 0 !important;
                  border-right-width: 0 !important; 
                }}
                table.body .btn table {{
                  width: 100% !important; 
                }}
                table.body .btn a {{
                  width: 100% !important; 
                }}
                table.body .img-responsive {{
                  height: auto !important;
                  max-width: 100% !important;
                  width: auto !important; 
                }}
              }}

              /* -------------------------------------
                  PRESERVE THESE STYLES IN THE HEAD
              ------------------------------------- */
              @media all {{
                .ExternalClass {{
                  width: 100%; 
                }}
                .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {{
                  line-height: 100%; 
                }}
                .apple-link a {{
                  color: inherit !important;
                  font-family: inherit !important;
                  font-size: inherit !important;
                  font-weight: inherit !important;
                  line-height: inherit !important;
                  text-decoration: none !important; 
                }}
                #MessageViewBody a {{
                  color: inherit;
                  text-decoration: none;
                  font-size: inherit;
                  font-family: inherit;
                  font-weight: inherit;
                  line-height: inherit;
                }}
                .btn-primary table td:hover {{
                  background-color: #34495e !important; 
                }}
                .btn-primary a:hover {{
                  background-color: #34495e !important;
                  border-color: #34495e !important; 
                }} 
              }}

            </style>
          </head>"""
        body1 = """\
          <body>
            <span class="preheader">Smart fulfilment | </span>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
              <tr>
                <td>&nbsp;</td>
                <td class="container">
                  <div class="content">

                    <!-- START CENTERED WHITE CONTAINER -->
                    <table role="presentation" class="main">

                      <!-- START MAIN CONTENT AREA -->
                      <tr>
                        <td class="wrapper">
                          <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td>
                                <p>{len_errors} ERRORS OCCURED</p>
                                
        """
        body2="""
                                <table>
        """
        for it in list_errors:
            body2 +="""
                                    <hr class="solid">
                                    <tr>
                                        <td>
                                            <table>
                                                <tr>
                                                    <td>errorlog_id: </td>
                                                    <td>{errorlog_id}</td>
                                                </tr>
                                                <tr>
                                                    <td>errorlog_date: </td>
                                                    <td>{errorlog_date}</td>
                                                </tr>
                                                <tr>
                                                    <td>errorlog_labeled_id: </td>
                                                    <td>{errorlog_labeled_id}</td>
                                                </tr>
                                            </table>
                                            <hr class="solid">
                                        </td>
                                    </tr>
                                    
            """.format(errorlog_id=it.errorlog_id,errorlog_date=it.errorlog_date,errorlog_labeled_id=it.errorlog_labeled_id)
        body2+="""
                                </table>
        """
        body3= """                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>

                    <!-- END MAIN CONTENT AREA -->
                    </table>
                    <!-- END CENTERED WHITE CONTAINER -->

                    <!-- START FOOTER -->
                    <div class="footer">
                      <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                          <td class="content-block">
                            <span class="apple-link">Smart Fulfilment | MenuaSoftware</span>
                          </td>
                        </tr>
                      </table>
                    </div>
                    <!-- END FOOTER -->

                  </div>
                </td>
                <td>&nbsp;</td>
              </tr>
            </table>
          </body>
        </html>"""
        html = head+body1+body2+body3
        html = html.format(len_errors=len_errors)
        part2 = MIMEText(html, "html")
        message.attach(part2)
        with smtplib.SMTP_SSL("mail.menua.be", port, context=context) as server:
            server.login(MAIL, MAIL_PASSOWRD)
            server.sendmail(MAIL, REC_MAIL, message.as_string())

def getBarcode(json_file, labeled_id):
    list = []
    global list_errors
    for i in json_file:
        ss = trimString(i["pdf"])
        try:
            pdf_file = io.BytesIO(base64.b64decode(str(ss)))
            bar_data = readBarcode(pdf_file)
            list.append(bar_data)
        except:
            # toevoegen ERRORLOG
            date = datetime.datetime.now()
            dict = {"errorlog_date": date, "errorlog_data": i, "errorlog_labeled_id": str(labeled_id)}
            _id = errorlog.insert_one(dict).inserted_id
            # toevoegen error list, om nadien te mailen
            errlog = Error_log(str(_id), date, i, labeled_id)
            list_errors.append(errlog)
    check_error(list_errors)
    list_errors = []

    return list
