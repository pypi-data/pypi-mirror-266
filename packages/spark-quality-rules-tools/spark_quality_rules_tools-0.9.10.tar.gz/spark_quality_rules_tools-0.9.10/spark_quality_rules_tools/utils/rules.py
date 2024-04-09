def get_validate_rules(hocons_dir=None):
    import os
    import sys
    import json
    from spark_quality_rules_tools.utils import BASE_DIR
    from spark_quality_rules_tools.utils.color import get_color, get_color_b, get_color_r, get_color_g
    from pyhocon.converter import HOCONConverter
    from pyhocon import ConfigFactory
    from prettytable import PrettyTable

    is_windows = sys.platform.startswith('win')
    dir_default_rules = os.path.join(BASE_DIR, "utils", "resource", "rules.json")
    file_conf = hocons_dir

    if hocons_dir in ("", None):
        raise Exception(f'required variable hocons_dir')

    if is_windows:
        dir_default_rules = dir_default_rules.replace("\\", "/")
        file_conf = file_conf.replace("\\", "/")

    with open(dir_default_rules) as f:
        default_rules = json.load(f)

    file_conf = ConfigFactory.parse_file(file_conf)
    file_conf = HOCONConverter.to_json(file_conf)
    file_conf = json.loads(file_conf)
    haas_rules = file_conf["hammurabi"]["rules"]

    rules_default_properties = default_rules["rules_common_properties"][0]

    key_id_list = list()
    for haas_rule in haas_rules:
        haas_class = str(haas_rule["class"])
        haas_columns = haas_rule["config"]
        haas_rules_type = str(haas_class).split(".")[4]
        haas_rules_class = str(haas_class).split(".")[5]

        rules_version = default_rules["rules_config"][haas_rules_type][haas_rules_class][0]["rules_version"]
        rules_columns = default_rules["rules_config"][haas_rules_type][haas_rules_class][0]["rules_columns"][0]
        rules_columns_all = {**rules_columns, **rules_default_properties}
        rules_columns_required = [key for key, val in rules_columns_all.items() if val[1] == "true"]

        t = PrettyTable()
        print(f"type   => {get_color_g(haas_rules_type)}")
        print(f"class  => {get_color_g(haas_rules_class)}")
        print(f"version=> {get_color_g(rules_version)}")
        if "id" in haas_columns.keys():
            print(f"id=> {get_color_g(haas_columns.get('id'))}")
            key_id_list.append(haas_columns.get('id'))
        else:
            print(f"id=> {get_color_g('No existe parametro ID')}")

        t.field_names = [f"Variable", "Value", "Dtype Actual", "Dtype Esperado", "Es Obligatorio"]
        for col in rules_columns_required:
            if "id" in haas_columns.keys():
                print(f"id=> {get_color_g(rules_columns_all[col])}")
            else:
                print(f"id=> {get_color_g('No existe parametro ID')}")

            if str(col) not in haas_columns.keys():
                t.add_row([get_color_r(col),
                           get_color_r("variable requerida"),
                           get_color_r("variable requerida"),
                           get_color_r(rules_columns_all[col][0]),
                           get_color_r(rules_columns_all[col][1])
                           ])

        for col, value in haas_columns.items():
            if not str(col) in rules_columns_all.keys():
                t.add_row([get_color_b(col),
                           get_color_b(value),
                           get_color_b("Deprecado"),
                           get_color_b("Deprecado"),
                           get_color_b("Deprecado")
                           ])

        for col, value in haas_columns.items():
            if str(col) in rules_columns_all.keys():
                t.add_row([get_color(col),
                           get_color(value),
                           get_color(str(type(value))),
                           get_color(rules_columns_all[col][0]),
                           get_color(rules_columns_all[col][1])
                           ])
        print(t)

    print(f"Total ID: {len(key_id_list)}")
    print(f"Unique ID: {len(set(key_id_list))}")
