import pyzipper
import rarfile
import os
import glob

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Gz:
    @classmethod
    def zip(cls, **kwargs):
        # init args
        filename = kwargs.get('filename')
        source = kwargs.get('source')
        password = kwargs.get('password', None)

        # get all files
        files = glob.glob(f'{source}/**', recursive=True)
        encryption = pyzipper.WZ_AES if password else None

        # zip files
        with pyzipper.AESZipFile(filename, 'w',compression=pyzipper.ZIP_STORED, encryption=encryption) as zf:
            if password:
                zf.setpassword(password)

            # 相对目录，添加到 zip 包中
            for file in files:
                zf.write(file, arcname=os.path.relpath(file, source))

    @classmethod
    def unzip(cls, **kwargs):
        filename = kwargs.get('filename')
        password = kwargs.get('password', None)
        target = kwargs.get('target', 'dist')

        # ensure target
        mkdir_p(target)

        # detect password
        if password:
            zip_class = pyzipper.AESZipFile
        else:
            zip_class = pyzipper.ZipFile

        with zip_class(filename, 'r', password=password) as zip_file:
            zip_list = zip_file.namelist()
            for zip_item in zip_list:
                if zip_item == './':
                    continue

                try:
                    nf = zip_item.encode('cp437').decode('gbk')
                except:
                    nf = zip_item.encode('utf-8').decode('utf-8')
                new_path = os.path.join(target, nf)
                # 判断f是否是目录，目录的结尾是'/'或'\'
                if zip_item[-1] not in ['\\', '/']:
                    with open(new_path, 'wb') as file:
                        file.write(zip_file.read(zip_item))
                        file.close()
                else:
                    os.mkdir(new_path)
            zip_file.close()

    @classmethod
    def unrar(cls, **kwargs):
        filename = kwargs.get('filename')
        target = kwargs.get('target', 'dist')

        # ensure target
        mkdir_p(target)

        if os.name == 'nt':
            cmd = f'360zip.exe -x "{filename}" "{target}"'
            os.system(cmd)
        else:
            if not rarfile.is_rarfile(filename):
                print(f'{filename} is not a valid rar file')
                return
            with rarfile.RarFile(filename) as rf:
                rf.extractall(path=target)
