import os;
import time
current_milli_time = lambda: int(round(time.time() * 1000))

class InputPlugin:

    def init(self, element):
        pass

    def read(self):
        pass


class OutputPlugin:
    def init(self, element):
        pass

    def write(self, record):
        pass

class FileInputPlugin(InputPlugin):
    folder = "";
    filenames = "*.*";
    toreadfiles = [];
    lastReadTimestamp = 0;
    currentReadFile = None;
    currentFilename = "";

    def __init__(self):
        pass

    def init(self, element):
        InputPlugin.init(self, element);
        self.folder = element["folder"];
        self.filenames = element["filenames"];

    def getNextFilename(self):
        if len(self.toreadfiles) == 0:
            curTimestamp = current_milli_time();
            if (curTimestamp - self.lastReadTimestamp < 1000):
                return None;
            self.toreadfiles = os.listdir(self.folder);
            if len(self.toreadfiles) == 0:
                return None;

        filename = self.toreadfiles[-1];
        del self.toreadfiles[-1];
        return filename;

    def openNextFile(self):
        filename = self.getNextFilename();
        if (filename == None):
            return None;
        self.currentFilename = filename;
        filepath = os.path.join(self.folder, filename);
        self.currentReadFile = open(filepath, "rb");
        return self.currentReadFile;

    def read(self):
        if (self.currentReadFile == None):
            self.currentReadFile = self.openNextFile();
            if (self.currentReadFile == None):
                return None;
        bytes_read = self.currentReadFile.read(8192);
        if not bytes_read:
            print "read file end", self.currentFilename;
            self.currentReadFile.close();
            self.currentReadFile = None;
            filepath = os.path.join(self.folder, self.currentFilename);
            os.remove(filepath);
            return None;
        record = {"filename": self.currentFilename, "buf": bytes_read};
        return record;

    def close(self ):
        self.currentReadFile.close();

class FileOutputPlugin(OutputPlugin):
    folder = "";
    filename = "";
    maxsize = 1024*1024;
    currentFilename = None;
    currentFileSeq = 0;
    currentWriteFilename = None;
    currentWriteFile = None;
    currentWritedBytes = 0;

    def __init__(self):
        pass

    def init(self, element):
        OutputPlugin.init(self, element);
        self.folder = element["folder"];
        self.filename = element["filename"];
        self.maxsize = int(element["maxsize"][0:-1]) * 1024 * 1024;
        print "folder=", self.folder, ", filename=", self.filename, ", maxsize=", self.maxsize


    def createNewFile(self):
        self.currentFileSeq = self.currentFileSeq + 1;
        filename = self.filename.replace("${filename}", self.currentFilename);
        filename = filename.replace("$seq", str(self.currentFileSeq));
        filepath = os.path.join(self.folder, filename);
        print "create file ", filepath
        self.currentWriteFilename = filename;
        self.currentWriteFile = open(filepath, "wb");

        pass

    def write(self, record):
        filename = record["filename"];
        buf = record["buf"];
        if self.currentFilename == None:
            print "create file ", filename
            self.currentFilename = filename;
            self.createNewFile();
        if self.currentFilename != filename or self.currentWriteFile == None:
            # close file
            print "close file"
            self.close();
            self.currentFilename = filename;
            self.currentFileSeq = 0;
            self.createNewFile();

        self.currentWriteFile.write(buf);
        self.currentWritedBytes += len(buf);
        #print "writed ", self.currentWritedBytes
        if (self.currentWritedBytes >=  self.maxsize):
            print "switch to new file"
            self.currentWriteFile.close();
            self.currentWriteFile = None;
            self.currentFilename = filename;
            self.currentFilename = filename;
            self.createNewFile();
            self.currentWritedBytes = 0;


        pass

    def onIdle(self):
        if self.currentWriteFile != None:
            print "close file"
            self.close();


    def close(self):
        if self.currentWriteFile != None:
            self.currentWriteFile.close();
            self.currentWriteFile = None;
        self.currentFilenname = None;
        self.currentWritedBytes = 0;
        self.currentWriteFilename = "";