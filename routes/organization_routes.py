from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models import Organization, User
from middleware import admin_required

organization_bp = Blueprint('organization', __name__)

@organization_bp.route('/', methods=['POST'])
def create_organization():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Organization name is required'}), 400
    
    organization = Organization(name=data['name'], description=data.get('description'))
    db.session.add(organization)
    db.session.commit()
    return jsonify({'message': 'Organization created successfully', 'organization': {'id': organization.id, 'name': organization.name}}), 201

@organization_bp.route('/', methods=['GET'])
@jwt_required()
def get_organizations():
    organizations = Organization.query.all()
    return jsonify({'organizations': [{'id': org.id, 'name': org.name, 'description': org.description} for org in organizations]}), 200

@organization_bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    return jsonify({'id': organization.id, 'name': organization.name, 'description': organization.description}), 200

@organization_bp.route('/<int:org_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    if 'name' in data:
        organization.name = data['name']
    if 'description' in data:
        organization.description = data['description']
    
    db.session.commit()
    return jsonify({'message': 'Organization updated successfully', 'organization': {'id': organization.id, 'name': organization.name, 'description': organization.description}}), 200

@organization_bp.route('/<int:org_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    db.session.delete(organization)
    db.session.commit()
    return jsonify({'message': 'Organization deleted successfully'}), 200
