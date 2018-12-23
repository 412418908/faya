
import os;
import ftplib

def uploadFileToFtp(localFile, serverIp, serverPort, username, password, remoteFolder):
    session = ftplib.FTP(serverIp , username, password)
    file = open(localFile, 'rb');
    filename = os.path.basename(localFile)
    path = os.path.join(remoteFolder, os.path.basename(localFile))
    session.makepasv();
    print "-----"
    session.storbinary(filename, file);
    print session.getline();
    file.close();
    session.quit();

uploadFileToFtp("d:/tmp/1.jpg", "192.168.182.130", 21, "ftp1", "ftp1", "/");
