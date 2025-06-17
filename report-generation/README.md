JDK API Changes Report Generation

Tina Xia, tzxia@uwaterloo.ca for issues or questions
Friday, April 2, 2025

This project automates the review process for newly introduced methods across subsequent JDK versions.

-----------

Configuration

PERFORMING MINIMIZATION AND STORING RESULTS
1. Create a sub-directory called "results" in the "report-generation" directory

2. Update the absolute paths in config.py to match your environment:

JDK_REPO_PATH: path to your local JDK repository.
CHECKER_FRAMEWORK_REPO_PATH: path to your local Checker Framework repository.
RESULTS_BASE_DIR: path to the "results" sub-directory you just created

3. run minimization script:
- python3 perform-minimization.py
- This will generate and store the minimized files for each jdk version in "results"

GENERATE DIFF JSONS
4. run JSON generation script:
- python3 generate-json.py
- This will compare and store differences between files in a sub-directory called json_files in a directory called "report-files"
- This script can be modified to only generate JSON's for a defined sub-set of minimized files by altering the versions array in the processing portion

GENERATE CSVs
5. run CSV generation script:
- python3 generate-csv.py
- This will generate a csv tracker for the review status of classes by iterating over the JSON files generated in the previous step
- NOTE: when introducing a new jdk version, this file must be modified to generate a CSV for ONLY the newly introduced jdk version, or past CSVs will be completely reset.

GENERATE HTML Report
6. run HTML report generation script:

- python3 generate-report.py
- this creates and opens a report in your browser, loading in information from the CSVs and JSONs generated in the previous step

-----------

Use

Once a method has been reviewed, updated the final column in each row "checked" by changing the entry from "False" to "True". The next time the report generation script is run, a tag will appear on the report that indicates its updated status. You must re-run the report generation script "python3 generate-report.py" to see the changes.

-----------

Future Updates

New JDK Versions:
When a new JDK version is released, update the branch list in the scripts to only include the newly introuced versions. This ensures that processing a new branch does not overwrite progress in previous versions.