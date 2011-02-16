# experiments with the Python Image Library (PIL)
# free from:  http://www.pythonware.com/products/pil/index.htm
# create 128x128 (max size) thumbnails of all JPEG images in the working folder
# Python23 tested    vegaseat    25feb2005
# fernandooa modified

import glob
import Image

# get all the jpg files from the current folder
for infile in glob.glob("*.jpg"):
    im = Image.open(infile)
    # don't save if thumbnail already exists
    if infile[0:2] != "T_":
        # convert to thumbnail image
        im.thumbnail((128, 128), Image.ANTIALIAS)
        # prefix thumbnail file with T_
        im.save("T_" + infile, "JPEG")
