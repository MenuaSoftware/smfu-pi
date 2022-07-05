from flask_restful import Resource
from webargs.flaskparser import use_kwargs
from webargs import fields
from label_api.barcodeReader import *


class Label(Resource):
    labels = []
    label_id = 0

    @use_kwargs({'l_id': fields.Int(required=False)}, location="query")
    def get(self, l_id=None):
        if l_id is None:
            return {'labels': Label.labels}
        if l_id>=0 and l_id<len(Label.labels):
            return {'label': Label.labels[l_id]}, 200
        return {'status':'Label not found'}, 400

    @use_kwargs({'data': fields.List(fields.Field,required=True)},location="json")
    def post(self,data):
        #create labled -> give id to getBarcode
        date = datetime.datetime.now()
        dict = {"labeled_json": data, "labeled_date": date}
        _id = labeled.insert_one(dict).inserted_id
        print(_id)

        Label.labels = []
        Label.labels = getBarcode(data,_id)
        #bewerkingen
        return  {'status':'Labels created'}, 201

def init_api(api):
    api.add_resource(Label, "/label")