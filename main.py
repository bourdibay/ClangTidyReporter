#!/usr/env python3

"""
Generate clang-tidy report.
"""

import os
import sys
import logging
import datetime
import argparse
import shutil

import filesystem
import clang_parser
import comparator
import clang_tidy
import printer

from typing import List

def init_logger(output_dir: str):
    log_path = os.path.join(filesystem.get_root_log_today_path(output_dir), 'Run_{0}.log'.format(filesystem.TODAY_STR))
    logger = logging.getLogger("Run")
    hdlr = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger

def run_clang_tidy(output_dir: str, files: List[str], compilation_db: str, clang_checks: str, logger):
    with open(filesystem.get_current_clang_result_full_path(output_dir), "w+") as fd:
        for file in files:
            logger.info("Run clang-tidy on {0} ...".format(file))
            success = clang_tidy.generate_output(fd, file, compilation_db, clang_checks, logger)
            logger.info("... Done")

def get_all_clang_sources(files: str, directories: str, logger):
    def _get_all_files(directory: str):
        return [os.path.abspath(os.path.join(root, file)) for root, _, files in os.walk(directory) for file in files if os.path.splitext(file)[1] in ['.cpp', '.c', '.cxx']]

    clang_sources = []
    if files:
        clang_sources = files.split(',')

    if directories:
        for dir in directories.split(','):
            if os.path.isdir(dir):
               clang_sources.extend(_get_all_files(dir))
            else:
                logger.error('Cannot get files from {0}'.format(dir))
    return clang_sources

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--checks', help='clang-tidy checks')
    parser.add_argument('-p','--compilation_db', help='clang-tidy compilation_db path (directory)')
    parser.add_argument('-o','--output_dir')
    sources = parser.add_argument_group('Sources', 'The files of directories to scan')
    sources.add_argument('-f','--files', help='files to scan, separated by a comma')
    sources.add_argument('-d','--directories', help='directories to scan, separated by a comma')
    arguments = parser.parse_args()

    clang_checks = arguments.checks.strip()
    compilation_db = arguments.compilation_db
    files = arguments.files
    directories = arguments.directories
    output_dir = arguments.output_dir

    start_run = datetime.datetime.now()

    root_log_today_path = filesystem.get_root_log_today_path(output_dir)
    if not os.path.exists(root_log_today_path):
        os.makedirs(root_log_today_path)

    # Logging init
    logger = init_logger(output_dir)

    # Run clang-tidy
    clang_sources = get_all_clang_sources(files, directories, logger)
    run_clang_tidy(output_dir, clang_sources, compilation_db, clang_checks, logger)

    # Html directory
    root_html_today_path = filesystem.get_root_html_today_path(output_dir)
    if not os.path.exists(root_html_today_path):
        os.makedirs(root_html_today_path)

    # Generate report
    logger.info("Analyze result and generate text files for each file/categorie...")
    clang_results_path = filesystem.get_current_clang_result_full_path(output_dir)
    current_list_files = clang_parser.ListFiles.from_clang_result(clang_results_path)
    current_list_categories = clang_parser.ListCategories.from_list_files(current_list_files)

    files_printer = printer.FilesPrinter(root_html_today_path)
    categories_printer = printer.CategoriesPrinter(root_html_today_path)
    files_printer.dump_files(current_list_files)
    categories_printer.dump_categories(current_list_categories)

    logger.info("...Done")

    # Get previous clang result to make a diff
    logger.info("Get previous clang result...")
    previous_clang_result_filename = filesystem.get_previous_clang_result(output_dir)
    logger.info("...Got {0}".format(previous_clang_result_filename))

    previous_list_files = clang_parser.ListFiles.from_clang_result(previous_clang_result_filename)
    previous_list_categories = clang_parser.ListCategories.from_list_files(previous_list_files)

    # Compare
    logger.info("Compare previous and current results => {0} with {1} ...".format(previous_clang_result_filename, clang_results_path))
    logger.debug("Previous list files = {0}".format(previous_list_files.files))
    logger.debug("Current list files = {0}".format(current_list_files.files))
    logger.debug("Previous list categories = {0}".format(previous_list_categories.categories))
    logger.debug("Current list categories = {0}".format(current_list_categories.categories))
    cmp_results = comparator.Comparator()
    diff_nb_issues_files = cmp_results.get_nb_diff_files(previous_list_files, current_list_files)
    diff_nb_issues_categories = cmp_results.get_nb_diff_categories(previous_list_categories, current_list_categories)
    logger.debug("Diff nb issues files = {0}".format(str(diff_nb_issues_files)))
    logger.debug("Diff nb issues categories = {0}".format(str(diff_nb_issues_categories)))
    
    current_files_dir = os.path.join(root_html_today_path, filesystem.FILES_DIRECTORY_NAME)
    current_categories_dir = os.path.join(root_html_today_path, filesystem.CATEGORIES_DIRECTORY_NAME)
    prev_html_dir = filesystem.get_previous_html(output_dir)
    logger.info("Previous html dir is: {0}".format(prev_html_dir))
    list_diff_views_files = None
    list_diff_views_categories = None
    if prev_html_dir:
        previous_files_dir = os.path.join(prev_html_dir, filesystem.FILES_DIRECTORY_NAME)
        list_diff_views_files = cmp_results.generate_all_diff_views(previous_files_dir, current_files_dir)
        previous_categories_dir = os.path.join(prev_html_dir, filesystem.CATEGORIES_DIRECTORY_NAME)
        list_diff_views_categories = cmp_results.generate_all_diff_views(previous_categories_dir, current_categories_dir)
    logger.info("...Done")

    # Get summary log file
    logger.info("Retrieve summary log file from previous run...")
    previous_gen_date = ""
    if previous_clang_result_filename:
        try:
            with open(os.path.join(os.path.dirname(previous_clang_result_filename), filesystem.GENERATION_SUMMARY_FILE), "r") as fd:
                previous_gen_date = fd.readline().split(':')[1].strip()
        except Exception as e:
            logger.error("Exception: {0}".format(e))
    logger.info("...Done")

    # Dump html files
    logger.info("Dump html files...")
    files_printer.dump_html(current_list_files, diff_nb_issues_files, list_diff_views_files)
    categories_printer.dump_html(current_list_categories, diff_nb_issues_categories, list_diff_views_categories)
    end_run = datetime.datetime.now()
    filesystem.create_index_html(output_dir, previous_gen_date, end_run - start_run)
    logger.info("...Done")

    # Write summary log file
    logger.info("Generating summary log file...")
    with open(os.path.join(filesystem.get_root_log_today_path(output_dir), filesystem.GENERATION_SUMMARY_FILE), "w+") as fd:
        pretty_date = "{day}/{month}/{year} - {hour}h{min}m{sec}s".format(year=filesystem.TODAY_STR[0:4], 
                                                                          month=filesystem.TODAY_STR[4:6],
                                                                          day=filesystem.TODAY_STR[6:8],
                                                                          hour=filesystem.TODAY_STR[9:11],
                                                                          min=filesystem.TODAY_STR[11:13],
                                                                          sec=filesystem.TODAY_STR[13:15])
        fd.write("DATE:{0}\n".format(pretty_date))
    logger.info("...Done")

    logger.info("FINISHED !")

if __name__ == "__main__":
    main()
