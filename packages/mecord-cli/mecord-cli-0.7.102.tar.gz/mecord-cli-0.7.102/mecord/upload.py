from urllib.parse import *

def addtionExif(srcFile, taskUUID):
    if taskUUID == None or len(taskUUID) == 0:
        return
    try:
        from pathlib import Path
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
            from PIL import Image
            img = Image.open(srcFile)
            exif_dict = {
                "0th": { }, 
                "Exif": { }, 
                "1st": { },
                "thumbnail": None, 
                "GPS": { }
            }
            import piexif
            if taskUUID:
                exif_dict["0th"] = { 
                    piexif.ImageIFD.Software: f'make with mecord({taskUUID})'.encode(),
                    piexif.ImageIFD.Copyright: f'xinyu'.encode(),
                }
                exif_dict["Exif"] = {
                    piexif.ExifIFD.UserComment: f'make with mecord({taskUUID})'.encode(),
                }
            exif_dat = piexif.dump(exif_dict)
            img.save(srcFile, "webp", quality=90, exif=exif_dat)
        # elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
        #     params = {}
        # elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
        #     params = {}
        # else:
        #     params = {}
    except:
        return

def transcode(srcFile):
    try:
        from pathlib import Path
        from PIL import Image
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        if ext in [".jpg", ".png", ".jpeg", ".bmp"]:
            image = Image.open(srcFile, "r")
            format = image.format
            if format.lower() != "webp":
                fname = Path(srcFile).name
                newFile = srcFile.replace(fname[fname.index("."):], ".webp")
                image.save(newFile, "webp", quality=90)
                image.close()
                return True, newFile
    except Exception as e:
        pass
    return False, srcFile

def additionalUrl(srcFile, ossUrl):
    from pathlib import Path
    from PIL import Image
    try:
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        params = {}
        if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
            img = Image.open(srcFile)
            params["width"] = img.width
            params["height"] = img.height
        elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
            params = {}
        elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
            params = {}
        else:
            params = {}
        parsed_url = urlparse(ossUrl)
        updated_query_string = urlencode(params, doseq=True)
        final_url = parsed_url._replace(query=updated_query_string).geturl()
        return final_url
    except:
        return ossUrl

def upload(src, taskUUID):
    import os
    from mecord import store
    from pathlib import Path
    from mecord import taskUtils
    from mecord import xy_pb
    import requests
    if os.path.exists(src) == False:
        raise Exception(f"upload file not found")
    country = None
    if store.is_multithread() or taskUUID != None:
        country = taskUtils.taskCountryWithUUID(taskUUID)
    else:
        firstTaskUUID, country = taskUtils.taskInfoWithFirstTask()
    if country == None:
        country = "test"

    needDeleteSrc, newSrc = transcode(src)
    addtionExif(newSrc, taskUUID)
    file_name = Path(newSrc).name
    ossurl, content_type = xy_pb.GetOssUrl(country, os.path.splitext(file_name)[-1][1:])
    if len(ossurl) == 0:
        raise Exception(f"oss server is not avalid, msg = {content_type}")

    headers = dict()
    headers['Content-Type'] = content_type
    requests.adapters.DEFAULT_RETRIES = 3
    s = requests.session()
    s.keep_alive = False
    res = s.put(ossurl, data=open(newSrc, 'rb').read(), headers=headers)
    s.close()
    if res.status_code == 200:
        ossurl = additionalUrl(newSrc, ossurl)
        if needDeleteSrc:
            os.remove(newSrc)
        return ossurl
    else:
        raise Exception(f"upload file fail! res = {res}")

def uploadWidget(src, widgetid):
    from mecord import xy_pb
    import requests
    ossurl, content_type = xy_pb.GetWidgetOssUrl(widgetid)
    if len(ossurl) == 0:
        raise Exception("oss server is not avalid")
    
    headers = dict()
    headers['Content-Type'] = content_type
    requests.adapters.DEFAULT_RETRIES = 3
    s = requests.session()
    s.keep_alive = False
    res = s.put(ossurl, data=open(src, 'rb').read(), headers=headers)
    s.close()
    if res.status_code == 200:
        ossurl = additionalUrl(src, ossurl)
        checkid = xy_pb.WidgetUploadEnd(ossurl)
        if checkid > 0:
            return ossurl, checkid
        else:
            raise Exception("check fail!")
    else:
        raise Exception(f"upload file fail! res = {res}")

def uploadModel(name, cover, model_url, type, taskUUID):
    from mecord import store
    from mecord import taskUtils
    from mecord import xy_pb
    from mecord import store
    realTaskUUID = taskUUID
    country = None
    if store.is_multithread() or taskUUID != None:
        country = taskUtils.taskCountryWithUUID(taskUUID)
    else:
        firstTaskUUID, country = taskUtils.taskInfoWithFirstTask()
        if realTaskUUID == None:
            realTaskUUID = firstTaskUUID
    if country == None:
        country = "test"
    return xy_pb.UploadMarketModel(country, name, cover, model_url, type, realTaskUUID)
    