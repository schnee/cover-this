import zipfile
from datetime import datetime
import pytz
import fsspec
from st_files_connection import FilesConnection
import streamlit as st


def zip_it(type, spec, resume, content):

    now = datetime.now(tz=pytz.utc)
    ymd = now.strftime("%Y%m%d")

    # determine the filesystem type
    fstype = st.secrets["fstype"]
    if fstype == "S3":
        conn = st.experimental_connection("s3", type=FilesConnection)
        fs = conn.fs
    else:
        fs = fsspec.filesystem('file')
    
    # Create storage dir if needed
    if not fs.exists(f'mahkr-sessions/{ymd}'):
        fs.makedirs(f'mahkr-sessions/{ymd}')

   
    timestamp = now.strftime("%Y%m%d%H%M%S")

    basename = f"{type}_{timestamp}"

    zip_name = f"mahkr-sessions/{ymd}/{basename}.zip"

    with fs.open(zip_name, 'wb') as zip_file:
        with zipfile.ZipFile(zip_file, mode='w') as zip_file:
            zip_file.writestr("job_spec.txt", spec, compress_type=zipfile.ZIP_DEFLATED) 
            zip_file.writestr("resume.pdf", resume, compress_type=zipfile.ZIP_DEFLATED) 
            zip_file.writestr("content.txt", content, compress_type=zipfile.ZIP_DEFLATED) 

    return basename

