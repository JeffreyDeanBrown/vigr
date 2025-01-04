import gffutils, sys, re, typing

try:
    sys.argv[1]
except:
    sys.exit("ERROR: no arguments given!\n"\
             "\ttype 'vigr.py -h' for help\n")
else:
    if re.match(".*\.gff", sys.argv[1]):
        gff_file = sys.argv[1]
    elif '-g' in sys.argv:
        _index = sys.argv.index('-g') + 1
        if re.match(".*\.gff", sys.argv[_index]):
            gff_file = sys.argv[_index]
    else:
        sys.exit("ERROR: no .gff file provided!\n"
                 "\tPlease provide a .gff file using the following format:\n\n"\
                 "\t\t'vigr.py [file]' -or- 'vigr.py -g [file]'\n")


class feature_presentation:

    def __init__(self, filename = 'gff/1A_genome.gff'):
        self.db = gffutils.create_db(filename, 'database/vigr.db', force = True)

        # get the seqids from the database
        cursor = self.db.execute('SELECT seqid FROM features')
        # save to disk
        _results = cursor.fetchall()
        # unnest row objects, sort
        self.seqids = list(set([row['seqid'] for row in _results]))
        self.seqids.sort(key = _undr_to_space)

        self.sequence_name = self.seqids[0] #default to first sequence
        self.set_sequence(self.sequence_name)

    features = []

    def set_sequence(self, sequence: typing.Union[int,str]):

        if isinstance(sequence, int):
            sequence = self.seqids[sequence]

        self.sequence_name = str(sequence)
        # get where last feature in sequence ends
        query = 'SELECT end FROM features WHERE seqid=="'\
                + str(sequence) + '"'
        cursor = self.db.execute(query)
        # returns a list of row objects (with only 1 col each)
        _results = cursor.fetchall()
        self.sequence_length = max([row[0] for row in _results])


    def gff_parser(self, start, end):

        # get db within screen region
        subset = self.db.region(seqid = self.sequence_name, start = start, end = end)
        # subset is an iterable of 'feature' objects
        # it may be faster to implement some way to iterate through
        # subset when rendering features to the screen, but I'll try
        # this out for now while I work on the 'features' window
        features_orig, buffer = [], []

        #save it to disk
        for x in subset:
            features_orig.append(x)

        for offset in range(len(features_orig)):
            feature = features_orig[offset]

            buffer.append({'id':feature.id, 'start':feature.start,\
                           'end':feature.end, 'col':None, 'tiles':None,\
                           'featuretype':feature.featuretype,\
                           'name':feature.attributes.get('Name'),\
                           'product':feature.attributes.get('product')[0],\
                           'strand':feature.strand})

        for buffered_feature in buffer:
            if any(buffered_feature['id'] == l['id'] for l in self.features):
                pass
            else:
                self.features.append(buffered_feature)

        for feature in self.features.copy():
            if any(feature['id'] == b['id'] for b in buffer):
                pass
            else:
                self.features.remove(feature)

    def reset_cols(self):
        for feature in self.features:
            feature['col'] = None


def _undr_to_space(i):
    return(i.replace("_"," "))



file = feature_presentation(filename = gff_file)

