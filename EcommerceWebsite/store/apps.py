from django.apps import AppConfig
from django.conf import settings
import os
import pickle

class StoreConfig(AppConfig):
    path = os.path.join(settings.MODELS, 'model.p')

    with open(path, 'rb') as pickled:
        data = pickle.load(pickled)
    classifier = data['classifier']
    def ready(self):
        import store.signals


