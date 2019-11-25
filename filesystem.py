
import os
import datetime

def get_current_date_string():
    now = datetime.datetime.now()
    return "{yy}{mm:02d}{dd:02d}_{hh:02d}{min:02d}{sec:02d}".format(yy=now.year, mm=now.month, dd=now.day, hh=now.hour, min=now.minute, sec=now.second)

ROOT = os.path.join("./")
TODAY_STR = get_current_date_string()

HTML_EXTENSION = ".html"
EXTENSION_DIFF_VIEW = "_diffview" + HTML_EXTENSION

def get_root_log_path(run_dir):
    return os.path.join(ROOT, run_dir, "logs")
def get_root_html_path(run_dir):
    return os.path.join(ROOT, run_dir, "html")
def get_root_log_today_path(run_dir):
    return os.path.join(ROOT, run_dir, "logs", TODAY_STR)
def get_root_html_today_path(run_dir):
    return os.path.join(ROOT, run_dir, "html", TODAY_STR)

HOME_NAME = "clang-tidy-report"
INDEX_HTML_NAME = "index" + HTML_EXTENSION
CLANG_RESULT_PREFIX = "result_clang-tidy_"
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

FILES_DIRECTORY_NAME = "files"
CATEGORIES_DIRECTORY_NAME = "categories"
FILES_HTML_NAME = "files_issues" + HTML_EXTENSION
CATEGORIES_HTML_NAME = "categories_issues" + HTML_EXTENSION

GENERATION_SUMMARY_FILE = "generation_summary.log"

def get_current_clang_result_full_path(run_dir):
    return os.path.join(get_root_log_today_path(run_dir), "{0}{1}.txt".format(CLANG_RESULT_PREFIX, TODAY_STR))
def get_junction_root_html_full_path(run_dir):
    return os.path.join(get_root_html_path(run_dir), HOME_NAME)
def get_junction_root_log_full_path(run_dir):
    return os.path.join(get_root_log_path(run_dir), HOME_NAME)

def get_previous_clang_result(run_dir):
    root_log_dir = get_root_log_path(run_dir)
    dirs = sorted([d.name for d in os.scandir(root_log_dir) if d.is_dir()], reverse=True)
    today = datetime.date.today()
    for dir in dirs:
        if not dir[0:8].isdigit():
            continue
        year, month, day = dir[0:4], dir[4:6], dir[6:8]
        d = datetime.date(int(year), int(month), int(day))
        clang_path = os.path.join(root_log_dir, dir, "{0}{1}.txt".format(CLANG_RESULT_PREFIX, dir))
        # compare to yesterday at least, not necessarily the last run
        if d < today and os.path.exists(clang_path):
            return clang_path
    return None

def get_previous_html(run_dir):
    root_html_dir = get_root_html_path(run_dir)
    dirs = sorted([d.name for d in os.scandir(root_html_dir) if d.is_dir()], reverse=True)
    today = datetime.date.today()
    for dir in dirs:
        if not dir[0:8].isdigit():
            continue
        year, month, day = dir[0:4], dir[4:6], dir[6:8]
        d = datetime.date(int(year), int(month), int(day))
        html_path = os.path.join(root_html_dir, dir)
        if d < today and os.path.exists(html_path):
            return html_path
    return None

def create_index_html(run_dir, prev_date, timedelta_run):
    now = datetime.datetime.now()

    hours_run, remain = divmod(timedelta_run.seconds, 3600)
    mins_run, secs_run = divmod(remain, 60)

    body = """
    <h2>Report summary</h2>
    <br/>
    <p> Generated on: <b>{date}</b> (time spent: {hours_run}h{mins_run}m:{secs_run}s)</p>
    <br/>
    <br/>
    <br/>
    """.format(date="{0:02d}/{1:02d}/{2} - {3:02d}h{4:02d}m{5:02d}s".format(now.day, now.month, now.year, now.hour, now.minute, now.second),
               hours_run=hours_run, mins_run=mins_run, secs_run=secs_run)
    if prev_date:
        body += """
        <h2>Compared with</h2>
        <br/>
        <p> Previous run on: <b>{prev_date}</b> </p>
        """.format(prev_date=prev_date)

    common_head = HtmlRenderer.get_common_head("Clang-tidy analyzer")
    header = HtmlRenderer.get_header(True, False, False)
    content = HtmlRenderer.get_index(common_head, header, body)

    with open(os.path.join(get_root_html_today_path(run_dir), INDEX_HTML_NAME), "w+") as fd:
        fd.write(content)

###############################################################

def _get_file_content(path):
    content = ""
    with open(path, "r") as fd:
        content = fd.read()
    return content

class HtmlRenderer(object):

    TEMPLATE_DIR = os.path.join(SCRIPT_PATH, "templates")
    
    @staticmethod
    def get_common_head(title):
        path = os.path.join(HtmlRenderer.TEMPLATE_DIR, "common_head.html")
        return _get_file_content(path).format(title=title)
        
    @staticmethod
    def get_header(home_active, file_active, categorie_active):
        path = os.path.join(HtmlRenderer.TEMPLATE_DIR, "header.html")
        hactive = "active" if home_active is True else "inactive"
        factive = "active" if file_active is True else "inactive"
        cactive = "active" if categorie_active is True else "inactive"
        return _get_file_content(path).format(index_html=INDEX_HTML_NAME, files_html=FILES_HTML_NAME, categories_html=CATEGORIES_HTML_NAME,
        home_active=hactive, file_active=factive, categorie_active=cactive)

    @staticmethod
    def get_index(common_head, header, body):
        path = os.path.join(HtmlRenderer.TEMPLATE_DIR, "index.html")
        return _get_file_content(path).format(common_head=common_head, header=header, content=body)
