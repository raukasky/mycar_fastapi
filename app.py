import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse, Response
import os
import zipfile
import io


app = FastAPI()

DIR = 'source'
DIR_COMPRESS = 'compressed'


async def compress(dir, dir_compress):
    with os.scandir(path=dir) as dir_path:
        async for entry in dir_path:
            if not entry.is_file():
                print('Not files')
            else:
                print('file: ' + entry.name)
            await os.system(
                'cjpeg.exe -quant-table 2 -quality 60 -outfile {}  {}'.format(dir_compress + '_2' + entry.name,
                                                                              dir + entry.name))
            await os.system(
                'cjpeg.exe -quant-table 3 -quality 60 -outfile {}  {}'.format(dir_compress + '_3' + entry.name,
                                                                              dir + entry.name))


def zipped(filenames):
    zip_subdir = 'compressed'
    zip_filename = "%s.zip" % zip_subdir
    s = io.StringIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)
    zf.close()
    resp = Response(s.getvalue(), mimetype="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp


@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    return JSONResponse(content=file.filename, status_code=200)


@app.get('/load')
async def download_file():
    for file in os.path(DIR_COMPRESS):
        return zipped(file)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

