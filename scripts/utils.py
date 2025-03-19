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
        rows = csv.reader(file)
        next(rows)
        logo_dict = {row[0]:[row[1],row[2]] for row in rows}
        # print(logo_dict)

    return logo_dict