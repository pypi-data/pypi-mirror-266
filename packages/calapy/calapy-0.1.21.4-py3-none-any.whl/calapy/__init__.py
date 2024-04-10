import datetime
import importlib

__version__ = '0.1.21.4'

__release_day__ = 9
__release_month_num__ = 4
__release_year__ = 2024


__release_date_object__ = datetime.date(__release_year__, __release_month_num__, __release_day__)
__release_date__ = __release_date_object__.__format__('%d %B %Y')
__release_month_name__ = __release_date_object__.__format__('%B')
del datetime

__author__ = 'Calafiore Carmelo'
__author_email__ = 'carmelo.calafiore@newcastle.ac.uk'
__maintainer_email__ = 'carmelo.calafiore@newcastle.ac.uk'

submodules = [
    'array', 'check', 'clock', 'combinations', 'directory', 'download',
    'format', 'image', 'lists', 'maths', 'mixamo', 'ml', 'pkl', 'plot', 'preprocessing',
    'shutdown', 'stats', 'stimulation', 'strings', 'threading', 'txt']
others = []
__all__ = submodules + others

for sub_module_m in submodules:
    importlib.import_module(name='.' + sub_module_m, package=__package__)
