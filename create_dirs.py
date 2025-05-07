import os

def create_upload_dirs():
    # Base uploads directory
    base_dir = 'app/static/uploads'
    
    # List of required subdirectories
    subdirs = [
        'graduation_certificate',
        'birth_certificate',
        'family_card',
        'report_card',
        'photo',
        'track_documents'
    ]
    
    # Create each directory
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
        print(f'Created directory: {dir_path}')

if __name__ == '__main__':
    create_upload_dirs()