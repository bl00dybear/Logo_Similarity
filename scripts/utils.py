import csv
import json


def write_dict_in_csv_file(logo_dict,dict_path="../datasets/logo_dict.csv"):
    with open(dict_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["domain", "path", "distribution"])
        for domain, values in logo_dict.items():
            temp = [domain]
            for value in values:
                temp.append(value)
            writer.writerow(temp)

def read_dict_from_csv(dict_path="../datasets/logo_dict.csv"):
    with open(dict_path, mode="r", newline="", encoding="utf-8") as file:
        rows = csv.reader(file)
        next(rows)
        logo_dict = {row[0]:[row[1],row[2]] for row in rows}
        # print(logo_dict)

    return logo_dict


def construct_label_domain_dict(labels, logo_dict, valid_domains):
    label_domain_dict = {}
    index = 0

    for domain in valid_domains:
        if logo_dict[domain][0] is not None:
            if labels[index] not in label_domain_dict:
                label_domain_dict[labels[index]] = [domain]
            else:
                label_domain_dict[labels[index]].append(domain)
            index += int(logo_dict[domain][1])

    return label_domain_dict

def save_label_domain_dict(label_domain_dict, filename="../datasets/label_domain_dict.json"):
    label_domain_dict_converted={int(k):v for k,v in label_domain_dict.items()}

    label_domain_dict_converted = {k: label_domain_dict_converted[k] for k in sorted(label_domain_dict_converted)}

    with open(filename, "w") as file:
        json.dump(label_domain_dict_converted, file, indent=4)


def save_strings_to_csv(string_list, filename="strings.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(string_list)


def load_strings_from_csv(filename="strings.csv"):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        string_list = next(reader)
    return string_list