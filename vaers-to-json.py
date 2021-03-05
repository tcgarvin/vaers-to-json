from csv import DictReader
from io import TextIOWrapper
import json
from pathlib import Path
from zipfile import ZipFile

def transform_zip_file(source_file : Path):
    with ZipFile(source_file) as vaers_zip:
        data_filename = None
        symptoms_filename = None
        vax_filename = None
        for file_name in vaers_zip.namelist():
            if file_name.lower().endswith("data.csv"):
                data_filename = file_name
            elif file_name.lower().endswith("symptoms.csv"):
                symptoms_filename = file_name
            elif file_name.lower().endswith("vax.csv"):
                vax_filename = file_name

        reports_by_id = {}
        with vaers_zip.open(data_filename) as data_file:
            reader = DictReader(TextIOWrapper(data_file, encoding="latin-1"))
            for row in reader:
                row["symptoms"] = []
                row["vax"] = []
                reports_by_id[row["VAERS_ID"]] = row

        with vaers_zip.open(symptoms_filename) as symptoms_file:
            reader = DictReader(TextIOWrapper(symptoms_file, encoding="latin-1"))
            for row in reader:
                report = reports_by_id[row["VAERS_ID"]]
                report["symptom_version"] = row["SYMPTOMVERSION1"]

                for col_i in range(1,6):
                    col = "SYMPTOM" + str(col_i)
                    symptom = row[col].strip()
                    if len(symptom) > 0:
                        report["symptoms"].append(symptom)

        with vaers_zip.open(vax_filename) as vax_file:
            reader = DictReader(TextIOWrapper(vax_file, encoding="latin-1"))
            for row in reader:
                report = reports_by_id[row["VAERS_ID"]]
                report["vax"].append(row["VAX_TYPE"])

    return list(reports_by_id.values())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Translate VAERS Zip File into a JSON file.')
    parser.add_argument('zipfile', help='The VAERS Zip File to be transformed')
    parser.add_argument('output', help='The location of the output', nargs="?")
    args = parser.parse_args()

    source_path = Path(args.zipfile)
    json_data = transform_zip_file(source_path)

    output_path = args.output
    if output_path is None:
        print(json.dumps(json_data))
    else:
        with open(output_path, "wb") as output_file:
            json.dump(json_data, output_file)