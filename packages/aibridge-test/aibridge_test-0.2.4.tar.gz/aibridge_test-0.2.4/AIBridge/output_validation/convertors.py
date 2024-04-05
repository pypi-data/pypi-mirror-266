import json
import csv
import xmltodict
import io
import re


class IntoJson:
    @classmethod
    def csv_to_json(self, csv_data):
        csv_data = csv_data.replace("\n", "")
        csv_list = csv_data.split(",")
        json_dict = {"data": []}
        new_dict = {}
        for key in csv_list:
            new_dict[key] = ""
        json_dict["data"].append(new_dict)
        return json_dict

    @classmethod
    def xml_to_json(self, xml_data):
        if """<?xml version="1.0" encoding="UTF-8"?>""" in xml_data:
            xml_data = xml_data.replace(
                """<?xml version="1.0" encoding="UTF-8"?>""", ""
            )

        cleaned_xml_data = re.sub(r"^.*?(<[^>]*>)", r"\1", xml_data, flags=re.DOTALL)
        json_data = xmltodict.parse(cleaned_xml_data)
        new_json = {}
        for key, value in json_data.items():
            new_json[key] = [value]
            break
        return new_json


class FromJson:
    @classmethod
    def json_to_csv(self, json_dict):
        # Convert JSON to CSV
        json_data = json_dict["data"]
        csv_output = io.StringIO()
        csv_writer = csv.DictWriter(csv_output, fieldnames=json_data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(json_data)
        # Get the CSV data as a string
        csv_data = csv_output.getvalue()
        return csv_data

    @classmethod
    def json_to_xml(self, json_data):
        root_element_name = "root"
        xml_data = xmltodict.unparse({root_element_name: json_data}, pretty=True)
        return xml_data
