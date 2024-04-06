"""Utils for dol_coobook"""

from importlib.resources import files

pkg_name = 'dol_cookbook'

pkg_files = files(pkg_name)
pkg_data_path = str(pkg_files)

pkg_data_files = pkg_files / 'data'

misc_files_path = str(pkg_data_files / 'misc_files')
