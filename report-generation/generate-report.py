import json
import os
import csv
import webbrowser
from html import escape

data = {}
json_folder = "../report-files/json_files"

#loads data from all present json files
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        version = os.path.splitext(filename)[0]
        file_path = os.path.join(json_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = json.load(f)
            data[version] = file_data[version]

checked_methods = {}
csv_folder = "../report-files/csv_reports"

#loads the review status from the csv files
for version in data:
    csv_file = os.path.join(csv_folder, f"{version}_methods.csv")
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f_csv:
            reader = csv.DictReader(f_csv)
            for row in reader:
                key = (row["version"], row["file_url"], row["method"])
                checked_methods[key] = (row["checked"].strip().lower() == "true")

output_dir = os.path.join("..", "report-files", "reports")
os.makedirs(output_dir, exist_ok=True)

custom_css = """
<style>
  body {
    background-color: #f8f9fa;
    padding: 2rem;
  }
  .card {
    margin-bottom: 1.5rem;
    border: none;
  }
  .card-header {
    background-color: #3230a1;
    color: white;
    font-weight: bold;
  }
  .card-header a {
    color: white;
  }
  .badge {
    font-size: 0.8rem;
    margin-left: 0.5rem;
  }
  /* Styles for new classes */
  .new-class-card {
    border: 1px solid #FF5733;
  }
  .new-class-header {
    background-color: #FF5733;
    color: white;
    font-weight: bold;
  }
</style>
"""

# HTML for the index page
index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JDK API Changes</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  {custom_css}
</head>
<body>
<div class="container">
  <h1>JDK API Changes</h1>
  <ul class="toc">
"""

#creates links and version pages (sorts versions in consecutive order)
for version in sorted(data.keys(), key=lambda v: int(v.split('-')[1])):
    # get the version filename (eg. jdk-18.html)
    version_filename = f"{version}.html"
    version_file = os.path.join(output_dir, version_filename)
    #link by file name
    index_content += f'    <li><a href="{version_filename}">JDK {version} API Changes</a></li>\n'

    version_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JDK {version} Changes</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  {custom_css}
</head>
<body>
<div class="container">
  <h1>JDK {version} Changes</h1>
  <!-- Since all pages are in the same folder, use a simple relative link -->
  <a href="index.html" class="back-link">← Back to all versions</a>
  <hr>
"""

    for file_url in data[version]:
        file_data = data[version][file_url]
        new_changes = file_data.get("new_changes", {})
        new_classes = new_changes.get("new_classes", [])
        new_methods = new_changes.get("new_methods", [])

        class_key = (version, file_url, "")
        if checked_methods.get(class_key, False):
            indicator = '<span class="badge bg-success">Checked</span>'
        else:
            indicator = '<span class="badge bg-warning text-dark">Not Checked</span>'

        version_content += f"""
        <div class="card">
          <div class="card-header">
            <a href="{file_url}" target="_blank">{file_url}</a> {indicator}
          </div>
          <div class="card-body">
        """

        #render all new classes by iterating over the new_classes list
        if new_classes:
            for cls in new_classes:
                #access elements stored in the json
                declaration = cls.get("declaration")
                methods = cls.get("methods", [])
                version_content += f'<div class="card mb-3 new-class-card">'
                #build key to get the checked status
                class_key = (version, file_url, cls.get("declaration"))
                if checked_methods.get(class_key, False):
                    indicator = '<span class="badge bg-success">Checked</span>'
                else:
                    indicator = '<span class="badge bg-warning text-dark">Not Checked</span>'
                version_content += f'<div class="card-header new-class-header">{escape(declaration)} {indicator}</div>'

                if methods:
                    version_content += '<ul class="list-group list-group-flush">'
                    for method in methods:
                        version_content += f'<li class="list-group-item">{escape(method)}</li>'
                    version_content += '</ul>'
                version_content += '</div>'

        if new_methods:
            version_content += '<ul class="list-group list-group-flush">'
            for method in new_methods:
                version_content += f'<li class="list-group-item">{escape(method)}</li>'
            version_content += '</ul>'

        version_content += """
          </div>
        </div>
        """
    version_content += """</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    with open(version_file, "w", encoding="utf-8") as f_out:
        f_out.write(version_content)

index_content += """  </ul>
  </div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
#index page into the output_dir (report-files/reports)
index_path = os.path.join(output_dir, "index.html")
with open(index_path, "w", encoding="utf-8") as f_index:
    f_index.write(index_content)

webbrowser.open("file://" + os.path.abspath(index_path))
