import os
from .extensions import events, classes

BEFORE = AFTER = {}

events.addEvent('file_added', handlers=[], parameters=['out.incomepath', 'out.filename'])
events.addEvent('file_removed', handlers=[], parameters=['out.incomepath', 'out.filename'])

OBSERVERACTIVE = 1
ERROR_RAISED = 0

FILES = []


def observeFolder(**kwargs):
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
            raise ValueError('observer path %s not found' % path)
        return  # error delivered

    if ERROR_RAISED == 1:
        ERROR_RAISED = 0  # reset errorstate
        
    AFTER = dict([(f, None) for f in os.listdir(path)])
    for a in [f for f in AFTER if not f in BEFORE and os.path.splitext(f)[-1][1:] in classes.get('settings').get('ocr.inputformat', ['pdf'])]:  # new files added
        if a not in FILES:
            events.raiseEvent('file_added', dict({'incomepath': path, 'filename': a}))
            FILES.append(a)
    
    for r in [f for f in BEFORE if not f in AFTER and os.path.splitext(f)[-1][1:] in classes.get('settings').get('ocr.inputformat', ['pdf'])]:
        if r in FILES:
            events.raiseEvent('file_removed', dict({'incomepath': path, 'filename': r}))
            FILES.remove(r)
            
    BEFORE = AFTER
    return
