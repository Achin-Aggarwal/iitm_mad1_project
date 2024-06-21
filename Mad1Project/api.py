from flask_restful import Resource, Api
from app import app
from models import db, Section

api = Api(app)

class GetSection(Resource):
    def get(self):
        sections = Section.query.all()
        return {'sections': [ {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'create_date': section.create_date.isoformat()
        } for section in sections]
        }
        

api.add_resource(GetSection, '/api/section')


