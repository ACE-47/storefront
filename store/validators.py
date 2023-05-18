
from django.core.exceptions import ValidationError
def validate_file_size(file):
    max_kb =50 

    if file.size > max_kb * 1024:
        raise ValidationError(f'file cannot be larger than {max_kb}KB')