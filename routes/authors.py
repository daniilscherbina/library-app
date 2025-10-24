from flask import Blueprint, request, jsonify
from models.base import db
from models.author import Author

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([author.to_dict() for author in authors])

@authors_bp.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify(author.to_dict())

@authors_bp.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    
    author = Author(
        first_name=data['first_name'],
        last_name=data['last_name'],
        biography=data.get('biography'),
        birth_date=data.get('birth_date')
    )
    
    db.session.add(author)
    db.session.commit()
    
    return jsonify(author.to_dict()), 201
