import os
import sys
from shutil import copyfile


def buildDocumentation():
    """
    Build eMonitor Documentation with sphinx

    :param sys.argv:

      * html: build html documentation in directory */docs/output/html*
      * pdf: build pdf documentation in directory */docs/output/pdf*

    """
    helptext = 'usage: build_doc.py <output format> <type of documentation>' \
               '\n - html: for html output' \
               '\n - pdf: for pdf output' \
               '\n\n - all: complete documentation' \
               '\n - dev: only developer documentation' \
               '\n - user: only user documentation'
    if len(sys.argv) != 3:
        print helptext
        sys.exit(1)

    if sys.argv[1] not in ['pdf', 'html']:
        print helptext
        sys.exit(1)
    if sys.argv[2] not in ['all', 'dev', 'user']:
        print helptext
        sys.exit(1)

    copyfile('docs/index_%s.rst.template' % sys.argv[2], 'index.rst')  # copy main file into root directory
    os.system('sphinx-build -b %s -c docs -D master_doc=index . docs/output/%s/%s' % (sys.argv[1], sys.argv[1], sys.argv[2]))
    os.remove('index.rst')  # delete config file from root directory

if __name__ == '__main__':
    buildDocumentation()
