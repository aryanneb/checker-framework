import json
import os
import csv

csv_folder = "../report-files/csv_reports"
os.makedirs(csv_folder, exist_ok=True)

data = {}
json_folder = "../report-files/json_files"
os.makedirs(csv_folder, exist_ok=True)

json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

#this list must be modified for newly added jdk versions, so that past versions are not overwitten with every method review status set to False
versions_to_process = ['jdk-18', 'jdk-19', 'jdk-20', 'jdk-21', 'jdk-22', 'jdk-23', 'jdk-24']

for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        version = os.path.splitext(filename)[0]
        #processes only the versions in the versions_to_process list
        if version not in versions_to_process:
            continue
        file_path = os.path.join(json_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = json.load(f)
            data[version] = file_data[version]

for version in data:
    #gets current csv path
    current_csv = os.path.join(csv_folder, f"{version}_methods.csv")
    with open(current_csv, "w", newline='', encoding="utf-8") as csvfile:

        fieldnames = ["version", "file_url", "method", "checked"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        #since methods are grouped by file_url in the methods json
        for file_url, file_data in data[version].items():
            new_changes = file_data.get("new_changes", {})
            new_classes = new_changes.get("new_classes", [])
            new_methods = new_changes.get("new_methods", [])

            writer.writerow({
                    "version": version,
                    "file_url": file_url,
                    "checked": "False"
                })

            # Write new class methods
            for cls in new_classes:
                declaration = cls.get("declaration")

                #store checked status for newly introduced classes
                writer.writerow({
                    "version": version,
                    "file_url": file_url,
                    "method": cls.get("declaration"),
                    "checked": "False"
                })

    print(f"Created csv for {version}")
