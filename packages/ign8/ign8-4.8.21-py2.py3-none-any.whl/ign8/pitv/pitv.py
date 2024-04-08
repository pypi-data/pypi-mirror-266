import requests
import time
import os
import urllib3
import redis
from PIL import Image
import subprocess
import hashlib
import hvac


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
r=redis.Redis()
vaulturl = os.getenv("VAULT_URL", "https://vault.openknowit.com")
vaulttoken = os.getenv("VAULT_TOKEN", "s.1J8Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1")

vault = hvac.Client(url=vaulturl, token=vaulttoken)


def init_redis():
  r = redis.Redis()
  r.set('foo', 'bar')
  value = r.get('foo')
  if value == b'bar':
    print("Redis is working")
    return r
  else:
    print("Redis is not working")
    exit(1)

pitvurl = os.getenv("pitv_URL", "https://pitvapi.openknowit.com")  

def status():
  print(pitvurl)

def service():
  print("service")


def registerallsystemfiles():
#   rpm -qa --filesbypkg
  mycmd = "rpm -qa --filesbypkg"
  mycmd = mycmd.split()
  p = subprocess.Popen(mycmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  out = out.decode("utf-8")
  lines = out.splitlines()
  count = len(lines)
  for line in lines:
    line = line.split()
    package = line[0]
    file = line[1]
    rediskey = "sytemfile:" + file
    r.set(rediskey, str(time.time()))
    print_line_and_return("%-016d" % count)
    #print_line_and_return("Registering system file: " + file)
    count = count - 1
   




def calculate_md5(filename, block_size=65536):
    if os.path.isfile(filename):
      print_line_and_return("Calculating md5 for file: " + filename)
      md5_hash = hashlib.md5()
      try:
        with open(filename, "rb") as file:
          for block in iter(lambda: file.read(block_size), b""):
            md5_hash.update(block)
        return md5_hash.hexdigest()
      except:
        return None
    else:
      return None


def hashit(file):
   #read file in binary mode
    with open(file, 'rb') as f:
        data = f.read()
        #return md5 hash
        data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

def check_if_file_is_picture(file):
  print_line_and_return("check if file is a picture")
  file = file.lower()
  if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".gif") or file.endswith(".bmp") or file.endswith(".tiff") or file.endswith(".tif") or file.endswith(".webp") or file.endswith("cr2"):
    
    return True
  else:
    return False

def get_image_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            metadata = img.info
            if len(metadata) > 0:
              return metadata
            else:
              return None
    except Exception as e:
        print_line_and_return("Error:")
        return None

def list_files_recursive(directory):
    files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "rb"):
                    files.append(file_path)
            except PermissionError:
                print_line_and_return("Permission denied for file:", file_path)
    return files

def print_line_and_return(text):
    terminal_width = os.get_terminal_size().columns
    text = text.ljust(terminal_width - 1)

    print(text, end='\r')


def locate_files(keyword=""):
    try:
        # Run the locate command and capture the output
        command = ["locate", keyword]
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
        output = result.stdout
        file_list = output.splitlines()
        return file_list
    except subprocess.CalledProcessError as e:
        print_line_and_return("Error:", e)
        return []

def evacuate():
  registerallsystemfiles()
  redis = init_redis()
  #get all files on the system
  files = locate_files()
  total = len(files)
  count = 0
  for file in files:
    count = count + 1
    if redis.exists(file):
      # get file size
      try:
        filesize = os.path.getsize(file)
      except:
        filesize = 0
        
      status = redis.get(file).decode("utf-8")
      # print a status wihout newline
      
      line = "file " + str(count) + " of " + str(total) + " status: " + status
      print_line_and_return(line)
      rediskey = "sytemfile:" + file
      
      if redis.exists(rediskey):
         next
      else:
         print_line_and_return("Registering non system file file: " + file)
         

      md5 = calculate_md5(file)
      # scp file remotehost:/files/
      if md5 is not None: 
        keys = "MD5:" + md5
        #i#vault.secrets.kv.v2.existing_version(keys)
        #if vault.secrets.kv.v2.get_secret_version(keys) is None:
        #  vault.secrets.kv.v2.create_or_update_secret(keys, md5=md5, file=file)
        
        redis.set(keys, filesize)

      if status == "1":
        metadata = get_image_metadata(file)
        if metadata is not None:
           key = "metadata:" + file
           redis.set(key, str(metadata))
    else:
      print_line_and_return("file " + str(count) + " of " + str(total) + " status: unknown")
      if check_if_file_is_picture(file):
        print_line_and_return("file " + str(count) + " of " + str(total) + " status: picture")
        key = "Picture:" + file
        redis.set(file, "1")
      else:
        redis.set(file, "999")
      
    





#      if status == 0 or status == 
#        print("file " + str(count) + " of " + str(total) ) #no newline
#        if check_if_file_is_picture(file):
#          print(file)
#          key = "Picture:" + file
#         redis.set(file, "1")
#       else:
#         redis.set(file, "999")
#      if status == "1":
#        metadata = get_image_metadata(file)
#        print(metadata)
#      else:
#        redis.set(file, "0")
#  print("evacuate")
  #get all files on the system

  
