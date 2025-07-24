import textart
import gffutils, sys, re, typing
from Bio import SeqIO

HAS_FASTA = False
DO_TEST = False
SHOW_ALL_FEATURES = True
CHILDREN_ONLY = False

named_parent = None
select_featuretypes = ['gene']

try:
    sys.argv[1]
except:
    sys.exit("ERROR: no arguments given!\n"\
             "\ttype 'vigr.py -h' for help\n")
else:

    if '-t' in sys.argv:
        DO_TEST = True
        gff_file = "testing"

    if '-h' in sys.argv:
        with open('help.txt', 'r') as help_file:
            print(help_file.read())
            sys.exit() #adios!
    elif re.match(".*\.gff", sys.argv[1]):
        gff_file = sys.argv[1]
    elif '-g' in sys.argv:
        _index = sys.argv.index('-g') + 1
        if re.match(".*\.gff", sys.argv[_index]):
            gff_file = sys.argv[_index]
    elif not DO_TEST:
        sys.exit("ERROR: no .gff file provided!\n"
                 "\tPlease provide a .gff file using the following format:\n\n"\
                 "\t\t'vigr.py [file]' -or- 'vigr.py -g [file]'\n")

    if '-f' in sys.argv:
        _index = sys.argv.index('-f') + 1
        fasta_file = sys.argv[_index]
        HAS_FASTA = True

#-----------------------------------------------------------------------

class feature_main_window:

    def __init__(self, filename = 'gff/1A_genome.gff'):

        if DO_TEST:
            fn = gffutils.example_filename("intro_docs_example.gff")
            self.db = gffutils.create_db(fn, 'database/vigr.db', force = True)
        else:
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
        self.check_sequence_length()

        if HAS_FASTA:
            _fasta = SeqIO.index(fasta_file, 'fasta')
            self.sequence = _fasta.get(self.sequence_name).seq

    def check_sequence_length(self):
        # check if default offset of 10,000bp is an OK size
        if self.sequence_length < 40000:
            textart.little_ladder.offset = self.sequence_length // 4
        else:
            textart.little_ladder.offset = 9999

    def gff_parser(self, start, end):

        # get db within screen region
        if CHILDREN_ONLY:
            subset = self.db.children(id = named_parent,\
                                      order_by = 'featuretype')
            self.clear_features()
        else:
            subset = self.db.region(seqid = self.sequence_name,\
                                    start = start, end = end)
        # subset is an iterable of 'feature' objects
        # it may be faster to implement some way to iterate through
        # subset when rendering features to the screen, but I'll try
        # this out for now while I work on the 'features' window

        #save it to disk from the database query
        queried_features, buffered_feat_dict = [], []
        for x in subset:
            queried_features.append(x)

        # run through the feature and pull pertinent info onto a
        # dictionary
        for offset in range(len(queried_features)):
            feature = queried_features[offset]

            buffered_feat_dict.append({'id':feature.id,\
                           'start':feature.start,'end':feature.end,\
                           'col':0, 'tiles':None,\
                           'featuretype':feature.featuretype,\
                           'name':feature.attributes.get('Name'),\
                           'product':feature.attributes.get('product'),\
                           'parent':feature.attributes.get('Parent'),\
                           'strand':feature.strand, 'offset_list':[]})

        for buffered_feature in buffered_feat_dict:
            if not any(buffered_feature['id'] == existing_feat['id']\
                       for existing_feat in self.features):
                if SHOW_ALL_FEATURES:
                    self.features.append(buffered_feature)
                elif buffered_feature['featuretype'] in select_featuretypes:
                    self.features.append(buffered_feature)

        for feature in self.features.copy():
            if any(feature['id'] == b['id'] for b in buffered_feat_dict):
                pass
            else:
                self.features.remove(feature)

    def clear_features(self):
        self.features = []



def _undr_to_space(i):
    return(i.replace("_"," "))



file = feature_main_window(filename = gff_file)

