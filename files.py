import gffutils, sqlite3


#FIXME

class feature_presentation:

    def __init__(self, filename = 'gff/1A_genome.gff', sequence_length = 328814,\
                 seqid = 'NODE_1_length_328814_cov_187.267238'):
        self.db = gffutils.create_db(filename, 'database/vigr.db', force = True)
        self.sequence_length = sequence_length
        self.seqid = seqid

    features = []

    def gff_parser(self, start, end):
        #FIXME
        # will have to actually implement this in the future

        subset = self.db.region(seqid = self.seqid, start = start, end = end)
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



file = feature_presentation()

