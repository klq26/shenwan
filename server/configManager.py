# -*- coding: utf-8 -*-
import os
import sys
import json

class configManager:

    def __init__(self):
        self.folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(self.folder, 'config.json'), 'r', encoding=u'utf-8') as f:
            self.config = json.loads(f.read())
        # print('current config: \n\n{0}'.format(self.config))
        pass

if __name__ == "__main__":
    cm = configManager()
    pass