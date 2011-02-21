import point_read
from mpl_toolkits.mplot3d import axes3d as p3
import numpy as np
import pylab
import argparse

default_cls = 'person'
default_pkl = 'validation-1298129177.09'


def draw_fig(inds, cls=default_cls):
    fig = pylab.figure(1)
    fig.clf()
    ax = p3.Axes3D(fig,azim=29,elev=22)

    ax.scatter3D(Rec[inds],
                 Prc[inds],
                 Time[inds][:-1],
                 c='b',marker='o',alpha=0.4,
                 vmin=[0,0], vmax=[1,1])

    length = lengths[inds][0]
    alg = C[np.nonzero(inds)[0][0]]
    print(alg)

    ax.set_ylabel('Precision')
    ax.set_xlabel('Recall')
    ax.set_zlabel('Time (s)')
    ax.set_title('Threshold PRT for %s [%d](%d-stage cascade)' %
                 (cls, keys[inds][0], length))
    pylab.draw()


if __name__ == "__main__" and not 'cms' in globals():
    parser = argparse.ArgumentParser(
        description='Generate a 3D plot from a pkl of results')

    parser.add_argument('pkl_path', help='pickle path (for point_read)')
    parser.add_argument('cls', metavar='class')
    parser.add_argument('alg', metavar='algorithm', type=int,
                        help='Algorithm index')
    parser.add_argument('-o','--out', metavar='out_name', type=str,
                        help='filename to output (.pdf)',
                        default='prt3d_output.pdf')

    args = parser.parse_args()

    # Only read if we don't have it already - makes iterating easier
    if not 'cms' in globals():
        (_,cms), = [_ for _ in
                    point_read.points_iter(args.pkl_path, args.cls)]

    TP = np.array([tp for tp,_,_,_, _,_,_ in cms],'f')
    FP = np.array([fp for _,fp,_,_, _,_,_ in cms],'f')
    TN = np.array([tn for _,_,tn,_, _,_,_ in cms],'f')
    FN = np.array([fn for _,_,_,fn, _,_,_ in cms],'f')
    Time = np.array([t for _,_,_,_, t,_,_ in cms],'f')

    Prc = TP / (TP + FP)
    Rec = TP / (TP + FN)

    C = [C for _,_,_,_, _,C,_ in cms]

    uC = set(C)
    lengths = np.array([len(c) for c in C])
    tbl = dict(zip(uC,range(len(uC))))
    keys = np.array([tbl[c] for c in C])

    draw_fig(keys==args.alg, cls=args.cls)
    pylab.figure(1).savefig(args.out)
