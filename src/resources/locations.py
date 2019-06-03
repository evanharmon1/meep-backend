from flask import Blueprint, request
from flask_restful import Api, Resource, fields
from .base import BaseAPI, BaseListAPI
from src.models import db, Project, ProjectType, Location


api_locations_blueprint = Blueprint('api_locations', __name__)
api = Api(api_locations_blueprint)

'''
defining a list api resource entails subclassing BaseListAPI and referring
to the base API resource it is built on
'''


class LocationAPI(BaseAPI):
    model = Location
    output_fields = {
        'id': fields.String(),
        'address': fields.String,
        'city': fields.String,
        'state': fields.String,
        'zipCode': fields.Integer(attribute='zip_code'),
        'latitude': fields.Float,
        'longitude': fields.Float
    }


api.add_resource(LocationAPI, '/locations/<int:id>', endpoint='location')


class LocationListAPI(BaseListAPI):
    base = LocationAPI

    def get(self):
        """ Overrides inherited get method from BaseListAPI in order to implement
        query string parameters
        """
        # query string parameters
        min_year = request.args.get('min-year')
        max_year = request.args.get('max-year')
        project_types = request.args.getlist('project-type')

        if not request.args:  # if no query string parameters provided
            # return all locations
            locs = [loc.json for loc in Project.query.all()]
            return {'locations': locs}

        # some query parameter was passed, so join project type, project, and
        # location tables, and filter based on non null queries
        q = db.session.query(ProjectType, Project, Location)\
            .filter(ProjectType.id == Project.project_type_id)\
            .filter(Project.id == Location.project_id)

        if min_year is not None:
            q = q.filter(Project.year >= min_year)

        if max_year is not None:
            q = q.filter(Project.year <= max_year)

        if project_types:
            q = q.filter(ProjectType.type_name.in_(project_types))

        # only return location data, even though projects and project types
        # were used in the query
        locs = [loc.json for (type, proj, loc) in q]
        return {'locations': locs}


api.add_resource(LocationListAPI, '/locations', '/locations/')


class LocationProjectAPI(Resource):
    """Given a location, return the associated project"""
    def get(self, id):
        location = Location.query.get(id)
        return location.project.json


api.add_resource(LocationProjectAPI, '/locations/<int:id>/project', endpoint='location_project')
