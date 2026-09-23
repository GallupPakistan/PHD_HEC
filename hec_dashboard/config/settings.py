import os

APP_NAME = "HEC Dashboard"
APP_SUBTITLE = "Higher Education Analytics"
PAGE_ICON = "🎓"
LAST_UPDATED = "22 Sep 2026"

# config/settings.py -> hec_dashboard/ is one level up from this file's folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(BASE_DIR, "HEIS_Data.xlsx")
ENROLMENT_DATA_FILE = os.path.join(BASE_DIR, "Enrolment_Data.xlsx")
DISCIPLINE_DATA_FILE = os.path.join(BASE_DIR, "Discipline_Data.xlsx")
FACULTY_DATA_FILE = os.path.join(BASE_DIR, "Faculty_Data.xlsx")
PASSOUT_DATA_FILE = os.path.join(BASE_DIR, "Passout_Data.xlsx")
PHD_DIRECTORY_DATA_FILE = os.path.join(BASE_DIR, "PhD_Directory_Data.xlsx")
