
import os;
import ftplib
import time;
import traceback;
import shutil;
import json;
import uuid;

def uploadFileToFtp(localFile, serverIp, serverPort, username, password, remoteFolder):
    session = ftplib.FTP(serverIp , username, password)
    file = open(localFile, 'rb');
    filename = os.path.basename(localFile)
    path = os.path.join(remoteFolder, os.path.basename(localFile))
    session.makepasv();
    session.storbinary('STOR %s' % filename, file);
    file.close();
    session.quit();



#TODO
#1) get file list
#2) upload to ftp server
#3) delete file
#4) loop


srcFolder = "d:/tmp/toftp";
workFolder = "d:/tmp/work";
ftpServer = "10.1.25.210";
username = "A5070";
password = "1234567890";
FILE_SEGMENT_SIZE = 10*1024*1024;


if not os.path.exists(workFolder):
    os.makedirs(workFolder);

def getfilelist(srcFolder):
    result = [];
    files = os.listdir(srcFolder);
    for file in files:
        if file.startswith("."):
            continue;
        result.append(os.path.join(srcFolder, file));
    return result;


def uploadToServer(file):
    try:
        print '-------upload start'
        uploadFileToFtp(file, ftpServer, 21, username, password, "/");
        print "upload %s success" % (file);
        print '-------upload end'
    except Exception as err:
        print "upload %s fail" % (file);
        traceback.print_exc();

def writeBytes(input, output, size):
    writed = 0;
    bytes = input.read(size - writed);
    while bytes:
        output.write(bytes);
        writed += len(bytes);
        if (writed >= size):
            break;
        bytes = input.read(size - writed);


def extractFileToFolder(file, folder, fileid):
    filename = os.path.basename(file);
    filesize = os.path.getsize(file);
    segments = filesize / FILE_SEGMENT_SIZE;
    if (filesize % FILE_SEGMENT_SIZE) != 0 :
        segments += 1;
    with open(file, "rb") as input:
        for i in range(1, segments+1):
            segfilename = os.path.join(folder, "%s_seg_%d"%(fileid, i));
            print 'write', segfilename
            with open(segfilename, "wb") as output:
                writeBytes(input, output, FILE_SEGMENT_SIZE)

    # write info
    metadata = {"filename": filename, "filesize":filesize, "segments":segments};
    text = json.dumps(metadata);
    metafilename = os.path.join(folder, "%s-metadata.json"%(fileid));
    with open(metafilename, "w") as output:
        output.write(text);


def uploadFolderToServer(folder):
    files = os.listdir(folder);
    for file in files:
        file = os.path.join(folder, file)
        uploadToServer(file);
        os.remove(file);
    pass

def mainLoop():
    while True:
        files = getfilelist(srcFolder);
        for file in files:
            atime = os.path.getmtime(file);
            curtime = time.time();
            if (curtime - atime) < 3:
                print "file %s is copying , ignore" % (file)
                continue;
            filesize = os.path.getsize(file);
            if filesize > FILE_SEGMENT_SIZE:
                print "process large file ", file
                folderId =  str(uuid.uuid4()); #os.path.basename(file);
                tmpFolder = os.path.join(workFolder, folderId);
                shutil.rmtree(tmpFolder, ignore_errors=True)
                if  not os.path.exists(tmpFolder):
                    os.makedirs(tmpFolder)
                #extract file to tmpFolder
                extractFileToFolder(file, tmpFolder, folderId);
                #upload folder to server
                uploadFolderToServer(tmpFolder);
                #clean folder
                shutil.rmtree(tmpFolder)
                os.remove(file);
                pass

            else:
                uploadToServer(file);
                os.remove(file);
        time.sleep(0.5);
    pass

mainLoop();






#uploadFileToFtp("d:/tmp/1.jpg", "10.1.25.210", 21, "A5070", "1234567890", "/");
