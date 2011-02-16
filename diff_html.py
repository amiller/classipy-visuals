import classipy_diff
import numpy as np
import StringIO
import string
import django
import argparse
from django.template import Template, Context
# Hack suggested by the Django docs to use templates on their own
# http://docs.djangoproject.com/en/dev/ref/templates/api/
#     #configuring-the-template-system-in-standalone-mode
try:
    django.conf.settings.configure()
except RuntimeError:
    pass


def make_roc_chart(runs):
    tpr = []
    fpr = []
    for run in runs:
        skip = np.ceil(float(run['P']+run['N'])/20)
        tpr.append(','.join(map(str, run['TPR'][::skip])))
        fpr.append(','.join(map(str, run['FPR'][::skip])))
    chd = '|'.join(['|'.join(_) for _ in zip(fpr, tpr)])
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


def render_items(run, inds=None):
    """Render a <div> containing a list of images, their confidences values,
    ground truth labels.
    """
    if inds is None:
        inds = range(len(run))
    context = Context(run)
    context.update(dict(inds=inds))
    context.update(dict(items=np.array(zip(run['ranks'],
                                           run['image_urls'],
                                           run['confs'],
                                           run['labels']))[inds]))

    template = """
    <div style='width:100%;
                white-space:nowrap;overflow-x:hidden;overflow-y:hidden'>\
      <div style='width:100%'>
      {% for rank,image_url,conf,label in items %}
        <div style='float:left;padding:5px'>
        <div><img src='{{image_url}}' style='height:100px;width:auto'/>
         </div>
              <div><span style='
              {% if label == '1' %}
                background-color:lightgreen;
              {% else %}
                background-color:lightpink;
              {% endif %}
                padding:5px'>[{{rank}}]{{conf|floatformat:2}}
              </span></div>
        </div>
      {% endfor %}
      </div>
    </div>"""
    return Template(template).render(context)


def make_divs(run):
    global pos_inds, neg_inds
    pos_inds = np.flatnonzero(run['labels']==1)
    neg_inds = np.flatnonzero(run['labels']==-1)
    hardest_pos = pos_inds[:100]
    hardest_neg = neg_inds[:-100:-1]
    hardest_pos_div = render_items(run, hardest_pos)
    hardest_neg_div = render_items(run, hardest_neg)
    item_div = render_items(run)
    return locals()


def render_html(runs):
    """Create an html file showing some important parts of images
    """
    with open('classipy_diff.html', 'r') as f:
        template = Template(f.read())

    for r in runs:
        r.update(make_divs(r))

    hardest_pos_inds = classipy_diff.hardest_positive_images(runs)
    hardest_pos_div = render_items(runs[0], hardest_pos_inds[:100])

    hardest_neg_inds = classipy_diff.hardest_negative_images(runs)
    hardest_neg_div = render_items(runs[0], hardest_neg_inds[:100])

    cls = runs[0]['cls']
    chart = make_roc_chart(runs[:2])
    return template.render(Context(locals()))


def write_html(filename='out.html', **kwargs):
    with open(filename, 'w') as f:
        f.write(render_html(**kwargs))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare runs')
    parser.add_argument('runs', metavar='runs', type=str, nargs='+',
                        help='paths to .pkls for classifier runs')
    args = parser.parse_args()

    # TODO: use command line arguments to render the html to stdout or a file
    runs = [classipy_diff.load_run(f) for f in args.runs]
    write_html(runs=runs)
