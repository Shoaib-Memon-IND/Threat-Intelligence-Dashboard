import os
import pickle
import numpy as np
from keras._tf_keras.keras.models import load_model
from androguard.core.apk import APK
from genetic_algorithm import GeneticSelector


class CustomUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        try:
            return super().find_class(__name__, name)
        except AttributeError:
            return super().find_class(module, name)


sel = CustomUnpickler(open('./static/models/ga.pkl', 'rb')).load()

permissions = []
with open('./static/permissions.txt', 'r') as f:
    content = f.readlines()
    for line in content:
        cur_perm = line[:-1]
        permissions.append(cur_perm)


def classify(file, ch):
    vector = {}
    result = 0
    name, sdk, size = 'unknown', 'unknown', 'unknown'
    app = APK(file)
    perm = app.get_permissions()
    name, sdk, size = meta_fetch(file)
    for p in permissions:
        if p in perm:
            vector[p] = 1
        else:
            vector[p] = 0
    data = [v for v in vector.values()]
    data = np.array(data)
    if ch == 0:
        ANN = load_model('static/models/ANN.h5')
        #print(data)
        result = ANN.predict(np.array([data[sel.support_]]))
        print(result)

        if result < 0.02:
            result = 'Benign(safe)'
        else:
            result = 'Malware'
    return result, name, sdk, size


def meta_fetch(apk):
    app = APK(apk)
    return app.get_app_name(), app.get_target_sdk_version(), str(round(os.stat(apk).st_size / (1024 * 1024), 2)) + ' MB'
