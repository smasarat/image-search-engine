import pickle
import logging


class PickleActions(object):
    def __init__(self, target_path):
        self.target_path = target_path

    def save_pickle(self, content):
        try:
            with open("{}".format(self.target_path), 'wb') as f:
                pickle.dump(content, f, protocol=pickle.HIGHEST_PROTOCOL,)
        except Exception as e:
            logging.exception(e)

    def load_pickle(self, file_name=None):
        try:
            if file_name is None:
                return pickle.load(open("{}".format(self.target_path), 'rb'))
            else:
                return pickle.load(open("{}/{}".format(self.target_path, file_name), 'rb'))
        except Exception as e:
            logging.exception(e)


def test_save_pickle():
    _pickle_actions = PickleActions(target_path="../data/source_list.pkl")
    source_text_list = [1,2,3,4]
    _pickle_actions.save_pickle(content=source_text_list)


def test_load_pickle():
    _pickle_actions = PickleActions(target_path="../data/source_list.pkl")
    tmp_pickle = _pickle_actions.load_pickle()
    print(len(tmp_pickle), tmp_pickle[0])
