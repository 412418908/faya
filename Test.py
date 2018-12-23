
from bs4 import BeautifulSoup
from Worker import Worker
from pluginbase import *

file = "conf/sendtoftp.job.xml"
file = open(file).read()
xml = BeautifulSoup(file, "html.parser")

worker = Worker(xml)
worker.run();

