from cornice.service import Service
from pyramid.config import Configurator
from pyramid.events import NewRequest

random_settings = Service('random_settings', path='/random_settings')
behavior = Service('behavior', path='/behavior')
behaviors = Service('behaviors', path='/behaviors')


@random_settings.put()
def set_random_settings(request):
    try:
        data = request.json
        name = data['settings']
    except ValueError:
        request.errors.add('body', '',
                           'the value is not a valid json object')
    except KeyError:
        request.errors.add('body', '',
                           'the value should contain a "settings" key')
    else:
        try:
            request.proxy.set_random_settings(**data)
        except KeyError:
            request.errors.add('body', 'settings',
                               "the '%s' behavior does not exist" % name)
    return {'status': 'ok'}

@random_settings.get()
def get_random_settings(request):
    return {'settings': request.proxy.settings.getsection('vaurien')['behavior']}

@behavior.put()
def set_behavior(request):
    try:
        data = request.json
        name = data['name']
    except ValueError:
        request.errors.add('body', '',
                           'the value is not a valid json object')
    except KeyError:
        request.errors.add('body', '',
                           'the value should contain a "name" key')
    else:
        try:
            request.proxy.set_behavior(**data)
        except KeyError:
            request.errors.add('body', 'name',
                               "the '%s' behavior does not exist" % name)
    return {'status': 'ok'}


@behavior.get()
def get_behavior(request):
    return {'behavior': request.proxy.get_behavior()[1]}


@behaviors.get()
def get_behaviors(request):
    return {'behaviors': request.proxy.get_behavior_names()}


def add_proxy_to_request(event):
    event.request.proxy = event.request.registry['proxy']


def get_config(global_config=None, **settings):
    if global_config is None:
        global_config = {}
    config = Configurator(settings=settings)
    config.include('cornice')
    config.scan('vaurien.webserver')

    config.add_subscriber(add_proxy_to_request, NewRequest)
    return config
