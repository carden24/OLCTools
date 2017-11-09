#!/usr/bin/env python
from queue import Queue
from glob import glob
from threading import Thread
import os
from accessoryFunctions.accessoryFunctions import printtime
__author__ = 'adamkoziol'


class Compress(object):

    def compressthreads(self):
        """Compresses large files created by the pipeline"""
        import re
        printtime('Compressing large files', self. start)
        compressfile = list()
        for sample in self.metadata:
            for key, value in sample.general.datastore.items():
                if type(value) is list:
                    for item in value:
                        if type(item) is str:
                            if re.search(".fastq$", item) and not os.path.islink(item):
                                compressfile.append(item)
        for i in range(len(compressfile)):
            # Send the threads to makeblastdb
            threads = Thread(target=self.compress, args=())
            # Set the daemon to true - something to do with thread management
            threads.setDaemon(True)
            # Start the threading
            threads.start()
        # Compress files as necessary
        for compress in sorted(compressfile):
            self.compressqueue.put(compress)
        self.compressqueue.join()  # wait on the dqueue until everything has been processed
        # Remove the original files once they are compressed
        for compress in sorted(compressfile):
            if os.path.isfile('{}.gz'.format(compress)):
                try:
                    os.remove(compress)
                except (OSError, IOError):
                    pass
        self.remove()

    def compress(self):
        while True:
            compressfile = self.compressqueue.get()
            if '.gz' not in compressfile:
                if not os.path.isfile('{}.gz'.format(compressfile)):
                    with open(compressfile, 'rb') as inputfile:
                        with open('{}.gz'.format(compressfile), 'wb') as outputfile:
                            outputfile.writelines(inputfile)
            self.compressqueue.task_done()

    def remove(self):
        """Removes unnecessary temporary files generated by the pipeline"""
        import shutil
        printtime('Removing temporary files', self.start)
        removefile = []
        for sample in self.metadata:
            if sample.general.bestassemblyfile != 'NA':
                removefile.append(glob('{}/K*/'.format(sample.general.spadesoutput)))
                removefile.append('{}/misc/'.format(sample.general.spadesoutput))
                removefile.append('{}/tmp/'.format(sample.general.spadesoutput))
        # Clear out the folders
        for folder in removefile:
            try:
                shutil.rmtree(folder)
            except (OSError, TypeError):
                pass

    def __init__(self, inputobject):
        self.metadata = inputobject.runmetadata.samples
        self.start = inputobject.starttime
        self.compressqueue = Queue()
        self.compressthreads()
