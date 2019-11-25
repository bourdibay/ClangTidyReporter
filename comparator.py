
"""
Compare two results and provide the differences.
"""

import os
import difflib
import uuid
import diff2html
import filesystem

TMP_DIFF_RESULT = "tmp_diff_file.tmp"

class Comparator(object):

    def get_nb_diff_files(self, prev_list_files, current_list_files):
        result = {}
        for prev_name, _ in prev_list_files.files.items():
            if prev_name in current_list_files.files.keys():
                result[prev_name] = len(current_list_files.files[prev_name].issues) - len(prev_list_files.files[prev_name].issues)
        return result

    def get_nb_diff_categories(self, prev_list_categories, current_list_categories):
        result = {}
        for prev_name, _ in prev_list_categories.categories.items():
            if prev_name in current_list_categories.categories.keys():
                result[prev_name] = len(current_list_categories.categories[prev_name].issues) - len(prev_list_categories.categories[prev_name].issues)
        return result

    def generate_all_diff_views(self, prev_html_files_dir, current_html_files_dir):
        prev_files = set(sorted([d.name for d in os.scandir(prev_html_files_dir) if d.is_file()], reverse=False))
        current_files = set(sorted([d.name for d in os.scandir(current_html_files_dir) if d.is_file()], reverse=False))
        list_diff_views = {}
        for curr_file in current_files:
            if curr_file in prev_files:
                diff_view = os.path.join(current_html_files_dir, curr_file + filesystem.EXTENSION_DIFF_VIEW)
                list_diff_views[curr_file] = diff_view
                self.generate_diff_file(os.path.join(current_html_files_dir, curr_file),
                                        os.path.join(prev_html_files_dir, curr_file),
                                        diff_view)
        return list_diff_views

    def generate_diff_file(self, file_recent, file_old, name_output_file):
        tmp_filename = TMP_DIFF_RESULT + str(uuid.uuid4()) + ".txt"

        with open(file_recent, "r") as fd_recent:
            with open(file_old, "r") as fd_old:
                c1 = fd_recent.readlines()
                c2 = fd_old.readlines()
                diff = difflib.unified_diff(c1, c2, fromfile=file_recent, tofile=file_old)
                
                content = "".join(diff)

                with open(tmp_filename, "w+") as fd:
                    fd.write(content)
                
        with open(tmp_filename, "r") as fd_in:
            with open(name_output_file, "w+") as fd_out:
                diff2html.parse_input(fd_in, fd_out, tmp_filename, name_output_file, False, True)
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
