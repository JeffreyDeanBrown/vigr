import gffutils, sqlite3



#FIXME
try:
    db
except NameError:
    db = gffutils.create_db('gff/1A_genome.gff', 'database/vigr.db', force = True)
    sequence_length = 328814


def gff_parser(start, end):


    #FIXME
    # will have to actually implement this in the future
    seqid = 'NODE_1_length_328814_cov_187.267238'

    subset = db.region(seqid = seqid, start = start, end = end)
    # subset is an iterable of 'feature' objects
    # it may be faster to implement some way to iterate through
    # subset when rendering features to the screen, but I'll try
    # this out for now while I work on the 'features' window
    global features_orig, features
    features_orig, features = [], []
    for x in subset:
        features_orig.append(x)

    for offset in range(len(features_orig)):
        feature = features_orig[offset]
        features.append({'id':feature.id, 'start':feature.start, 'end':feature.end})


