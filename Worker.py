
import time
import json
import traceback
from pluginbase import *;

class Worker:
    """  transfer worker
    """
    xml = "";
    input = "";
    output = "";

    def __init__(self, xml):
        self.xml = xml;
        self.input = FileInputPlugin();
        self.input.init(xml.input);
        self.output = FileOutputPlugin();
        self.output.init(xml.output);

    def run(self):
        try:
            while True:
                rec = self.input.read();
                if (rec == None):
                    self.output.onIdle();
                    time.sleep(1);
                    continue;
                self.output.write(rec);
        except Exception as err:
            print "process file fail", err
            traceback.print_exc()


    def close(self):
        self.input.close();
        self.output.close();