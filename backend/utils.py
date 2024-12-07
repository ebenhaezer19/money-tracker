import uuid


def generate_id() -> str:
    """
    Generate primary key for table entry using UUID
    """
    
    return str(uuid.uuid4())
