import re
import glob
import pickle
import gzip


def points_iter(conf_dir, class_names=None):
    """Load confusion matrix points from a variety of styles

    Args:
        conf_dir: Directory path to data
        class_names: If specified, only produce these classes (default: None)

    Yields:
        class_name, cms where cms is iterator of
        (tp, fp, tn, fn, run_time, chain_names, chain_threshs)
    """
    def skip_class(name):
        if class_names and name not in class_names:
            return True

    def load_pkl_list(fp):
        while 1:
            try:
                yield pickle.load(fp)
            except EOFError:
                break
    for pickle_fn in glob.glob('%s/*.pkl' % conf_dir):
        class_name = re.search('.+/(.+)\.pkl', pickle_fn).group(1)
        if skip_class(class_name):
            continue
        with open(pickle_fn) as pickle_fp:
            yield class_name, pickle.load(pickle_fp)
    for pickle_fn in glob.glob('%s/*.pkl.list' % conf_dir):
        class_name = re.search('.+/(.+)\.pkl\.list', pickle_fn).group(1)
        if skip_class(class_name):
            continue
        print(pickle_fn)
        pickle_fp = open(pickle_fn)
        yield class_name, load_pkl_list(pickle_fp)
    for pickle_fn in glob.glob('%s/*.pkl\.gz' % conf_dir):
        class_name = re.search('.+/(.+)\.pkl\.gz', pickle_fn).group(1)
        if skip_class(class_name):
            continue
        pickle_fp = gzip.GzipFile(pickle_fn)
        yield class_name, load_pkl_list(pickle_fp)

if __name__ == '__main__':
    for class_name, cms in points_iter('validation-1298129177.09'):
        print(class_name)
