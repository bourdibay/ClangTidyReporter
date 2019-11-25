
import shutil
import os
import filesystem

LINE_SEPARATOR = "======================================================================================================================================================================================\n"

def _recreate_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

def print_column_trend(diff_nb_issues, name):
    trend = "new"
    color = "black"
    if diff_nb_issues and name in diff_nb_issues.keys():
        trend = diff_nb_issues[name]
        if trend > 0:
            color = "red"
            trend = "+" + str(trend)
        elif trend < 0:
            color = "green"
            trend = str(trend)
        else:
            color = "blue"
            trend = "="
    return "    <td style=\"color:{color} ; min-width:50px ; text-align:center\">{trend}</td>\n".format(color=color, trend=trend)

def print_column_diff_view(diff_view, txt_file, root_dir):
    base_txt_file = os.path.basename(txt_file)
    if base_txt_file in diff_view.keys():
        filename = os.path.join(root_dir, os.path.basename(diff_view[base_txt_file]))
        return "<td style=\"min-width:50px ; text-align:center\"><a href={0}>View diff</a></td>\n".format(filename)
    return ""

def print_nb_issues_column(nb):
    return "    <td style=\"min-width:50px; text-align:center\">{0}</td>\n".format(nb)

class FilesPrinter(object):

    def __init__(self, root_dir):
        self.root_dir = root_dir
        _recreate_directory(os.path.join(root_dir, filesystem.FILES_DIRECTORY_NAME))

    def dump_html(self, list_files, diff_nb_issues=None, diff_views=None):
        body = """<div>
        <table class=\"table table-bordered table-hover table-striped\">
        <thead>
        <tr>
        <th style=\"text-align:center\">Filenames</th>
        <th style=\"text-align:center\">Number issues</th>
        <th style=\"text-align:center\">Trends</th>
        <th style=\"text-align:center\">Diff visualizer</th>
        </thead>
        </tr>
        <tbody>
        """
        for name, file in list_files.files.items():
            body += "    <tr>\n"
            filename = os.path.join(filesystem.FILES_DIRECTORY_NAME, os.path.splitext(os.path.basename(os.path.abspath(name)))[0] + ".txt")
            body += "    <td><a href={0}>{1}</a></td>\n".format(filename, name)
            body += print_nb_issues_column(len(file.issues))
            if diff_nb_issues:
                body += print_column_trend(diff_nb_issues, name)
            if diff_views:
                body += print_column_diff_view(diff_views, filename, filesystem.FILES_DIRECTORY_NAME)
            body += "    </tr>\n"
        body += """</tbody>
        </table>
        </div>"""

        common_head = filesystem.HtmlRenderer.get_common_head("Issues by files")
        header = filesystem.HtmlRenderer.get_header(False, True, False)
        content = filesystem.HtmlRenderer.get_index(common_head, header, body)
        with open(os.path.join(self.root_dir, filesystem.FILES_HTML_NAME), "w+") as fd_files:
            fd_files.write(content)

    def dump_files(self, list_files):
        for name, file in list_files.files.items():
            filename = os.path.join(filesystem.FILES_DIRECTORY_NAME, os.path.splitext(os.path.basename(os.path.abspath(name)))[0] + ".txt")
            full_path = os.path.join(self.root_dir, filename)
            with open(full_path, "w+") as fd_txt:
                for issue in file.issues:
                    fd_txt.write(issue.desc)
                    fd_txt.write(LINE_SEPARATOR)

class CategoriesPrinter(object):

    def __init__(self, root_dir):
        self.root_dir = root_dir
        _recreate_directory(os.path.join(root_dir, filesystem.CATEGORIES_DIRECTORY_NAME))

    def dump_html(self, list_categories, diff_nb_issues=None, diff_views=None):
        body = """<div>
        <table class=\"table table-bordered table-hover table-striped\">
        <thead>
        <tr>
        <th style=\"text-align:center\">Categories</th>
        <th style=\"text-align:center\">Number issues</th>
        <th style=\"text-align:center\">Trends</th>
        <th style=\"text-align:center\">Diff visualizer</th>
        </thead>
        </tr>
        <tbody>
        """
        for name, categorie in list_categories.categories.items():
            body += "    <tr>\n"
            filename = os.path.join(filesystem.CATEGORIES_DIRECTORY_NAME, name + ".txt")
            body += "    <td><a href={0}>{1}</a></td>\n".format(filename, name)
            body += print_nb_issues_column(len(categorie.issues))
            if diff_nb_issues:
                body += print_column_trend(diff_nb_issues, name)
            if diff_views:
                body += print_column_diff_view(diff_views, filename, filesystem.CATEGORIES_DIRECTORY_NAME)
            body += "    </tr>\n"

        body += """</tbody>
        </table>
        </div>"""

        common_head = filesystem.HtmlRenderer.get_common_head("Issues by categories")
        header = filesystem.HtmlRenderer.get_header(False, False, True)
        content = filesystem.HtmlRenderer.get_index(common_head, header, body)
        with open(os.path.join(self.root_dir, filesystem.CATEGORIES_HTML_NAME), "w+") as fd_cat:
            fd_cat.write(content)

    def dump_categories(self, list_categories):
        for name, categorie in list_categories.categories.items():
            filename = os.path.join(filesystem.CATEGORIES_DIRECTORY_NAME, name + ".txt")
            full_path = os.path.join(self.root_dir, filename)
            with open(full_path, "w+") as fd_txt:
                for issue in categorie.issues:
                    fd_txt.write(issue.desc)
                    fd_txt.write(LINE_SEPARATOR)
