#!/usr/bin/env python
__author__ = 'adamkoziol'


class MetadataReader(object):

    def reader(self):
        import os
        import json
        from accessoryFunctions.accessoryFunctions import GenObject, MetadataObject
        for sample in self.metadata:
            metadatafile = '{}{}/{}_metadata.json'.format(self.path, sample.name, sample.name)
            if os.path.isfile(metadatafile):
                size = os.stat(metadatafile).st_size
                if size != 0:
                    try:
                        with open(metadatafile) as metadatareport:
                            jsondata = json.load(metadatareport)
                        # Create the metadata objects
                        metadata = MetadataObject()
                        # Initialise the metadata categories as GenObjects created using the appropriate key
                        for attr in jsondata:
                            if not isinstance(jsondata[attr], dict):
                                setattr(metadata, attr, jsondata[attr])
                            else:
                                setattr(metadata, attr, GenObject(jsondata[attr]))
                        # As files often need to be reanalysed after being moved, test to see if it possible to use the
                        # metadata from the previous assembly
                        jsonfile = '{}/{}_metadata.json'.format(metadata.general.outputdirectory, sample.name)
                        try:
                            # Open the metadata file to write
                            with open(jsonfile, 'w') as metadatafile:  # Change from wb to w since this is text in python3
                                # Write the json dump of the object dump to the metadata file
                                json.dump(sample.dump(), metadatafile, sort_keys=True, indent=4, separators=(',', ': '))
                            # Set the name
                            metadata.name = sample.name
                            self.samples.append(metadata)
                        except IOError:
                            self.samples.append(sample)
                    except ValueError:
                        self.samples.append(sample)
            else:
                self.samples.append(sample)

    def __init__(self, inputobject):
        self.metadata = inputobject.samples
        self.path = inputobject.path
        self.samples = []
        self.reader()
