# spark_quality_rules_tools

[![Github License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Updates](https://pyup.io/repos/github/woctezuma/google-colab-transfer/shield.svg)](pyup)
[![Python 3](https://pyup.io/repos/github/woctezuma/google-colab-transfer/python-3-shield.svg)](pyup)
[![Code coverage](https://codecov.io/gh/woctezuma/google-colab-transfer/branch/master/graph/badge.svg)](codecov)

spark_quality_rules_tools is a Python library that implements quality rules in sandbox

## Installation

The code is packaged for PyPI, so that the installation consists in running:


## Usage

wrapper run hammurabies

## Sandbox
## Installation
```sh
!yes| pip uninstall spark-quality-rules-tools
```

```sh
pip install spark-quality-rules-tools --user --upgrade
```

## IMPORTS
```sh
import os
import pyspark
from spark_quality_rules_tools import dq_path_workspace
from spark_quality_rules_tools import dq_download_jar
from spark_quality_rules_tools import dq_spark_session
from spark_quality_rules_tools import dq_extract_parameters
from spark_quality_rules_tools import dq_run_sandbox
from spark_quality_rules_tools import dq_validate_conf
from spark_quality_rules_tools import dq_validate_rules
from spark_quality_rules_tools import show_spark_df
pyspark.sql.dataframe.DataFrame.show2 = show_spark_df
```

## Variables
```sh
project_sda="SDA_37036"
url_conf = "http://artifactory-gdt.central-02.nextgen.igrupobbva/artifactory/gl-datio-spark-libs-maven-local/com/datiobd/cdd-hammurabi/4.0.9/DQ_LOCAL_CONFS/KCOG/KCOG_branch_MRField.conf"
```


## Creating Workspace
```sh
dq_path_workspace(project_sda=project_sda)
```


## Download haas jar
```sh
dq_download_jar(haas_version="4.8.0", force=True)
```


## Spark Session
```sh
spark, sc = dq_spark_session()
```


## Validate Conf
```sh
dq_validate_conf(url_conf=url_conf)
```


## Extract Params
```sh
dq_extract_parameters(url_conf=url_conf)
```


## Json params
```sh
parameter_conf_list = [
 {      
    "ARTIFACTORY_UNIQUE_CACHE": "http://artifactory-gdt.central-02.nextgen.igrupobbva",
    "ODATE_DATE": "2022-11-11",
    "COUNTRY_ID": "PE",
    "SCHEMA_PATH": "t_kcog_branch.output.schema",
    "CUTOFF_DATE": "2022-11-11",
    "SCHEMAS_REPOSITORY": "gl-datio-da-generic-local/schemas/pe/kcog/master/t_kcog_branch/latest/"
 }
]
```


## Run 
```sh
dq_run_sandbox(spark=spark,
               sc=sc,
               parameter_conf_list=parameter_conf_list,
               url_conf=url_conf)
```

               
```sh         
df = spark.read.csv("file:/var/sds/homes/P030772/workspace/data_quality_rules/data_reports/KCOG/KCOG_BRANCH_MRFIELD_202304120046_20221111.csv", 
                    header=True)                 
df.show2(100)
```


## Run 
```sh
dq_validate_rules(url_conf=url_conf)
```


## License

[Apache License 2.0](https://www.dropbox.com/s/8t6xtgk06o3ij61/LICENSE?dl=0).

## New features v1.0

## BugFix

- choco install visualcpp-build-tools

## Reference

- Jonathan Quiza [github](https://github.com/jonaqp).
- Jonathan Quiza [RumiMLSpark](http://rumi-ml.herokuapp.com/).
