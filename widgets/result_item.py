import os
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'result_item.kv'))


class ResultItem(BoxLayout):

    sn = StringProperty()
    chracters = StringProperty()
    confidence = StringProperty()
    recog_time = StringProperty()

    def __init__(self, sn, chracters, confidence, recog_time):
        super(ResultItem, self).__init__()
        self.sn = sn
        self.chracters = chracters
        self.confidence = confidence
        self.recog_time = recog_time
