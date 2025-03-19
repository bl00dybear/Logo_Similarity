import csv


def write_dict_in_csv_file(logo_dict,dict_path="../logo_dict.csv"):
    with open(dict_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["domain", "path", "distribution"])
        for domain, values in logo_dict.items():
            temp = [domain]
            for value in values:
                temp.append(value)
            writer.writerow(temp)

def read_dict_from_csv(dict_path="../logo_dict.csv"):
    with open(dict_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        logo_dict = {rows[0]:rows[1] for rows in reader}

    return logo_dict