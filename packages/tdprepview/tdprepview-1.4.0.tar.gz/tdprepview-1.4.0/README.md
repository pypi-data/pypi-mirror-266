![Logo](https://raw.githubusercontent.com/martinhillebrand/tdprepview/main/media/tdprepview_logo.png)


# tdprepview

Python Package that creates Data Preparation Pipelines in Views written in Teradata-SQL.

## Installation


* pip install tdprepview

## Features

* Pipeline class that allows creating in-DB preprocessing pipelines
* Several Preprocessor functions
* API similar to sklearn.Pipeline

![Preprocessors](https://raw.githubusercontent.com/martinhillebrand/tdprepview/main/media/supportedpreprocessors_v131.png)


## Quickstart

### 1. setting up the pipeline

```python
import teradataml as tdml
database_credentials = {
    # ...
}
DbCon = tdml.create_context(**database_credentials)

myschema, table_train, table_score = "...", "...", "..."
DF_train = tdml.DataFrame(tdml.in_schema(myschema,table_train))
DF_score = tdml.DataFrame(tdml.in_schema(myschema,table_score))

from tdprepview import Pipeline
from tdprepview import (
    StandardScaler, IterativeImputer, PCA, DecisionTreeBinning )

steps = [
    ({"pattern":"^floatfeat_[1-5]$"}, [StandardScaler(), IterativeImputer()], {"suffix":"_imputed"}),
    ({"suffix":"_imputed"}, PCA(n_components=2), {"prefix":"mypca_"}),
    ({"prefix":"mypca_"}, DecisionTreeBinning(target_var="target_class", no_bins=3))
]

mypipeline = Pipeline(steps=steps)

```

### 2.a transform DataFrames directly
this is suitable if you are working in a sandbox Jupyter Notebook
```python
# fit() calculates all necessary statistics in DB
mypipeline.fit(DF=DF_train)
# transform generates SQL syntax based on the chosen Preprocessors and the statistics from fit()
DF_train_transf = mypipeline.transform(DF_train)
DF_score_transf = mypipeline.transform(DF_score)
#... go on with some modelling (e.g. sklearn, TD_DecisionForest,...) 
# and scoring (via BYOM, TD_DecisionForestPredict, ...)
```

### 2.b inspect produced queries
if you want to check the SQL code, that is generated py tdprepview
```python
mypipeline.fit(DF=DF_train)
query_train = mypipeline.transform(DF_train, return_type = "str")
print(query_train)
```
the output: (Note how columns not part of the pipeline are simply forwarded)
```sql
WITH preprocessing_steps AS
(
    SELECT
    row_id AS c_i_35,
    floatfeat_1 AS c_i_36,
    floatfeat_2 AS c_i_37,
    floatfeat_3 AS c_i_38,
    target_class AS c_i_39,
    ZEROIFNULL( (( c_i_36 ) - -0.2331302 ) / NULLIF( 1.747159 , 0) ) AS c_i_40,
    ZEROIFNULL( (( c_i_37 ) - 0.03895576 ) / NULLIF( 1.722347 , 0) ) AS c_i_41,
    ZEROIFNULL( (( c_i_38 ) - 0.2363556 ) / NULLIF( 2.808312 , 0) ) AS c_i_42,
    -1.118451e-08  +  (-0.07714142) * (COALESCE(c_i_41, 1.610355e-09))  +  (-0.1758817) * (COALESCE(c_i_42, -4.838372e-09)) AS c_i_43,
    4.261288e-09  +  (-0.0431946) * (COALESCE(c_i_40, -1.045776e-08))  +  (0.6412595) * (COALESCE(c_i_42, -4.838372e-09)) AS c_i_44,
    -7.079888e-09  +  (-0.118112) * (COALESCE(c_i_40, -1.045776e-08))  +  (0.624912) * (COALESCE(c_i_41, 1.610355e-09)) AS c_i_45,
    (0.2604757) * (c_i_43)  +  (-0.681657) * (c_i_44)  +  (-0.6837369) * (c_i_45) AS c_i_46,
    (-0.1047098) * (c_i_43)  +  (0.6840609) * (c_i_44)  +  (-0.7218702) * (c_i_45) AS c_i_47,
    CASE     WHEN c_i_46 < -2.0 THEN 0     WHEN c_i_46 < -1.236351 THEN 1     WHEN c_i_46 < -1.182989 THEN 2     ELSE 3 END AS c_i_48,
    CASE     WHEN c_i_47 < -2.0 THEN 0     WHEN c_i_47 < -0.3139175 THEN 1     WHEN c_i_47 < 0.2286314 THEN 2     ELSE 3 END AS c_i_49
    FROM
        <input_schema>.<input_table_view> t
)

SELECT
    c_i_35 AS row_id,
    c_i_48 AS mypca_pc_1,
    c_i_49 AS mypca_pc_2,
    c_i_39 AS target_class
FROM
preprocessing_steps t
```

if you want to inspect the pipeline as a chart
```python
mypipeline.plot_sankey()
```
Output:

![Sankey Chart](https://raw.githubusercontent.com/martinhillebrand/tdprepview/main/media/example_sankey.png)



### 2.c persist transformed data as a view for later use
this is suitable and compliant with the Teradata ModelOps-Framework, where training.py and scoring.py 
are separate scripts.

__in `training.py`:__
```python
view_train_transf = table_train+"_transf_v"
view_score_transf = table_score+"_transf_v"

mypipeline.fit(schema_name = myschema, 
               table_name = table_train)

# 3. transform: create views for pipelines
# DF_train_transf is already based on the newly created View
DF_train_transf = mypipeline.transform(
                        schema_name = myschema, 
                        table_name = table_train,
                        # this triggeres the creation of a VIEW, thus the transformation 
                        # pipeline is persited
                        create_replace_view = True, 
                        output_schema_name = myschema, 
                        output_view_name= view_train_transf)

# 3.b create view for scoring table - no need for further inspection, thus no return
mypipeline.transform(   schema_name = myschema, 
                        table_name = table_score,
                        return_type = None,
                        create_replace_view = True, 
                        output_schema_name = myschema, 
                        output_view_name= view_score_transf)

# further steps:
# Model training with DF_train_transf, 
# e.g. local and use BYOM, or in-DB with TD_DecisionForest
# save model in DB
```

__in `scoring.py`:__
```python
view_score_transf = table_score+"_transf_v"
# 1. get DataFrame based on View, transform is happening as per view definition
DF_score_transf = tdml.DataFrame(tdml.in_schema(myschema, view_score_transf))

# 2. Model Scoring with trained model 
# (e.g. PMMLPredict, TD_DecisionForestPredict,...)
# get pointer for model from DB + execute scoring in DB

# 3. Save Scored Data in DB
```

