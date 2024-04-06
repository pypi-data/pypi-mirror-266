import pickle


def pickle_to_file(obj, pickle_fn):
    ofd = open(pickle_fn, 'wb')    
    ofd.write(pickle.dumps(obj))
    ofd.close()

def un_pickle_from_file(pickle_fn):
    ifd = open(pickle_fn, 'rb')
    revived = pickle.load(ifd)
    ifd.close()
    return revived
