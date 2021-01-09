# -*- encoding: utf-8 -*-
"""
License: Commercial
Copyright (c) 2019 - present AppSeed.us
"""

import os
from sys import exit

from app import app
from app.routes import write_munro_json
import multiprocessing as mp

if __name__ == "__main__":

    p = mp.Process(target=write_munro_json)
    p.start()

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

    p.join()
