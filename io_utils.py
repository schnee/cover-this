import zipfile
from datetime import datetime
import fsspec

def zip_it(type, spec, resume, content):


    fs = fsspec.filesystem('file')
  # Create storage dir if needed
    if not fs.exists('storage'):
        fs.makedirs('storage')

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    zip_name = f"./storage/{type}_{timestamp}.zip"

    with fs.open(zip_name, 'wb') as zip_file:
        with zipfile.ZipFile(zip_file, mode='w', ) as zip_file:
            zip_file.writestr("job_spec.txt", spec) 
            zip_file.writestr("resume.pdf", resume)  
            zip_file.writestr("content.txt", content)

    return zip_name

