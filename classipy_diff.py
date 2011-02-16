import simplejson as json
import numpy as np
import cPickle as pickle
import django
import itertools

# FIXME: This can't easily be changed, it's coupled with serve_classipy.py
images_path = 'JPEGImages'


# These are used if no arguments are passed, mostly to help debugging
default_runs = ['pickles/imfeat._histogram_joint.histogram_joint__0__train.pkl',
                'pickles/imfeat._histogram_joint.histogram_joint_lab__0__train.pkl']
default_class = 'bicycle'


def pick_threshold_tpr(run_items, tpr):
    """Given a run and a target TPR, choose the effective threshold
    """
    pass


def hardest_positive_images(runs):
    # Indices in runs, sorted by image name
    indss = [np.argsort(run['images']) for run in runs]
    indss = [[i for i in inds if run['labels'][i]==1]
             for run, inds in zip(runs, indss)]

    # Find highest rank across all runs for each image
    rankss = [run['ranks'][inds] for run, inds in zip(runs, indss)]
    max_ranks = np.max(rankss, 0)

    # Find the lowest ranking images, in indices for runs[0]
    indsmax = np.argsort(max_ranks)
    return np.array(indss[0])[indsmax]


def hardest_negative_images(runs):
    # Indices in runs, sorted by image name
    indss = [np.argsort(run['images']) for run in runs]
    indss = [[i for i in inds if run['labels'][i]==-1]
             for run, inds in zip(runs, indss)]

    # Find lowest rank across all runs for each image
    rankss = [run['ranks'][inds] for run, inds in zip(runs, indss)]
    min_ranks = np.min(rankss, 0)

    # Find the highest ranking images, in indices for runs[0]
    indsmin = np.argsort(min_ranks)
    return np.array(indss[0])[indsmin]


def load_run(filename=default_runs[0],
                cls=default_class):
    """Convert to dict of parallel arrays
    """
    with open(filename, 'r') as f:
        items = pickle.load(f)[cls]

    confs = np.array([_[1] for _ in items[1]])
    inds = np.argsort(confs)
    confs = np.array([_[1] for _ in items[1]])[inds]
    labels = np.array([_[0] for _ in items[1]])[inds]
    images = np.array(items[2])[inds]

    image_urls = ['%s/T_%s' % (images_path, image[:-2]) for image in images]
    # TODO: This strips _0 off the end of the filename. Improve this later

    ranks = np.array(range(len(images)))
    tn = np.cumsum(labels == -1)
    fn = np.cumsum(labels == 1)
    P = np.sum(labels == 1)
    N = np.sum(labels == -1)
    TPR = 1 - fn/float(P)
    FPR = 1 - tn/float(N)
    del f, items, inds, image
    return locals()
