import csv


def write_dict_in_csv_file(logo_dict,dict_path="../logo_dict.csv"):
    with open(dict_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["domain", "path"])
        for domain, path in logo_dict.items():
            writer.writerow([domain, path])

def read_dict_from_csv(dict_path="../logo_dict.csv"):
    with open(dict_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        logo_dict = {rows[0]:rows[1] for rows in reader}

    return logo_dict