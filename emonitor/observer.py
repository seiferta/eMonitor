import os
import logging
from .extensions import events, classes

logger = logging.getLogger(__name__)
BEFORE = AFTER = {}

events.addEvent('file_added', handlers=[], parameters=['out.incomepath', 'out.filename'])
events.addEvent('file_removed', handlers=[], parameters=['out.incomepath', 'out.filename'])

OBSERVERACTIVE = 1
ERROR_RAISED = 0

FILES = []


def observeFolder(**kwargs):
    """
    Observer method to observe given folder
    :param kwargs:
    """
    global BEFORE, AFTER, FILES, ERROR_RAISED

    if OBSERVERACTIVE == 0:
        return
    
    if 'path' in kwargs:
        path = kwargs['path']
    else:
        return
        
    if not os.path.exists(path):
        if ERROR_RAISED == 0:
            ERROR_RAISED = 1
            logger.error('observer path %s not found' % path)
        return  # error delivered
    elif ERROR_RAISED == 1:  # path found again
        ERROR_RAISED = 0
        logger.info('observer path {} present again'.format(path))

    if ERROR_RAISED == 1:
        ERROR_RAISED = 0  # reset errorstate
        
    AFTER = dict([(f, None) for f in os.listdir(path)])
    for a in [f for f in AFTER if f not in BEFORE and os.path.splitext(f)[-1][1:] in classes.get('settings').get('ocr.inputformat', ['pdf']) + classes.get('settings').get('ocr.inputtextformat', [])]:  # new files added
        if a not in FILES:
            events.raiseEvent('file_added', dict({'incomepath': path, 'filename': a}))
            logger.info('file_added: %s%s' % (path, a))
            FILES.append(a)
    
    for r in [f for f in BEFORE if f not in AFTER and os.path.splitext(f)[-1][1:] in classes.get('settings').get('ocr.inputformat', ['pdf']) + classes.get('settings').get('ocr.inputtextformat', [])]:
        if r in FILES:
            events.raiseEvent('file_removed', dict({'incomepath': path, 'filename': r}))
            logger.info('file_removed: %s%s' % (path, r))
            FILES.remove(r)
            
    BEFORE = AFTER
    return
