import os
env = f".\env\\Scripts\\"
os.system('py -m venv env')                         # Create Virtual enviroment
os.system(f"{env}pip install -r requirements.txt")  # Install requirements
os.system(f"{env}python manage.py runserver 0.0.0.0:8000")  # Run server
