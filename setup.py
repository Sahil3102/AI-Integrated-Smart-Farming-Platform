#!/usr/bin/env python
"""
Setup script for Smart AI Agriculture Decision Platform
"""
import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {command}\n")
    
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed")
        return False
    print(f"\n✅ {description} completed successfully")
    return True


def main():
    """Main setup function"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     Smart AI Agriculture Decision Platform - Setup           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Change to project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'smart_agriculture')
    os.chdir(project_dir)
    print(f"✅ Working directory: {os.getcwd()}")
    
    # Install dependencies
    if not run_command(
        'pip install -r ../requirements.txt',
        "Installing dependencies"
    ):
        return False
    
    # Create .env file if it doesn't exist
    env_file = '../.env'
    env_example = '../.env.example'
    if not os.path.exists(env_file) and os.path.exists(env_example):
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("\n✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your database credentials")
    
    # Run migrations
    if not run_command(
        'python manage.py migrate',
        "Running database migrations"
    ):
        return False
    
    # Create superuser
    print("\n" + "="*60)
    print("Create Admin User")
    print("="*60)
    result = subprocess.run('python manage.py createsuperuser', shell=True)
    
    # Collect static files
    if not run_command(
        'python manage.py collectstatic --noinput',
        "Collecting static files"
    ):
        return False
    
    # Create media directories
    media_dirs = ['media', 'media/crops', 'media/avatars', 'media/disease_uploads', 'media/disease_detection']
    for dir_name in media_dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("\n✅ Created media directories")
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              Setup Completed Successfully!                   ║
    ║                                                              ║
    ║  To start the development server, run:                       ║
    ║                                                              ║
    ║      python manage.py runserver                              ║
    ║                                                              ║
    ║  Then access the application at:                             ║
    ║      http://127.0.0.1:8000/                                  ║
    ║                                                              ║
    ║  Admin panel: http://127.0.0.1:8000/admin/                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
