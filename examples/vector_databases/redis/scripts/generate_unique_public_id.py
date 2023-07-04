import uuid

def generate_unique_public_id():
    # Generate a UUID (Universally Unique Identifier)
    unique_id = str(uuid.uuid4())

    # Remove hyphens from the UUID and return it as the PublicID
    public_id = unique_id.replace('-', '')

    return public_id