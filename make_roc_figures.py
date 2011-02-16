import numpy as np
from pylab import *
import classipy_diff


#labels = np.array([-1, -1, 1, 1, -1, -1, 1, -1, -1, 1])
#labels = np.sign(np.random.random(80)-0.5)
labels = np.array([ 1.,  1., -1., -1.,  1., -1., -1.,  1., -1., -1., -1.,  1.,  1.,
                   -1.,  1., -1., -1.,  1.,  1., -1., -1.,  1.,  1., -1., -1., -1.,
                   -1.,  1., -1.,  1., -1., -1.,  1.,  1.,  1., -1.,  1.,  1.,  1.,
                    1., -1.,  1., -1., -1.,  1.,  1., -1., -1., -1., -1., -1., -1.,
                   -1.,  1.,  1.,  1.,  1.,  1.,  1., -1.,  1.,  1., -1., -1.,  1.,
                    1.,  1.,  1.,  1.,  1., -1., -1., -1.,  1.,  1., -1.,  1.,  1.,
                   -1., -1.])
                  
def filter_exact(run_items):
    """Return indices corresponding to the exact 'kept' values.
    No care has been taken to match the ideal behavior for edge cases
    """
    #labels = np.array([_['label'] for _ in run_items])
    inds = []
    for i in range(len(labels)-1):
        if labels[i]==-1 and labels[i+1]==1:
            inds.append(i)
    return inds


def load_pickle():
    run_items = classipy_diff.load_pickle()
    return locals()


def make_roc(run_items):
    #labels = np.array([_['label'] for _ in run_items])
    tn = np.cumsum(labels == -1)
    fn = np.cumsum(labels == 1)
    P = np.sum(labels == 1)
    N = np.sum(labels == -1)
    TPR = 1 - fn/float(P)
    FPR = 1 - tn/float(N)
    return locals()


if __name__ == '__main__' or 1:
    globals().update(load_pickle())
    globals().update(make_roc(run_items))
    exact = filter_exact(run_items)

    # Draw the ROC
    figure(1)
    clf()
    plot(FPR, TPR)
    scatter(FPR, TPR, color='k', marker='+')
    # exact=[20,28,40] force fewer points selected for the figure
    scatter(FPR[exact], TPR[exact], color='r', marker='o')
    xlabel('False Positive Rate')
    ylabel('True Positive Rate')
    title('ROC')
    draw()
    show()
