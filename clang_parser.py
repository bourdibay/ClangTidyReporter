
import sys
import os
import re
import collections

LINE_SCANNED_TAG = "File scanned: "

class ClangFileParser(object):
    
    def _is_file_scanned(self, line):
        return line.startswith(LINE_SCANNED_TAG)

    def _get_file_scanned(self, line):
        return line[len(LINE_SCANNED_TAG):].replace('\n', '').strip()
        
    def _get_check_categorie(self, issue_desc):
        for line in issue_desc.split('\n'):
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            m = re.match(r".*\[(.*)\]$", line)
            if m:
                return m.group(1) if m else "_____Badly_parsed_____"
        return "Fail"

###############################################

class ListFiles(object):
    def __init__(self):
        self.files = {}

    def add_file(self, file):
        self.files[file.fullpath] = file

    def remove_file(self, file):
        del self.files[file.fullpath]

    def sort(self):
        self.files = collections.OrderedDict(sorted(self.files.items(), key=lambda t: t[0]))

    def _build_list_files(self, fd):
        current_file = None
        parser = ClangFileParser()

        for line in fd:
            line = line.decode("latin1") # because of French comments...
            if parser._is_file_scanned(line):
                if current_file and len(current_file.issues) == 0:
                    self.remove_file(current_file)
                current_file = File(parser._get_file_scanned(line))
                self.add_file(current_file)
            elif current_file:
                if any(tag in line for tag in ["warning:", "error:"]):
                    issue = Issue(line)
                    current_file.add_new_issue(issue)
                else:
                    current_file.get_last_issue().add_desc(line)

        if current_file and len(current_file.issues) == 0:
            self.remove_file(current_file)

    @staticmethod
    def from_clang_result(result_file):
        list_files = ListFiles()
        if not result_file:
            return list_files
        try:
            with open(result_file, 'rb') as fd:
                list_files._build_list_files(fd)
                list_files.sort()
        except:
            return None
        return list_files
       
        
class File(object):
    def __init__(self, fullpath):
        self.fullpath = os.path.normcase(fullpath)
        self.issues = []

    def get_last_issue(self):
        return self.issues[-1]

    def add_new_issue(self, issue):
        self.issues.append(issue)

class Issue(object):
    def __init__(self, desc):
        self.desc = desc

    def add_desc(self, desc):
        self.desc += desc

###############################################

class ListCategories(object):
    def __init__(self):
        self.categories = {}

    def add_categorie(self, name, issue):
        if name in self.categories.keys():
            self.categories[name].add_issue(issue)
        else:
            self.categories[name] = Categorie(name)
            self.categories[name].add_issue(issue)

    def sort(self):
        self.categories = collections.OrderedDict(sorted(self.categories.items(), key=lambda t: t[0]))

    @staticmethod
    def from_list_files(list_files):
        parser = ClangFileParser()
        categories = ListCategories()
        if not list_files:
            return categories
        for _, file in list_files.files.items():
            for issue in file.issues:
                name_categorie = parser._get_check_categorie(issue.desc)
                categories.add_categorie(name_categorie, issue)
        categories.sort()
        return categories

class Categorie(object):
    def __init__(self, name):
        self.name = name
        self.issues = []

    def add_issue(self, issue):
        self.issues.append(issue)
