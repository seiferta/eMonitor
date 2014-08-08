from flask import render_template, request
from emonitor.extensions import classes, db, events


def getAdminContent(self, **params):
    module = request.view_args['module'].split('/')
    
    if len(module) > 1:
        pass
        
    else:
        if request.method == 'POST':
            if request.form.get('action').startswith('edithandler_'):  # edit handler
                handler = classes.get('eventhandler').getEventhandlers(id=int(request.form.get('action').split('_')[-1]))  # handler defined in db
                handlers = events.getEvents(name=handler.event).getHandlerList()  # all possible handlers for given event
                params.update({'handler': handler, 'handlers': handlers})
                return render_template('admin.events_actions.html', **params)

            elif request.form.get('action').startswith('createhandler_'):  # add handler
                handler = classes.get('eventhandler')(request.form.get('action').replace('createhandler_', ''), '', '', '')
                handlers = events.getEvents(name=handler.event).getHandlerList()  # all possible handlers for given event
                params.update({'handler': handler, 'handlers': handlers})
                return render_template('admin.events_actions.html', **params)

            elif request.form.get('action') == 'updateeventhandler':  # save handler
                if request.form.get('handler_id') != 'None':  # update
                    hdl = classes.get('eventhandler').getEventhandlers(id=request.form.get('handler_id'))
                    hdl.position = request.form.get('edit_position')
                
                else:  # add
                    existing = classes.get('eventhandler').getEventhandlers(event=request.form.get('edit_event'))
                    hdl = classes.get('eventhandler')(request.form.get('edit_event'), '', '', '')
                    db.session.add(hdl)
                    hdl.position = len(existing) + 1
                    
                hdl.handler = request.form.get('edit_handler')
                hdl.parameters = ''
                for k in request.form.keys():
                    if k.startswith('check.in'):  # in parameters
                        if request.form.get(k) == "alternative":  # use alternative text field
                            hdl.parameters += '%s=%s\r\n' % (k[6:], request.form.get('in.' + k[9:]))
                        else:
                            hdl.parameters += '%s=%s\r\n' % (k[6:], request.form.get(k))  # use checkbox

                    elif k.startswith('check.out'):  # out parameters
                        if request.form.get(k) == "alternative":  # use alternative text field
                            hdl.parameters += '%s=%s\r\n' % (k[6:], request.form.get('out.' + k[10:]))
                        else:
                            hdl.parameters += '%s=%s\r\n' % (k[6:], request.form.get(k))  # use checkbox
                db.session.commit()

            elif request.form.get('action').startswith('deletehandler_'):  # delete handler
                handler = classes.get('eventhandler').getEventhandlers(id=int(request.form.get('action').split('_')[-1]))
                db.session.delete(handler)
                db.session.commit()
                
            elif request.form.get('action') == 'updateorder':  # update order of handlers/event
                for item in [i for i in request.form if i.startswith('position_')]:
                    ids = request.form.getlist(item)
                    for _id in ids:
                        hdl = classes.get('eventhandler').getEventhandlers(id=_id)
                        hdl.position = ids.index(_id) + 1
                db.session.commit()
        params.update({'events': events.getEvents()})
        return render_template('admin.events.html', **params)

    
def getAdminData(self, **params):
    
    if request.args.get('action') == 'getparams':  # event handler parameter sub form
        event = events.getEvents(name=request.args.get('event'))
        if request.args.get('handler') != '':
            handler = [hdl for hdl in event.getHandlerList() if hdl[0] == request.args.get('handler')][0]  # defined
        else:
            return "- error, no handler given -"

        if request.args.get('id') != 'None':
            eventhandler = classes.get('eventhandler').getEventhandlers(request.args.get('id'))  # db
        else:
            eventhandler = classes.get('eventhandler')(request.args.get('event'), '', '', '')  # db
            
        # previous parameters
        inparameters = eventhandler.getInParameters()
        return render_template('admin.events_data.html', handler=handler, eventhandler=eventhandler, inparameters=inparameters)

    return ""
