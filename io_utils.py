import zipfile
from datetime import datetime
import fsspec
from st_files_connection import FilesConnection
import streamlit as st


def zip_it(type, spec, resume, content):

    conn = st.experimental_connection("s3", type=FilesConnection)
    fs = conn.fs

    #fs = fsspec.filesystem('file')
  # Create storage dir if needed
    if not fs.exists('mahkr-sessions/storage'):
        fs.makedirs('mahkr-sessions/storage')

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    zip_name = f"mahkr-sessions/storage/{type}_{timestamp}.zip"

    with fs.open(zip_name, 'wb') as zip_file:
        with zipfile.ZipFile(zip_file, mode='w', ) as zip_file:
            zip_file.writestr("job_spec.txt", spec) 
            zip_file.writestr("resume.pdf", resume)  
            zip_file.writestr("content.txt", content)

    return zip_name

