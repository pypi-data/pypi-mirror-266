import os
import platform


if platform.system() == "Windows":
    home_word_list = ["USERPROFILE", "HOMEDRIVE", "HOMEPATH"]
    for home_word in home_word_list:
        if home_word in os.environ:
            path = os.path.join(os.environ[home_word], ".devcord", "data.db")
            break
    else:
        path = None
else:
    path = os.path.join(os.getenv("HOME"), ".devcord", "data.db")
