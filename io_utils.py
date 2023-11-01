import zipfile
from datetime import datetime
import os

def zip_it(type, spec, resume, content):

  # Create storage dir if needed
  if not os.path.exists('storage'):
    os.makedirs('storage')

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    zip_name = f"./storage/{type}_{timestamp}.zip"

    with zipfile.ZipFile(zip_name, 'w') as zip_file:
        zip_file.writestr("job_spec.txt", spec) 
        zip_file.writestr("resume.pdf", resume)  
        zip_file.writestr("content.txt", content)

    return zip_name

