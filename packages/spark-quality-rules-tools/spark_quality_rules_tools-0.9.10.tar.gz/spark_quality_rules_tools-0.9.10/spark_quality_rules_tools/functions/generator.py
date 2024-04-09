# def dq_searching_rules(category_rule=None, table_name=None, rule_id=None, static_id=None, sequence="001"):
#     from spark_quality_rules_tools.utils import BASE_DIR
#     import os
#     import json
#     import ast
#     import sys
#
#     is_windows = sys.platform.startswith('win')
#     json_resource_rules = os.path.join(BASE_DIR, "utils", "resource", "rules.json")
#
#     if is_windows:
#         json_resource_rules = json_resource_rules.replace("\\", "/")
#
#     with open(json_resource_rules) as f:
#         default_rules = json.load(f)
#     rules_config = default_rules.get("rules_config", None)
#     hamu_dict = dict()
#     id_key_dict = dict()
#     rs_dict = dict()
#     for k, v in rules_config.items():
#         for key_name, value_name in v.items():
#             rules_version = value_name[0].get("rules_version")
#             rules_class = str(value_name[0].get("rules_class"))
#             rules_columns = value_name[0].get("rules_columns")
#             if rules_version == rule_id:
#                 for rule_name, rule_dtype in rules_columns[0].items():
#                     if rule_dtype[1] == "True":
#                         id_key_dict[rule_name] = "Mandatory"
#                     if rule_dtype[0] == "Boolean" and rule_dtype[2] == "True":
#                         rules_value = True
#                     elif rule_dtype[0] == "Boolean" and rule_dtype[2] == "False":
#                         rules_value = False
#                     elif rule_dtype[0] == "Double" and rule_dtype[2] == "100":
#                         rules_value = ast.literal_eval(rule_dtype[2])
#                     elif rule_dtype[0] == "String" and rule_dtype[2] in ("None", ""):
#                         rules_value = ""
#                     elif rule_dtype[0] == "Array[String]" and rule_dtype[2] in ("None", ""):
#                         rules_value = ["default"]
#                     elif rule_dtype[0] == "Dict" and rule_dtype[2] in ("None", ""):
#                         rules_value = dict()
#                     else:
#                         rules_value = rule_dtype[2]
#                     rs_dict[rule_name] = rules_value
#                 if static_id:
#                     rs_dict["id"] = static_id
#                 else:
#                     rule_id = str(rule_id).replace("-1", "").replace("-2", "").strip()
#                     rs_dict["id"] = f"PE_{category_rule}_{table_name}_{rule_id}_{sequence}"
#                 hamu_dict["class"] = rules_class
#                 hamu_dict["config"] = rs_dict
#     return hamu_dict, id_key_dict
#
#
# def dq_creating_directory_hdfs(spark=None, path=None):
#     from spark_quality_rules_tools import get_color, get_color_b
#
#     sc = spark.sparkContext
#     fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
#     if path in ("", None):
#         raise Exception(f'required variable path')
#     if not fs.exists(sc._jvm.org.apache.hadoop.fs.Path(f'{path}')):
#         fs.mkdirs(sc._jvm.org.apache.hadoop.fs.Path(f'{path}'))
#         print(f"{get_color('Directory Created:')} {get_color_b(path)}")
#     else:
#         print(f"{get_color('Directory Exists:')} {get_color_b(path)}")
#
#
# def dq_creating_directory_sandbox(path=None):
#     from spark_quality_rules_tools import get_color, get_color_b
#     import os
#
#     if path in ("", None):
#         raise Exception(f'required variable path')
#     if not os.path.exists(f'{path}'):
#         os.makedirs(f'{path}')
#         print(f"{get_color('Directory Created:')} {get_color_b(path)}")
#     else:
#         print(f"{get_color('Directory Exists:')} {get_color_b(path)}")
#
#
# def dq_spark_session(user_sandbox=None):
#     import os
#     from pyspark.sql import SparkSession
#     from spark_quality_rules_tools import get_color, get_color_b
#
#     dir_uuaa_code = os.getenv("pj_dq_dir_uuaa_code")
#     dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
#     dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")
#     dir_sandbox_dq_temporaries = os.getenv("pj_dq_dir_sandbox_dq_temporaries")
#     if user_sandbox is None:
#         user_sandbox = os.getenv('JPY_USER')
#         if user_sandbox in ("", None):
#             raise Exception(f'required variable user_sandbox')
#     if dir_uuaa_code in ("", None):
#         raise Exception(f'required environment: pj_dq_dir_uuaa_code')
#     if dir_sandbox_dq_metrics in ("", None):
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')
#     if dir_sandbox_dq_refusals in ("", None):
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_refusals')
#     if dir_sandbox_dq_temporaries in ("", None):
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_temporaries')
#
#     os.environ['UUAA_CODE'] = dir_uuaa_code
#     os.environ['JPY_USER'] = user_sandbox
#     os.environ['SANDBOX_DQ_METRICS'] = dir_sandbox_dq_metrics
#     os.environ['SANDBOX_DQ_REFUSALS'] = dir_sandbox_dq_refusals
#     os.environ['SANDBOX_DQ_TEMPORARIES'] = dir_sandbox_dq_temporaries
#
#     spark = SparkSession.builder \
#         .master("local[*]") \
#         .appName("JONAP") \
#         .getOrCreate()
#     spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
#     sc = spark.sparkContext
#     sc._conf.setExecutorEnv("UUAA_CODE", os.getenv("UUAA_CODE"))
#     sc._conf.setExecutorEnv("JPY_USER", os.getenv("JPY_USER"))
#     sc._conf.setExecutorEnv("SANDBOX_DQ_METRICS", os.getenv("SANDBOX_DQ_METRICS"))
#     sc._conf.setExecutorEnv("SANDBOX_DQ_REFUSALS", os.getenv("SANDBOX_DQ_REFUSALS"))
#     sc._conf.setExecutorEnv("SANDBOX_DQ_TEMPORARIES", os.getenv("SANDBOX_DQ_TEMPORARIES"))
#
#     print(f"{get_color('Created Session Spark for user:')} {get_color_b(user_sandbox)}")
#     return spark, sc
#
#
# def dq_path_workspace(spark=None,
#                       user_sandbox=None,
#                       uuaa_code='fina',
#                       project_sda='CDD'):
#     import os
#     import sys
#
#     if user_sandbox is None:
#         user_sandbox = os.getenv('JPY_USER')
#         print(f"user_sandbox = {user_sandbox}")
#         if user_sandbox in ("", None):
#             raise Exception(f'required variable user_sandbox')
#     is_windows = sys.platform.startswith('win')
#     pj_dir_workspace = ""
#     pj_dq_dir_uuaa_code = os.path.join(uuaa_code, "data", "projects", project_sda, "data_quality_rules")
#     pj_dq_dir_sandbox_dq_metrics = f"/data/sandboxes/{pj_dq_dir_uuaa_code}/data/users/{user_sandbox}/dq/metrics"
#     pj_dq_dir_sandbox_dq_refusals = f"/data/sandboxes/{pj_dq_dir_uuaa_code}/data/users/{user_sandbox}/dq/refusals"
#     pj_dq_dir_sandbox_dq_temporaries = f"/data/sandboxes/{pj_dq_dir_uuaa_code}/data/users/{user_sandbox}/dq/temporaries"
#
#     pj_dq_dir_name = "data_quality_rules"
#     pj_dq_dir_artifacts_python = os.path.join(pj_dir_workspace, "artifacts", "python")
#     pj_dq_dir_artifacts_scala = os.path.join(pj_dir_workspace, "artifacts", "scala")
#     pj_dq_dir_name = os.path.join(pj_dir_workspace, pj_dq_dir_name)
#     pj_dq_dir_confs_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_confs")
#     pj_dq_dir_hocons_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_hocons")
#     pj_dq_dir_reports_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_reports")
#     pj_dq_dir_resolve_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_resolve")
#
#     if is_windows:
#         pj_dq_dir_uuaa_code = pj_dq_dir_uuaa_code.replace("\\", "/")
#         pj_dq_dir_sandbox_dq_metrics = pj_dq_dir_sandbox_dq_metrics.replace("\\", "/")
#         pj_dq_dir_sandbox_dq_refusals = pj_dq_dir_sandbox_dq_refusals.replace("\\", "/")
#         pj_dq_dir_sandbox_dq_temporaries = pj_dq_dir_sandbox_dq_temporaries.replace("\\", "/")
#         pj_dq_dir_artifacts_python = pj_dq_dir_artifacts_python.replace("\\", "/")
#         pj_dq_dir_artifacts_scala = pj_dq_dir_artifacts_scala.replace("\\", "/")
#         pj_dq_dir_name = pj_dq_dir_name.replace("\\", "/")
#         pj_dq_dir_confs_name = pj_dq_dir_confs_name.replace("\\", "/")
#         pj_dq_dir_hocons_name = pj_dq_dir_hocons_name.replace("\\", "/")
#         pj_dq_dir_reports_name = pj_dq_dir_reports_name.replace("\\", "/")
#         pj_dq_dir_resolve_name = pj_dq_dir_resolve_name.replace("\\", "/")
#
#     dq_creating_directory_sandbox(path=pj_dq_dir_name)
#     dq_creating_directory_sandbox(path=pj_dq_dir_artifacts_python)
#     dq_creating_directory_sandbox(path=pj_dq_dir_artifacts_scala)
#     dq_creating_directory_sandbox(path=pj_dq_dir_confs_name)
#     dq_creating_directory_sandbox(path=pj_dq_dir_hocons_name)
#     dq_creating_directory_sandbox(path=pj_dq_dir_reports_name)
#     dq_creating_directory_sandbox(path=pj_dq_dir_resolve_name)
#     dq_creating_directory_hdfs(spark=spark, path=pj_dq_dir_sandbox_dq_metrics)
#     dq_creating_directory_hdfs(spark=spark, path=pj_dq_dir_sandbox_dq_refusals)
#     dq_creating_directory_hdfs(spark=spark, path=pj_dq_dir_sandbox_dq_temporaries)
#     os.environ['pj_dq_dir_name'] = pj_dq_dir_name
#     os.environ['pj_dq_dir_artifacts_python'] = pj_dq_dir_artifacts_python
#     os.environ['pj_dq_dir_artifacts_scala'] = pj_dq_dir_artifacts_scala
#     os.environ['pj_dq_dir_confs_name'] = pj_dq_dir_confs_name
#     os.environ['pj_dq_dir_hocons_name'] = pj_dq_dir_hocons_name
#     os.environ['pj_dq_dir_reports_name'] = pj_dq_dir_reports_name
#     os.environ['pj_dir_workspace'] = pj_dir_workspace
#     os.environ['pj_dq_dir_uuaa_code'] = pj_dq_dir_uuaa_code
#     os.environ['pj_dq_dir_sandbox_dq_metrics'] = pj_dq_dir_sandbox_dq_metrics
#     os.environ['pj_dq_dir_sandbox_dq_refusals'] = pj_dq_dir_sandbox_dq_refusals
#     os.environ['pj_dq_dir_sandbox_dq_temporaries'] = pj_dq_dir_sandbox_dq_temporaries
#     os.environ['pj_dq_dir_resolve_name'] = pj_dq_dir_resolve_name
#
#
# def dq_download_jar(haas_jar_url=None,
#                     haas_version="4.8.0",
#                     force=False):
#     import requests
#     import sys
#     import os
#     from spark_quality_rules_tools import get_color, get_color_b
#     is_windows = sys.platform.startswith('win')
#     dir_artifacts_python = os.getenv('pj_dq_dir_artifacts_python')
#     dir_artifacts_scala = os.getenv('pj_dq_dir_artifacts_scala')
#     jar_name = "hammurabi-sandbox-spark3.jar"
#     if dir_artifacts_python is None:
#         raise Exception(f'required environment: pj_dq_dir_artifacts_python')
#     if dir_artifacts_scala is None:
#         raise Exception(f'required environment: pj_dq_dir_artifacts_scala')
#     if haas_jar_url is None:
#         haas_jar_url = f"http://artifactory-gdt.central-02.nextgen.igrupobbva/artifactory/" \
#                        f"gl-datio-spark-libs-maven-local/com/datio/hammurabi-sandbox/{haas_version}/" \
#                        f"hammurabi-sandbox-{haas_version}-jar-with-dependencies.jar"
#     dir_artifacts_python_jar_file = os.path.join(dir_artifacts_python, jar_name)
#     dir_artifacts_scala_jar_file = os.path.join(dir_artifacts_scala, jar_name)
#     if is_windows:
#         dir_artifacts_python_jar_file = dir_artifacts_python_jar_file.replace("\\", "/")
#         dir_artifacts_scala_jar_file = dir_artifacts_scala_jar_file.replace("\\", "/")
#
#     os.makedirs(os.path.dirname(dir_artifacts_python_jar_file), exist_ok=True)
#     os.makedirs(os.path.dirname(dir_artifacts_scala_jar_file), exist_ok=True)
#
#     if force:
#         if os.path.isfile(dir_artifacts_python_jar_file):
#             os.remove(dir_artifacts_python_jar_file)
#         if os.path.isfile(dir_artifacts_scala_jar_file):
#             os.remove(dir_artifacts_scala_jar_file)
#         with requests.get(haas_jar_url, stream=True, verify=True) as r:
#             r.raise_for_status()
#             with open(dir_artifacts_python_jar_file, 'wb+') as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     f.write(chunk)
#         with requests.get(haas_jar_url, stream=True, verify=True) as r:
#             with open(dir_artifacts_scala_jar_file, 'wb+') as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     f.write(chunk)
#         print(f"{get_color('Download Python finished on:')} {get_color_b(dir_artifacts_python_jar_file)}")
#         print(f"{get_color('Download Scala finished on:')} {get_color_b(dir_artifacts_scala_jar_file)}")
#     else:
#         print(f"{get_color('Exist Jar haas Path:')} {get_color_b(dir_artifacts_python_jar_file)}")
#
#
# def dq_validate_conf_artifactory(url_conf=None):
#     import requests
#     from spark_quality_rules_tools import get_color_b
#
#     if url_conf in ("", None):
#         raise Exception(f'required variable url_conf')
#     res = requests.get(url_conf)
#     print(f"{get_color_b(f'{res.text}')}")
#
#
# def dq_validate_conf_file(file_conf=None):
#     from spark_quality_rules_tools import get_color_b
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#
#     with open(file_conf) as f:
#         res = f.read()
#     print(f"{get_color_b(f'{res}')}")
#
#
# def dq_extract_parameters_artifactory(url_conf=None):
#     import os
#     import sys
#     import re
#     import json
#     import requests
#     from spark_quality_rules_tools import get_color, get_color_b
#     is_windows = sys.platform.startswith('win')
#     dir_confs_name = os.getenv('pj_dq_dir_confs_name')
#
#     if url_conf in ("", None):
#         raise Exception(f'required variable url_conf')
#     if dir_confs_name is None:
#         raise Exception(f'required environment: pj_dq_dir_confs_name')
#
#     url = url_conf
#     url_conf_extension = str(str(url).split("/")[-1]).replace("-", "_").upper().strip()
#     url_conf_name = str(str(url_conf_extension).split(".")[0])
#     uuaa_name = str(str(url).split("/")[-2]).upper()
#     if not len(uuaa_name) == 4:
#         uuaa_name = str(str(url).split("/")[-5]).upper()
#
#     dir_confs_filename = os.path.join(dir_confs_name, uuaa_name, f"{url_conf_name}.txt")
#     dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, f"PARAMS-{url_conf_name}.json")
#
#     if is_windows:
#         dir_confs_filename = dir_confs_filename.replace("\\", "/")
#         dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")
#
#     os.makedirs(os.path.dirname(dir_confs_filename), exist_ok=True)
#
#     with requests.get(url, stream=True, verify=True) as r:
#         r.raise_for_status()
#         with open(dir_confs_filename, 'wb+') as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)
#
#     with open(dir_confs_filename) as f:
#         hammurabi_conf = f.read()
#
#     variables_1 = sorted(list(set(re.findall(r'{([a-zA-Z_.-]+)}', hammurabi_conf))))
#     variables_2 = sorted(list(set(re.findall(r'{?([a-zA-Z_.-]+)}', hammurabi_conf))))
#     variables_list = list(set(variables_1 + variables_2))
#
#     variables_dict = {variables: "" for variables in variables_list if
#                       variables not in ("ARTIFACTORY_UNIQUE_CACHE", "SCHEMAS_REPOSITORY", "TEST_PATH")}
#
#     parameter_dict = dict()
#     parameter_dict[uuaa_name] = list()
#     parameter_dict[uuaa_name].append({"table": url_conf_name,
#                                       "conf_name": url_conf_extension,
#                                       "parameters": variables_dict})
#
#     with open(f"{dir_confs_filename_parameters}", "w") as f:
#         json.dump(parameter_dict, f, indent=4)
#
#     with open(f"{dir_confs_filename_parameters}") as f:
#         parameter_conf = f.read()
#         parameter_conf = json.loads(parameter_conf)
#
#     params = parameter_conf[uuaa_name][0]["parameters"]
#     params = json.dumps(params, indent=4)
#     print(f"{get_color(f'================================')} ")
#     print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
#     print(f"{get_color('table name:')} {get_color_b(url_conf_name)}")
#     print(f"{get_color('conf name :')} {get_color_b(url_conf_extension)}")
#     print(f"{get_color('parameters:')} {get_color_b(params)}")
#     print(f"{get_color('=================================')} ")
#
#
# def dq_extract_parameters_file(file_conf=None, uuaa=None, table_name=None):
#     import os
#     import sys
#     import re
#     import json
#     from spark_quality_rules_tools import get_color, get_color_b
#     is_windows = sys.platform.startswith('win')
#     dir_confs_name = os.getenv('pj_dq_dir_confs_name')
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#     if dir_confs_name is None:
#         raise Exception(f'required environment: pj_dq_dir_confs_name')
#
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#     dir_confs_filename = os.path.join(dir_confs_name, uuaa_name, f"{url_conf_name}.txt")
#     dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, f"PARAMS-{url_conf_name}.json")
#
#     if is_windows:
#         dir_confs_filename = dir_confs_filename.replace("\\", "/")
#         dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_confs_filename), exist_ok=True)
#
#     with open(file_conf) as file:
#         hammurabi_conf = file.read()
#
#     with open(dir_confs_filename, 'w') as file:
#         file.write(hammurabi_conf)
#
#     with open(dir_confs_filename) as f:
#         hammurabi_conf = f.read()
#
#     variables_1 = sorted(list(set(re.findall(r'{([a-zA-Z_.-]+)}', hammurabi_conf))))
#     variables_2 = sorted(list(set(re.findall(r'{?([a-zA-Z_.-]+)}', hammurabi_conf))))
#     variables_list = list(set(variables_1 + variables_2))
#
#     variables_dict = {variables: "" for variables in variables_list if
#                       variables not in ("ARTIFACTORY_UNIQUE_CACHE", "SCHEMAS_REPOSITORY", "TEST_PATH")}
#
#     parameter_dict = dict()
#     parameter_dict[uuaa_name] = list()
#     parameter_dict[uuaa_name].append({"table": table_name,
#                                       "conf_name": url_conf_name,
#                                       "parameters": variables_dict})
#
#     with open(f"{dir_confs_filename_parameters}", "w") as f:
#         json.dump(parameter_dict, f, indent=4)
#
#     with open(f"{dir_confs_filename_parameters}") as f:
#         parameter_conf = f.read()
#         parameter_conf = json.loads(parameter_conf)
#
#     params = parameter_conf[uuaa_name][0]["parameters"]
#     params = json.dumps(params, indent=4)
#     print(f"{get_color(f'================================')} ")
#     print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
#     print(f"{get_color('table name:')} {get_color_b(table_name)}")
#     print(f"{get_color('conf name :')} {get_color_b(url_conf_name)}")
#     print(f"{get_color('parameters:')} {get_color_b(params)}")
#     print(f"{get_color('=================================')} ")
#
#
# def dq_run_sandbox_artifactory(spark=None,
#                                sc=None,
#                                parameter_conf_list=None,
#                                url_conf=None,
#                                is_prod=True,
#                                resolve_name="resolve_sandbox.conf"):
#     import json
#     import sys
#     import os
#     from datetime import datetime
#     from tqdm import tqdm
#     from pyhocon import ConfigFactory
#     from pyhocon.converter import HOCONConverter
#     from pyspark.sql import functions as func
#     from spark_quality_rules_tools import get_color, get_color_b
#     from spark_quality_rules_tools import get_replace_resolve_parameter
#
#     is_windows = sys.platform.startswith('win')
#     dir_confs_name = os.getenv('pj_dq_dir_confs_name')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#     dir_reports_name = os.getenv('pj_dq_dir_reports_name')
#     uuaa_code = os.getenv("UUAA_CODE")
#     user_sandbox = os.getenv("JPY_USER")
#     dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
#     dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")
#
#     if url_conf in ("", None):
#         raise Exception(f'required variable url_conf')
#     if parameter_conf_list in ("", None):
#         raise Exception(f'required variable parameter_conf_list')
#     if dir_confs_name is None:
#         raise Exception(f'required environment: pj_dq_dir_confs_name')
#     if dir_hocons_name is None:
#         raise Exception(f'required environment: pj_dq_dir_hocons_name')
#     if dir_reports_name is None:
#         raise Exception(f'required environment: pj_dq_dir_reports_name')
#     if uuaa_code is None:
#         raise Exception(f'required environment: UUAA_CODE')
#     if user_sandbox is None:
#         raise Exception(f'required environment: JPY_USER')
#     if dir_sandbox_dq_metrics is None:
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')
#     if resolve_name is None:
#         raise Exception(f'required environment: resolve_name')
#
#     url = url_conf
#     url_conf_extension = str(str(url).split("/")[-1]).replace("-", "_").upper().strip()
#     url_conf_name = str(str(url_conf_extension).split(".")[0])
#     uuaa_name = str(str(url).split("/")[-2]).upper()
#     if not len(uuaa_name) == 4:
#         uuaa_name = str(str(url).split("/")[-5]).upper()
#
#     now = datetime.now()
#     current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
#     current_datetime_str = now.strftime("%Y%m%d%H%M")
#
#     dir_confs_filename = os.path.join(dir_confs_name, uuaa_name, f"{url_conf_name}.txt")
#     dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, f"PARAMS-{url_conf_name}.json")
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}.conf")
#
#     if is_windows:
#         dir_confs_filename = dir_confs_filename.replace("\\", "/")
#         dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_hocons_filename), exist_ok=True)
#
#     with open(dir_confs_filename_parameters) as f:
#         parameter_conf = f.read()
#         parameter_conf = json.loads(parameter_conf)
#
#     params_parameter = parameter_conf[uuaa_name][0]["parameters"]
#     validate_parameter_keys = list(set(params_parameter.keys()))
#     validate_parameter_conf_keys = list(set([b for a in parameter_conf_list for b in a.keys()]))
#     validate_compare_parameters = (sorted(validate_parameter_keys) == sorted(validate_parameter_conf_keys))
#     if not validate_compare_parameters:
#         raise Exception(f'Need more variables the parameters: parameter_conf_list')
#
#     cutoff_date = ""
#     with open(dir_confs_filename) as f:
#         txt_conf = f.read()
#
#     txt_conf = txt_conf.replace(f'${{TEST_PATH}}', "")
#     txt_conf = txt_conf.replace(f'${{COUNTRY}}', "pe")
#     txt_conf = txt_conf.replace(f'"/artifactory/"', "/artifactory/")
#     txt_conf = txt_conf.replace(f'${{ARTIFACTORY_UNIQUE_CACHE}}', "http://artifactory-gdt.central-02.nextgen.igrupobbva")
#     if is_prod:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-local")
#     else:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-dev-local")
#
#     for params_parameter_conf in tqdm(parameter_conf_list):
#         for k, v in params_parameter_conf.items():
#             if str(k).upper() in ("ODATE", "ODATE_DATE", "CUTOFF_DATE"):
#                 cutoff_date = str(v).replace("-", "").strip()
#             txt_conf = txt_conf.replace(f'${{{k}}}', v)
#             txt_conf = txt_conf.replace(f'${{?{k}}}', v)
#     dir_reports_name_filename = os.path.join(dir_reports_name, uuaa_name,
#                                              f"{url_conf_name}_{current_datetime_str}_{cutoff_date}.csv")
#     if is_windows:
#         dir_reports_name_filename = dir_reports_name_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_reports_name_filename), exist_ok=True)
#
#     conf_file = ConfigFactory.parse_string(txt_conf)
#     hocons_file = HOCONConverter.to_hocon(conf_file)
#     with open(dir_hocons_filename, "w") as f:
#         f.write(hocons_file)
#
#     spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
#     conf = sc._jvm.java.io.File(dir_hocons_filename)
#     ConfigFactory2 = sc._jvm.com.typesafe.config.ConfigFactory
#     parsed_conf = ConfigFactory2.parseFile(conf)
#     resolve_path = get_replace_resolve_parameter(sc=sc, resolve_name=resolve_name)
#     resolvedConfig = parsed_conf.withFallback(resolve_path).resolve()
#     Standalone = sc._jvm.com.datio.hammurabi.sandbox
#     result = Standalone.Hammurabi.run(spark._jsparkSession, resolvedConfig)
#
#     if result == 2:
#         print(f"{get_color('Problema para construir la ejecución, posible configuración o regla mal definida')} ")
#     else:
#         if result == 1:
#             print(f"{get_color('La validación de calidad falló, la regla crítica falló')} ")
#         elif result == 0:
#             print(
#                 f"{get_color('Ha pasado la validación de calidad. Esto significa que no hay ninguna regla crítica que haya fallado.')} ")
#
#     metrics_df = spark.read.parquet(dir_sandbox_dq_metrics)
#     metrics_filter = metrics_df.filter(
#         func.col("gf_quality_rule_execution_date") >= func.unix_timestamp(func.lit(current_datetime)).cast('timestamp'))
#     df2 = metrics_filter.select(
#         func.col("gf_qr_functional_definition_id"),
#         func.concat(func.col("g_quality_rule_principle_type"),
#                     func.lit("."),
#                     func.col("g_quality_rule_type")).alias("Rule"),
#         func.regexp_replace(func.col("gf_quality_rule_metadata_map.ruleName"),
#                             "com.datio.hammurabi.rules.", ""
#                             ).alias("Rule Name"),
#         func.col("gf_qr_tg_object_physical_name"),
#         func.col("gf_cutoff_date"),
#         func.col("gf_field_physical_name").alias("Field"),
#         func.col("gf_qr_aux_attribute_desc").alias("Format"),
#         func.col("g_qr_critical_type").alias("Is Critical"),
#         func.col("gf_qr_min_acceptance_per").alias("% Acceptation"),
#         func.col("g_quality_rule_status_type").alias("Status"),
#         func.col("gf_quality_rule_compliance_per").alias("Por"))
#     df3 = df2.distinct().sort("gf_qr_functional_definition_id")
#     df3 = df3.select(*[func.col(col).cast("string") for col in df3.columns])
#     df3.show(500, False, True)
#
#     metrics_filter_pandas = df3.toPandas()
#     metrics_filter_pandas.to_csv(dir_reports_name_filename, index=False)
#
#     print(f"{get_color(f'================================')} ")
#     print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
#     print(f"{get_color('table name:')} {get_color_b(url_conf_name)}")
#     print(f"{get_color('conf name :')} {get_color_b(url_conf_extension)}")
#     print(f"{get_color('cutoff date:')} {get_color_b(cutoff_date)}")
#     print(f"{get_color('Generating a file csv:')} {get_color_b(dir_reports_name_filename)}")
#     print(f"{get_color('=================================')} ")
#
#
# def dq_run_sandbox_file(spark=None,
#                         sc=None,
#                         uuaa=None,
#                         table_name=None,
#                         parameter_conf_list=None,
#                         file_conf=None,
#                         is_prod=True,
#                         resolve_name="resolve_sandbox.conf"):
#     import json
#     import sys
#     import os
#     from datetime import datetime
#     from tqdm import tqdm
#     from pyhocon import ConfigFactory
#     from pyhocon.converter import HOCONConverter
#     from pyspark.sql import functions as func
#     from spark_quality_rules_tools import get_color, get_color_b
#     from spark_quality_rules_tools import get_replace_resolve_parameter
#
#     is_windows = sys.platform.startswith('win')
#     dir_confs_name = os.getenv('pj_dq_dir_confs_name')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#     dir_reports_name = os.getenv('pj_dq_dir_reports_name')
#     uuaa_code = os.getenv("UUAA_CODE")
#     user_sandbox = os.getenv("JPY_USER")
#     dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
#     dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#     if parameter_conf_list in ("", None):
#         raise Exception(f'required variable parameter_conf_list')
#     if dir_confs_name is None:
#         raise Exception(f'required environment: pj_dq_dir_confs_name')
#     if dir_hocons_name is None:
#         raise Exception(f'required environment: pj_dq_dir_hocons_name')
#     if dir_reports_name is None:
#         raise Exception(f'required environment: pj_dq_dir_reports_name')
#     if uuaa_code is None:
#         raise Exception(f'required environment: UUAA_CODE')
#     if user_sandbox is None:
#         raise Exception(f'required environment: JPY_USER')
#     if dir_sandbox_dq_metrics is None:
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')
#     if resolve_name is None:
#         raise Exception(f'required environment: resolve_name')
#
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#
#     now = datetime.now()
#     current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
#     current_datetime_str = now.strftime("%Y%m%d%H%M")
#
#     dir_confs_filename = os.path.join(dir_confs_name, uuaa_name, f"{url_conf_name}.txt")
#     dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, f"PARAMS-{url_conf_name}.json")
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}.conf")
#
#     if is_windows:
#         dir_confs_filename = dir_confs_filename.replace("\\", "/")
#         dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_hocons_filename), exist_ok=True)
#
#     with open(dir_confs_filename_parameters) as f:
#         parameter_conf = f.read()
#         parameter_conf = json.loads(parameter_conf)
#
#     params_parameter = parameter_conf[uuaa_name][0]["parameters"]
#     validate_parameter_keys = list(set(params_parameter.keys()))
#     validate_parameter_conf_keys = list(set([b for a in parameter_conf_list for b in a.keys()]))
#     validate_compare_parameters = (sorted(validate_parameter_keys) == sorted(validate_parameter_conf_keys))
#     if not validate_compare_parameters:
#         raise Exception(f'Need more variables the parameters: parameter_conf_list')
#
#     cutoff_date = ""
#     with open(dir_confs_filename) as f:
#         txt_conf = f.read()
#
#     txt_conf = txt_conf.replace(f'${{TEST_PATH}}', "")
#     txt_conf = txt_conf.replace(f'${{COUNTRY}}', "pe")
#     txt_conf = txt_conf.replace(f'"/artifactory/"', "/artifactory/")
#     txt_conf = txt_conf.replace(f'${{ARTIFACTORY_UNIQUE_CACHE}}', "http://artifactory-gdt.central-02.nextgen.igrupobbva")
#     if is_prod:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-local")
#     else:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-dev-local")
#
#     for params_parameter_conf in tqdm(parameter_conf_list):
#         for k, v in params_parameter_conf.items():
#             if str(k).upper() in ("ODATE", "ODATE_DATE", "CUTOFF_DATE"):
#                 cutoff_date = str(v).replace("-", "").strip()
#             txt_conf = txt_conf.replace(f'${{{k}}}', v)
#             txt_conf = txt_conf.replace(f'${{?{k}}}', v)
#     dir_reports_name_filename = os.path.join(dir_reports_name, uuaa_name,
#                                              f"{url_conf_name}_{current_datetime_str}_{cutoff_date}.csv")
#     if is_windows:
#         dir_reports_name_filename = dir_reports_name_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_reports_name_filename), exist_ok=True)
#
#     conf_file = ConfigFactory.parse_string(txt_conf)
#     hocons_file = HOCONConverter.to_hocon(conf_file)
#     with open(dir_hocons_filename, "w") as f:
#         f.write(hocons_file)
#
#     spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
#     conf = sc._jvm.java.io.File(dir_hocons_filename)
#     ConfigFactory2 = sc._jvm.com.typesafe.config.ConfigFactory
#     parsed_conf = ConfigFactory2.parseFile(conf)
#     resolve_path = get_replace_resolve_parameter(sc=sc, resolve_name=resolve_name)
#     resolvedConfig = parsed_conf.withFallback(resolve_path).resolve()
#     Standalone = sc._jvm.com.datio.hammurabi.sandbox
#     result = Standalone.Hammurabi.run(spark._jsparkSession, resolvedConfig)
#
#     if result == 2:
#         print(f"{get_color('Problema para construir la ejecución, posible configuración o regla mal definida')} ")
#     else:
#         if result == 1:
#             print(f"{get_color('La validación de calidad falló, la regla crítica falló')} ")
#         elif result == 0:
#             print(
#                 f"{get_color('Ha pasado la validación de calidad. Esto significa que no hay ninguna regla crítica que haya fallado.')} ")
#
#     metrics_df = spark.read.parquet(dir_sandbox_dq_metrics)
#     metrics_filter = metrics_df.filter(
#         func.col("gf_quality_rule_execution_date") >= func.unix_timestamp(func.lit(current_datetime)).cast('timestamp'))
#     df2 = metrics_filter.select(
#         func.col("gf_qr_functional_definition_id"),
#         func.concat(func.col("g_quality_rule_principle_type"),
#                     func.lit("."),
#                     func.col("g_quality_rule_type")).alias("Rule"),
#         func.regexp_replace(func.col("gf_quality_rule_metadata_map.ruleName"),
#                             "com.datio.hammurabi.rules.", ""
#                             ).alias("Rule Name"),
#         func.col("gf_qr_tg_object_physical_name"),
#         func.col("gf_cutoff_date"),
#         func.col("gf_field_physical_name").alias("Field"),
#         func.col("gf_qr_aux_attribute_desc").alias("Format"),
#         func.col("g_qr_critical_type").alias("Is Critical"),
#         func.col("gf_qr_min_acceptance_per").alias("% Acceptation"),
#         func.col("g_quality_rule_status_type").alias("Status"),
#         func.col("gf_quality_rule_compliance_per").alias("Por"))
#     df3 = df2.distinct().sort("gf_qr_functional_definition_id")
#     df3 = df3.select(*[func.col(col).cast("string") for col in df3.columns])
#     df3.show(500, False, True)
#
#     metrics_filter_pandas = df3.toPandas()
#     metrics_filter_pandas.to_csv(dir_reports_name_filename, index=False)
#
#     print(f"{get_color(f'================================')} ")
#     print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
#     print(f"{get_color('table name:')} {get_color_b(table_name)}")
#     print(f"{get_color('conf name :')} {get_color_b(url_conf_name)}")
#     print(f"{get_color('cutoff date:')} {get_color_b(cutoff_date)}")
#     print(f"{get_color('Generating a file csv:')} {get_color_b(dir_reports_name_filename)}")
#     print(f"{get_color('=================================')} ")
#
#
# def dq_run_sandbox_file_with_rules(spark=None,
#                                    sc=None,
#                                    uuaa=None,
#                                    table_name=None,
#                                    parameter_conf_list=None,
#                                    file_conf=None,
#                                    is_prod=True,
#                                    rules_id=None,
#                                    resolve_name="resolve_sandbox.conf"):
#     import json
#     import sys
#     import os
#     from datetime import datetime
#     from tqdm import tqdm
#     from pyhocon import ConfigFactory
#     from pyhocon.converter import HOCONConverter
#     from pyspark.sql import functions as func
#     from spark_quality_rules_tools import get_color, get_color_b
#     from spark_quality_rules_tools import get_replace_resolve_parameter
#
#     is_windows = sys.platform.startswith('win')
#     dir_confs_name = os.getenv('pj_dq_dir_confs_name')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#     dir_reports_name = os.getenv('pj_dq_dir_reports_name')
#     uuaa_code = os.getenv("UUAA_CODE")
#     user_sandbox = os.getenv("JPY_USER")
#     dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
#     dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#     if parameter_conf_list in ("", None):
#         raise Exception(f'required variable parameter_conf_list')
#     if dir_confs_name is None:
#         raise Exception(f'required environment: pj_dq_dir_confs_name')
#     if dir_hocons_name is None:
#         raise Exception(f'required environment: pj_dq_dir_hocons_name')
#     if dir_reports_name is None:
#         raise Exception(f'required environment: pj_dq_dir_reports_name')
#     if uuaa_code is None:
#         raise Exception(f'required environment: UUAA_CODE')
#     if user_sandbox is None:
#         raise Exception(f'required environment: JPY_USER')
#     if dir_sandbox_dq_metrics is None:
#         raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')
#     if resolve_name is None:
#         raise Exception(f'required environment: resolve_name')
#
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#
#     now = datetime.now()
#     current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
#     current_datetime_str = now.strftime("%Y%m%d%H%M")
#
#     dir_confs_filename = os.path.join(dir_confs_name, uuaa_name, f"{url_conf_name}.txt")
#     dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, f"PARAMS-{url_conf_name}.json")
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{table_name}_ruleid_generated.conf")
#
#     if is_windows:
#         dir_confs_filename = dir_confs_filename.replace("\\", "/")
#         dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_hocons_filename), exist_ok=True)
#
#     with open(dir_confs_filename_parameters) as f:
#         parameter_conf = f.read()
#         parameter_conf = json.loads(parameter_conf)
#
#     params_parameter = parameter_conf[uuaa_name][0]["parameters"]
#     validate_parameter_keys = list(set(params_parameter.keys()))
#     validate_parameter_conf_keys = list(set([b for a in parameter_conf_list for b in a.keys()]))
#     validate_compare_parameters = (sorted(validate_parameter_keys) == sorted(validate_parameter_conf_keys))
#     if not validate_compare_parameters:
#         raise Exception(f'Need more variables the parameters: parameter_conf_list')
#
#     cutoff_date = ""
#     with open(dir_confs_filename) as f:
#         txt_conf = f.read()
#
#     txt_conf = txt_conf.replace(f'${{TEST_PATH}}', "")
#     txt_conf = txt_conf.replace(f'${{COUNTRY}}', "pe")
#     txt_conf = txt_conf.replace(f'"/artifactory/"', "/artifactory/")
#     txt_conf = txt_conf.replace(f'${{ARTIFACTORY_UNIQUE_CACHE}}', "http://artifactory-gdt.central-02.nextgen.igrupobbva")
#     if is_prod:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-local")
#     else:
#         txt_conf = txt_conf.replace(f'${{SCHEMAS_REPOSITORY}}', "gl-datio-da-generic-dev-local")
#
#     for params_parameter_conf in tqdm(parameter_conf_list):
#         for k, v in params_parameter_conf.items():
#             if str(k).upper() in ("DATE", "ODATE", "ODATE_DATE", "CUTOFF_DATE", "PROCESS_DATE", "REPROCESS_DATE"):
#                 cutoff_date = str(v).replace("-", "").strip()
#             txt_conf = txt_conf.replace(f'${{{k}}}', v)
#             txt_conf = txt_conf.replace(f'${{?{k}}}', v)
#     dir_reports_name_filename = os.path.join(dir_reports_name, uuaa_name, f"{url_conf_name}_{current_datetime_str}_{cutoff_date}.csv")
#
#     if is_windows:
#         dir_reports_name_filename = dir_reports_name_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_reports_name_filename), exist_ok=True)
#
#     conf_file = ConfigFactory.parse_string(txt_conf)
#     hocons_file = HOCONConverter.to_json(conf_file)
#     json_file = json.loads(hocons_file)
#
#     rule_list = list()
#     hamu_dict = None
#     for hamu, info in json_file.items():
#         dataframeinfo = None
#         input = None
#         if 'dataFrameInfo' in info.keys():
#             dataframeinfo = info["dataFrameInfo"]
#         if 'input' in info.keys():
#             input = info["input"]
#         if 'rules' in info.keys():
#             rules = info["rules"]
#             for rule in rules:
#                 key_id_rule = rule.get("config").get("id", None)
#                 if str(key_id_rule).strip() in rules_id:
#                     rule_list.append(rule)
#         hamu_dict = dict(hammurabi=dict(dataFrameInfo=dataframeinfo, input=input, rules=rule_list))
#     json_file2 = json.dumps(hamu_dict, indent=4)
#     conf2 = ConfigFactory.parse_string(json_file2)
#     hocons_file2 = HOCONConverter.convert(conf2, "hocon")
#     with open(dir_hocons_filename, "w") as f:
#         f.write(hocons_file2)
#
#     spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
#     conf = sc._jvm.java.io.File(dir_hocons_filename)
#     ConfigFactory2 = sc._jvm.com.typesafe.config.ConfigFactory
#     parsed_conf = ConfigFactory2.parseFile(conf)
#     resolve_path = get_replace_resolve_parameter(sc=sc, resolve_name=resolve_name)
#     resolvedConfig = parsed_conf.withFallback(resolve_path).resolve()
#     Standalone = sc._jvm.com.datio.hammurabi.sandbox
#     result = Standalone.Hammurabi.run(spark._jsparkSession, resolvedConfig)
#
#     if result == 2:
#         print(f"{get_color('Problema para construir la ejecución, posible configuración o regla mal definida')} ")
#     else:
#         if result == 1:
#             print(f"{get_color('La validación de calidad falló, la regla crítica falló')} ")
#         elif result == 0:
#             print(
#                 f"{get_color('Ha pasado la validación de calidad. Esto significa que no hay ninguna regla crítica que haya fallado.')} ")
#
#     metrics_df = spark.read.parquet(dir_sandbox_dq_metrics)
#     metrics_filter = metrics_df.filter(
#         func.col("gf_quality_rule_execution_date") >= func.unix_timestamp(func.lit(current_datetime)).cast('timestamp'))
#     df2 = metrics_filter.select(
#         func.col("gf_qr_functional_definition_id"),
#         func.concat(func.col("g_quality_rule_principle_type"),
#                     func.lit("."),
#                     func.col("g_quality_rule_type")).alias("Rule"),
#         func.regexp_replace(func.col("gf_quality_rule_metadata_map.ruleName"),
#                             "com.datio.hammurabi.rules.", ""
#                             ).alias("Rule Name"),
#         func.col("gf_qr_tg_object_physical_name"),
#         func.col("gf_cutoff_date"),
#         func.col("gf_field_physical_name").alias("Field"),
#         func.col("gf_qr_aux_attribute_desc").alias("Format"),
#         func.col("g_qr_critical_type").alias("Is Critical"),
#         func.col("gf_qr_min_acceptance_per").alias("% Acceptation"),
#         func.col("g_quality_rule_status_type").alias("Status"),
#         func.col("gf_quality_rule_compliance_per").alias("Por"))
#     df3 = df2.distinct().sort("gf_qr_functional_definition_id")
#     df3 = df3.select(*[func.col(col).cast("string") for col in df3.columns])
#     df3.show(500, False, True)
#
#     metrics_filter_pandas = df3.toPandas()
#     metrics_filter_pandas.to_csv(dir_reports_name_filename, index=False)
#
#     print(f"{get_color(f'================================')} ")
#     print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
#     print(f"{get_color('table name:')} {get_color_b(table_name)}")
#     print(f"{get_color('conf name :')} {get_color_b(url_conf_name)}")
#     print(f"{get_color('cutoff date:')} {get_color_b(cutoff_date)}")
#     print(f"{get_color('Generating a file csv:')} {get_color_b(dir_reports_name_filename)}")
#     print(f"{get_color('=================================')} ")
#
#
# def dq_validate_artifactory(url_conf=None):
#     import sys
#     import os
#     from spark_quality_rules_tools import get_validate_rules
#
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#
#     url = url_conf
#     url_conf_extension = str(str(url).split("/")[-1]).replace("-", "_").upper().strip()
#     url_conf_name = str(str(url_conf_extension).split(".")[0])
#     uuaa_name = str(str(url).split("/")[-2]).upper()
#     if not len(uuaa_name) == 4:
#         uuaa_name = str(str(url).split("/")[-5]).upper()
#
#     if url_conf in ("", None):
#         raise Exception(f'required variable url_conf')
#
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}.conf")
#     if is_windows:
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     get_validate_rules(hocons_dir=dir_hocons_filename)
#
#
# def dq_validate_file(file_conf=None, uuaa=None):
#     import sys
#     import os
#     from spark_quality_rules_tools import get_validate_rules
#
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}.conf")
#     if is_windows:
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     get_validate_rules(hocons_dir=dir_hocons_filename)
#
#
# def dq_validate_artifactory_with_rules(table_name=None,
#                                        file_conf=None,
#                                        rules_id=None,
#                                        uuaa=None):
#     import sys
#     import os
#     from spark_quality_rules_tools import get_validate_rules
#
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#
#     id_split = str(rules_id).split("_")
#     rule_country = str(id_split[0])
#     rule_type = str(id_split[1])
#     rule_id = str(id_split[-2])
#     rule_correlative = str(id_split[-1])
#
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}_{rule_country}_{rule_type}_{rule_id}_{rule_correlative}.conf")
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{table_name}_ruleid_generated.conf")
#     if is_windows:
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     get_validate_rules(hocons_dir=dir_hocons_filename)
#
#
# def dq_validate_file_with_rules(table_name=None,
#                                 file_conf=None,
#                                 rules_id=None,
#                                 uuaa=None):
#     import sys
#     import os
#     from spark_quality_rules_tools import get_validate_rules
#
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#     url_conf_name = str(str(file_conf).split(".")[0])
#     uuaa_name = str(uuaa).upper()
#
#     if file_conf in ("", None):
#         raise Exception(f'required variable file_conf')
#
#     id_split = str(rules_id).split("_")
#     rule_country = str(id_split[0])
#     rule_type = str(id_split[1])
#     rule_id = str(id_split[-2])
#     rule_correlative = str(id_split[-1])
#
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{url_conf_name}_{rule_country}_{rule_type}_{rule_id}_{rule_correlative}.conf")
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{table_name}_ruleid_generated.conf")
#     if is_windows:
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     get_validate_rules(hocons_dir=dir_hocons_filename)
#
#
# def dq_get_rules_list():
#     import os
#     import json
#     import sys
#     from prettytable import PrettyTable
#     from spark_quality_rules_tools.utils.color import get_color_b
#     from spark_quality_rules_tools.utils import BASE_DIR
#
#     is_windows = sys.platform.startswith('win')
#     json_resource_rules = os.path.join(BASE_DIR, "utils", "resource", "rules.json")
#
#     if is_windows:
#         json_resource_rules = json_resource_rules.replace("\\", "/")
#
#     with open(json_resource_rules) as f:
#         default_rules = json.load(f)
#     rules_config = default_rules.get("rules_config", None)
#
#     t = PrettyTable()
#     t.field_names = [get_color_b("DQ NAME"), get_color_b("VERSION"), get_color_b("DESCRIPTION")]
#     for k, v in rules_config.items():
#         for key_name, value_name in v.items():
#             t.add_row([key_name, value_name[0].get("rules_version"), value_name[0].get("rules_name")])
#     print(t)
#
#
# def dq_generated_rules(rule_id=None,
#                        table_name=None,
#                        category_rule="MVP"):
#     import os
#     import sys
#     import json
#     from pyhocon import ConfigFactory
#     from pyhocon.converter import HOCONConverter
#     from spark_quality_rules_tools.utils.color import get_color_b, get_color
#     from prettytable import PrettyTable
#
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#     uuaa_name = str(table_name.split("_")[1]).upper()
#     dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{table_name}_{rule_id}_generated.conf")
#
#     if is_windows:
#         dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#     os.makedirs(os.path.dirname(dir_hocons_filename), exist_ok=True)
#
#     rs_list = list()
#     hamu_dict, id_key_dict = dq_searching_rules(category_rule=category_rule, table_name=table_name,
#                                                 rule_id=rule_id, static_id=None, sequence="001")
#     rs_list.append(hamu_dict)
#     json_file2 = json.dumps(rs_list, indent=4)
#     conf2 = ConfigFactory.parse_string(json_file2)
#     hocons_file2 = HOCONConverter.convert(conf2, "hocon")
#     with open(dir_hocons_filename, "w") as f:
#         f.write(hocons_file2)
#
#     print(f"{get_color(f'========CREATE RULE============')} ")
#     with open(dir_hocons_filename) as f:
#         res = f.read()
#     print(f"{get_color_b(f'{res}')}")
#
#     print(f"{get_color(f'========MANDATORY============')} ")
#     t = PrettyTable()
#     t.field_names = [get_color_b("DQ NAME"), get_color_b("TYPE")]
#     for key_name, value_name in id_key_dict.items():
#         t.add_row([key_name, value_name])
#     print(t)
#
#
# def dq_run_sandbox_archive_path_rules(spark=None, path=None, category_rule="MVP"):
#     import pandas as pd
#     from pyspark.sql.types import StructType, StructField, StringType
#     from pyspark.sql.window import Window
#     from pyspark.sql import functions as func
#     import os
#     import sys
#     from spark_quality_rules_tools.utils.color import get_color_b, get_color
#     import json
#     from pyhocon import ConfigFactory
#     from pyhocon.converter import HOCONConverter
#
#     global dir_hocons_filename
#     is_windows = sys.platform.startswith('win')
#     dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
#
#     df = pd.read_csv(path, sep=",").fillna("")
#     schema = StructType([
#         StructField("TABLE", StringType(), True),
#         StructField("FIELD", StringType(), True),
#         StructField("SUBPARTITION_ONE", StringType(), True),
#         StructField("SUBPARTITION_TWO", StringType(), True),
#         StructField("VERSION", StringType(), True),
#         StructField("PERIODICITY", StringType(), True),
#         StructField("STATIC_ID", StringType(), True)
#     ])
#     df = spark.createDataFrame(df, schema=schema)
#     df = df.orderBy("TABLE", "FIELD", "VERSION")
#     df = df.withColumn('ORDEN', func.row_number().over(Window.partitionBy(func.lit('1')).orderBy(func.lit('1'))))
#     window_spec = Window.partitionBy("TABLE", "VERSION").orderBy("ORDEN")
#     df = df.withColumn("SEQUENCE", func.row_number().over(window_spec)).orderBy("ORDEN")
#     df2 = df.toPandas()
#     table_dict = dict()
#     table_list = list()
#
#     for index, row in df2.iterrows():
#         table_name = str(row["TABLE"]).strip().lower()
#         field_name = str(row["FIELD"]).strip().lower()
#         subpartition_one = row["SUBPARTITION_ONE"]
#         if subpartition_one not in (None, "", "NaN"):
#             subpartition_one = str(subpartition_one.split("=")[0])
#         subpartition_two = row["SUBPARTITION_TWO"]
#         if subpartition_two not in (None, "", "NaN"):
#             subpartition_two = str(subpartition_two.split("=")[0])
#         rule_id = row["VERSION"]
#         periodicity = str(row["PERIODICITY"]).strip().capitalize()
#         sequence = str(row["SEQUENCE"]).zfill(3)
#         static_id = None if row["STATIC_ID"] in ("", None, "NaN", "Null") else row["STATIC_ID"]
#         uuaa_name = str(table_name.split("_")[1]).lower()
#         uuaa_tag = "".join(table_name.split("_")[2:])
#
#         hamu_dict, id_key_dict = dq_searching_rules(category_rule=category_rule, table_name=table_name,
#                                                     rule_id=rule_id, static_id=static_id, sequence=sequence)
#
#         class_rules = hamu_dict["class"]
#         if class_rules == "com.datio.hammurabi.rules.completeness.ConditionalPerimeterCompletenessRule":
#             if 'drillDown' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['drillDown']
#             if 'subset' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['subset']
#             if 'balanceIds' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['balanceIds']
#             if 'condition' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['condition']
#
#             hamu_dict["config"]["dataValues"] = dict(applyConversions="", paths="", schema=dict(), type="")
#             hamu_dict["config"]["dataValues"]["applyConversions"] = False
#             hamu_dict["config"]["dataValues"]["paths"] = ["variable is required"]
#             hamu_dict["config"]["dataValues"]["schema"]["path"] = "${ARTIFACTORY_UNIQUE_CACHE}/artifactory/${SCHEMAS_REPOSITORY}" \
#                                                                   f"/schemas/pe/{uuaa_name}" \
#                                                                   f"/raw/{uuaa_tag}/latest/{uuaa_tag}.output.schema"
#             hamu_dict["config"]["dataValues"]["type"] = "avro"
#         else:
#             if 'columns' in hamu_dict["config"].keys():
#                 hamu_dict["config"]["columns"] = [field_name]
#             if 'column' in hamu_dict["config"].keys():
#                 hamu_dict["config"]["columns"] = field_name
#             if 'drillDown' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['drillDown']
#             if 'subset' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['subset']
#             if 'balanceIds' in hamu_dict["config"].keys():
#                 del hamu_dict["config"]['balanceIds']
#             if 'withRefusals' in hamu_dict["config"].keys():
#                 hamu_dict["config"]['withRefusals'] = False
#             if 'isCritical' in hamu_dict["config"].keys():
#                 hamu_dict["config"]['isCritical'] = True
#
#         if table_name not in table_dict.keys():
#             table_dict[table_name] = dict(hammurabi=dict())
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"] = dict()
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"]["cutoffDate"] = "${?CUTOFF_DATE}"
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"]["frequencyRuleExecution"] = periodicity
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"]["physicalTargetName"] = f"/data/master/{uuaa_name}/data/{table_name}"
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"]["subset"] = "cutoff_date='${?CUTOFF_DATE}'"
#             if subpartition_one:
#                 table_dict[table_name]["hammurabi"]["dataFrameInfo"]["subset"] = "cutoff_date='${?CUTOFF_DATE}' and " \
#                                                                                  f"{subpartition_one}=" + "'${?SUBPATITION_ONE}'"
#             if subpartition_two:
#                 table_dict[table_name]["hammurabi"]["dataFrameInfo"]["subset"] = "cutoff_date='${?CUTOFF_DATE}' and " \
#                                                                                  f"{subpartition_one}=" + "'${?SUBPATITION_ONE}' and " \
#                                                                                                           f"{subpartition_two}=" + "'${?SUBPATITION_TWO}'"
#             table_dict[table_name]["hammurabi"]["dataFrameInfo"]["uuaa"] = uuaa_name
#             table_dict[table_name]["hammurabi"]["Input"] = dict()
#             table_dict[table_name]["hammurabi"]["Input"]["options"] = dict(includeMetadataAndDeleted=True, overrideSchema=True)
#             table_dict[table_name]["hammurabi"]["Input"]["paths"] = [f"/data/master/{uuaa_name}/data/{table_name}"]
#             table_dict[table_name]["hammurabi"]["Input"]["schema"] = dict(path="${ARTIFACTORY_UNIQUE_CACHE}/artifactory/${SCHEMAS_REPOSITORY}"
#                                                                                f"/schemas/pe/{uuaa_name}"
#                                                                                f"/master/{uuaa_tag}/latest/{uuaa_tag}.output.schema")
#             table_dict[table_name]["hammurabi"]["Input"]["type"] = "parquet"
#             table_dict[table_name]["hammurabi"]["rules"] = list()
#         table_dict[table_name]["hammurabi"]["rules"].append(hamu_dict)
#         table_list.append(table_name)
#
#     table_unique_list = list(set(table_list))
#
#     for table in table_unique_list:
#         uuaa_name = str(table.split("_")[1]).upper()
#         table_name = str(table).lower()
#         dir_hocons_filename = os.path.join(dir_hocons_name, uuaa_name, f"{table_name}_archive_generated.conf")
#         if is_windows:
#             dir_hocons_filename = dir_hocons_filename.replace("\\", "/")
#         os.makedirs(os.path.dirname(dir_hocons_filename), exist_ok=True)
#
#         txt_string = table_dict[table]
#         json_file2 = json.dumps(txt_string, indent=4)
#         conf2 = ConfigFactory.parse_string(json_file2)
#         hocons_file2 = HOCONConverter.convert(conf2, "hocon")
#
#         with open(dir_hocons_filename, "w") as f:
#             f.write(hocons_file2)
#
#         print(f"{get_color('HOCON CREATE:')} {get_color_b(dir_hocons_filename)}")
