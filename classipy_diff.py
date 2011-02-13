import simplejson as json
import numpy as np
import cPickle as pickle
import django
import StringIO
import string
from django.template import Template, Context
# Hack suggested by the Django docs to use templates on their own
# http://docs.djangoproject.com/en/dev/ref/templates/api/
#     #configuring-the-template-system-in-standalone-mode
try:
    django.conf.settings.configure()
except RuntimeError:
    pass
import itertools

pickles_path = 'pickles'

# FIXME: This can't easily be changed, it's coupled with serve_classipy.py
images_path = 'JPEGImages'


# These are used if no arguments are passed, mostly to help debugging
default_runs = ['imfeat._histogram_joint.histogram_joint__0__train.pkl',
                'imfeat._histogram_joint.histogram_joint_lab__0__train.pkl']
default_class = 'bicycle'


def load_pickle(filename='%s/%s' % (pickles_path, default_runs[0]),
                cls=default_class):
    """Convert from input structure to an array of dicts, sorted by confidence
    in[1][i] = (confidence, label)
    in[2][i] = image

    out[i].label: a ground truth label (-1, 1)
    out[i].image:
    out[i].image_url:
    out[i].rank: index in the array
    """
    with open(filename, 'r') as f:
        items = pickle.load(f)[cls]
    items = [dict(label=label, conf=conf, image=image) for (label, conf), image
            in zip(items[1], items[2])]

    for d in items:
        d['filename'] = filename
        image = d['image']
        # TODO: Strip the _0 off the end of the filename. Improve this later
        d['image_url'] = '%s/%s' % (images_path, image[:-2])
    items = sorted(items, key=lambda _: _['conf'])
    for i in range(len(items)):
        items[i]['rank'] = i
    return items


def render_items(items):
    """Render a <div> containing a list of images, their confidences values,
    ground truth labels.
    in[i].image_url
    in[i].label
    ...
    """
    result = StringIO.StringIO()
    result.write("""<div style='width:100%;
                    white-space:nowrap;overflow-x:hidden;overflow-y:hidden'>\
                    <div style='width:100%'>""")
    for item in items:
        locals().update(item)
        if item['label'] == 1:
            gtstyle = 'background-color:lightgreen;'
            gt = '+'
        else:
            gtstyle = 'background-color:lightpink;'
            gt = '-'
        result.write("""
        <div style='float:left;padding:5px'>
              <div><img src='{image_url}' style='height:100px;width:auto' />
              </div>
              <div><span style='{gtstyle}padding:5px'>[{rank}]{conf:.2f}</span></div>
      </div>""".format(**locals()))
    result.write("""</div></div>""")
    return result.getvalue()


def make_roc_chart(runs):
    tpr = []
    fpr = []
    for run in runs:
        run_items = run['run_items']
        confs = np.array([_['conf'] for _ in run_items])
        labels = np.array([_['label'] for _ in run_items])
        tn = np.cumsum(labels == -1)
        fn = np.cumsum(labels == 1)
        P = np.sum(labels == 1)
        N = np.sum(labels == -1)
        TPR = 1 - fn/float(P)
        FPR = 1 - tn/float(N)
        skip = np.ceil(float(P+N)/20)
        tpr.append(','.join(map(str, TPR[::skip])))
        fpr.append(','.join(map(str, FPR[::skip])))
    chd = '|'.join(['|'.join(_) for _ in zip(fpr,tpr)])
    chart = """
    http://chart.apis.google.com/chart
       ?chs=256x256
       &cht=lxy
       &chco=3072F3,FF0000
       &chd=t:{chd}
       &chds=0,1,0,1
       &chxr=0,0,1|1,0,1
       &chxt=x,y
       &chdl=Run_0|Run_1
       &chdlp=b
     """.format(chd=chd)
    return ''.join(chart.split())


def make_items(filename, cls=default_class):
    run_items = load_pickle('%s/%s' % (pickles_path, filename), cls)

    hardest_pos = (_ for _ in run_items if _['label'] == 1)
    hardest_pos = list(itertools.islice(hardest_pos, 25))
    hardest_neg = (_ for _ in run_items[::-1] if _['label'] == -1)
    hardest_neg = list(itertools.islice(hardest_neg, 25))
    hardest_pos_div = render_items(hardest_pos)
    hardest_neg_div = render_items(hardest_neg)
    item_div = render_items(run_items)
    return locals()


def render_html(run_filenames=default_runs, cls=default_class):
    """Create an html file showing some important parts of images
    """
    with open('classipy_diff.html', 'r') as f:
        template = Template(f.read())

    runs = map(lambda x: make_items(x, cls), run_filenames)
    chart = make_roc_chart(runs[:2])
    return template.render(Context(locals()))


def write_html(filename='out.html', **kwargs):
    with open(filename,'w') as f:
        f.write(render_html(**kwargs))


if __name__ == "__main__":
    # TODO: use command line arguments to render the html to stdout or a file
    write_html()
