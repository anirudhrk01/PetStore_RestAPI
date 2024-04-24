from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kenxinda@localhost/petstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_PORT'] = 3306  
db = SQLAlchemy(app)

# Defining aPet model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))

    def __repr__(self):
        return f"<Pet {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'status': self.status
        }

# Create the database tables if not exists
@app.before_request
def create_tables():
    if not hasattr(app, 'is_db_initialized'):
        db.create_all()
        app.is_db_initialized = True

# Endpoint to create a pet
@app.route('/pet', methods=['POST'])
def create_pet():
    data = request.json
    print("Received data:", data)  

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name')
    category = data.get('category')
    status = data.get('status')

    if not all((name, category, status)):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        pet = Pet(name=name, category=category, status=status)
        db.session.add(pet)
        db.session.commit()
        print("Pet created successfully:", pet)  
        return jsonify({'message': 'Pet created successfully', 'pet': pet.to_dict()}), 201
    except Exception as e:
        print("Error creating pet:", e)  
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


# Endpoint to get all pets
@app.route('/pet', methods=['GET'])
def get_all_pets():
    pets = Pet.query.all()
    pet_dicts = [pet.to_dict() for pet in pets]
    return jsonify({'pets': pet_dicts}), 200

# Endpoint to get a pet by id
@app.route('/pet/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    # pet = Pet.query.get(pet_id)
    pet = db.session.get(Pet, pet_id)

    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    return jsonify({'pet': pet.to_dict()})

# Endpoint to find pets by status
@app.route('/pet/findByStatus', methods=['GET'])
def find_pet_by_status():
    status = request.args.get('status')
    if not status:
        return jsonify({'error': 'Status parameter is missing'}), 400

    pets = Pet.query.filter_by(status=status).all()
    pet_dicts = [pet.to_dict() for pet in pets]
    return jsonify({'pets': pet_dicts}), 200

# Endpoint to update a pet
@app.route('/pet/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    data = request.json
    name = data.get('name', pet.name)
    category = data.get('category', pet.category)
    status = data.get('status', pet.status)

    pet.name = name
    pet.category = category
    pet.status = status

    db.session.commit()

    return jsonify({'message': 'Pet updated successfully', 'pet': pet.to_dict()})

# Endpoint to delete a pet
@app.route('/pet/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    db.session.delete(pet)
    db.session.commit()

    return jsonify({'message': 'Pet deleted successfully'})

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(Exception)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
