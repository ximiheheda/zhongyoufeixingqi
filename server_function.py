from urllib.request import urlopen
from urllib import request
from MultiPartForm import MultiPartForm

def audio_broadcast(ip, student_id, name):
    try:
        with urlopen(f"http://{ip}:5000/audio_broadcast/{student_id}/{name}") as response:
            response_content = response.read()
            print(response_content)
    except Exception as e:
        print(e)

def upload_crop_photo(ip, student_id, photo_name, photo_path):
    try:
        form = MultiPartForm()
        form.add_file('file', photo_name, fileHandle=open(photo_path, 'rb'))
        data = bytes(form)
        r = request.Request(f'http://{ip}:5000/crop_photo/{student_id}', data=data)
        r.add_header('Content-type', form.get_content_type())
        r.add_header('Content-length', len(data))
        response = request.urlopen(r).read().decode('utf-8')
        print(response)
        return response
    except Exception as e:
        print(e)

