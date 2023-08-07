from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bootstrap import Bootstrap
import boto3
import uuid 
import os
from .filters import datetimeformat, file_type
from .config import S3_BUCKET, S3_KEY, S3_SECRET, SECRET_KEY, SQL_Host, SQL_User, SQL_Password, URI
from .main import main as app
from .models import Entry
from . import db

class aws_s3_url():
  def __init__(self):
    self.url = None
    self.last_modified = None


s3 = Blueprint('s3', __name__)


@s3.route('/files')
@login_required
def files():
    s3_resource = boto3.resource(
         's3',
         aws_access_key_id=S3_KEY,
         aws_secret_access_key= S3_SECRET
      )
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key= S3_SECRET
    )

    my_bucket = s3_resource.Bucket(S3_BUCKET)

    summaries = my_bucket.objects.all()

    # 
    # build list with entries of Tag { Key=user, Value = current.user }
    # 
    user_obj_list = []

    for entry in summaries:
        response = s3_client.get_object_tagging(
            Bucket=S3_BUCKET,
            Key=entry.key
        )
        Tag = response["TagSet"]
        for KeyValue in Tag:
            if KeyValue["Key"] == "user":
                if KeyValue["Value"] == current_user.name:

                        entry_list=aws_s3_url()
                        entry_list.last_modified = entry.last_modified
                        entry_list.url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET,
                                                            'Key': entry.key},
                                                    ExpiresIn=900)
                        
                        print(f'appending {entry_list.url}, last_modified {entry_list.last_modified} ')
                        user_obj_list.append(entry_list)


    return render_template('files.html', my_bucket=my_bucket, files=user_obj_list)

@s3.route('/upload')
@login_required
def upload():
    s3_resource = boto3.resource('s3',aws_access_key_id=S3_KEY,aws_secret_access_key= S3_SECRET)
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    return render_template('upload.html',my_bucket=my_bucket)

@s3.route('/upload', methods=['POST'])
def upload_post():
    file = request.files['file']
    
    dst_filename = str(uuid.uuid1()) + os.path.splitext(file.filename)[1]

    s3_resource = boto3.resource('s3',
      aws_access_key_id=S3_KEY,
      aws_secret_access_key=S3_SECRET
    )

    my_bucket = s3_resource.Bucket(S3_BUCKET)
    tag = 'user=' + current_user.name
    my_bucket.Object(dst_filename).put(Body=file,Tagging='user=' + current_user.name)

    flash('File uploaded successfully')
    
    url='https://' + S3_BUCKET + '.s3-ap-southeast-1.amazonaws.com/' + dst_filename
    new_entry = Entry(
                  name = current_user.name,
                  url = url,
                  origfilename = file.filename
                  )
    db.session.add(new_entry)
    db.session.commit()


    return redirect(url_for('s3.upload'))