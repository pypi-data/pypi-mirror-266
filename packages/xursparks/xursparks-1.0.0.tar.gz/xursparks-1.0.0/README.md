** Running XurSparkSMain.py

```
ssh ml-user@13.228.39.91
cd framework
source /app/python/ml/venvp311/bin/activate
python XurSparkSMain.py \
--master=local[*] \
--client-id=trami-data-folder \
--target-table=talentsolutions.candidate_reports \
--process-date=2023-07-05 \
--properties-file=job-application.properties \
--switch=1

```

```
ssh ml-user@13.228.39.91
cd framework
source /app/python/ml/venvp311/bin/activate
python Test.py \
--master=local[*] \
--client-id=trami-data-folder \
--target-table=talentsolutions.candidate_reports \
--process-date=2023-06-06 \
--properties-file=job-application.properties \
--switch=1

```

*SPARK-SUBMIT
```
spark-submit XurSparkSMain.py \
--master=local[*] \
--client-id=trami-data-folder \
--target-table=talentsolutions.candidate_reports \
--process-date=2023-05-24 \
--properties-file=job-application.properties \
--switch=1
```

## Synthesia
```
ssh ml-user@13.228.39.91
cd framework
source /app/python/ml/venvp311/bin/activate
python Test.py \
--master=local[*] \
--client-id=trami-data-folder \
--target-table=talent_solutions.candidates_model_synthesia \
--process-date=2023-06-06 \
--properties-file=job-application.properties \
--switch=1

```

*Hadoop Sir Andy Setp
```
spark-submit framework/AiLabsCandidatesDatamart.py \
--master=spark://13.251.237.177:7077 \
--deploy-mode=cluster \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-15 \
--properties-file=framework/job-application.properties \
--switch=1
```

*Hadoop Sir Andy Setp
```
python AiLabsCandidatesDatamart.py \
--master=local[*] \
--deploy-mode=cluster \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-15 \
--properties-file=job-application.properties \
--switch=1
```

*Hadoop
```
spark-submit \
--name AiLabsCandidatesDatamart \
--master yarn \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar \
--conf spark.yarn.dist.files=job-application.properties \
AiLabsCandidatesDatamart.py \
--keytab=hive.keytab \
--principal=hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--master=yarn \
--deploy-mode=cluster \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-16 \
--properties-file=job-application.properties \
--switch=1
```

*Hadoop 3.3.2
``` 
spark-submit \
--name AiLabsCandidatesDatamart \
--master yarn \
--keytab hive.keytab \
--principal hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar,hive-jdbc-3.1.3.jar \
--conf spark.yarn.dist.files=job-application.properties \
AiLabsCandidatesDatamart.py \
--keytab=hive.keytab \
--principal=hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--master=yarn \
--deploy-mode=client \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-17 \
--properties-file=job-application.properties \
--switch=1
```
*Hadoop testhdfs 3.3.2
``` 
spark-submit \
--name HdfsTest \
--master yarn \
--deploy-mode client \
--keytab hive.keytab \
--principal hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar \
--conf spark.yarn.dist.files=job-application.properties \
--driver-memory 4g \
--executor-memory 4g \
--executor-cores 2 \
HdfsTest.py \
--keytab=hive.keytab \
--principal=hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--master=yarn \
--deploy-mode=cluster \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-16 \
--properties-file=job-application.properties \
--switch=1
```

*Hadoop
```
spark-submit \
--name AiLabsCandidatesDatamart \
--master yarn \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar,hive-jdbc-3.1.3.jar \
--conf spark.yarn.dist.files=job-application.properties \
AiLabsCandidatesDatamart.py \
--master=yarn \
--deploy-mode=client \
--client-id=trami-data-folder \
--target-table=ailabs.candidates_transformed \
--process-date=2023-11-19 \
--properties-file=job-application.properties \
--switch=1
```

*Hadoop Employees
``` 
spark-submit \
--name AiLabsEmployeeDatamart \
--master yarn \
--keytab hive.keytab \
--principal hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar,hive-jdbc-3.1.3.jar,spark-excel_2.12-3.5.0_0.20.1.jar \
--conf spark.yarn.dist.files=job-application.properties \
AiLabsEmployeeDatamart.py \
--keytab=hive.keytab \
--principal=hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--master=yarn \
--deploy-mode=client \
--client-id=trami-data-folder \
--target-table=ailab.employees \
--process-date=2023-11-30 \
--properties-file=job-application.properties \
--switch=1
```

*Hadoop Candidates
``` 
spark-submit \
--name AiLabsHdfsDatamart \
--master yarn \
--keytab hive.keytab \
--principal hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--jars aws-java-sdk-bundle-1.12.262.jar,hadoop-aws-3.3.4.jar,hive-jdbc-3.1.3.jar,spark-excel_2.12-3.5.0_0.20.1.jar \
--conf spark.yarn.dist.files=job-application.properties \
AiLabsHdfsDatamart.py \
--keytab=hive.keytab \
--principal=hive/hdfscluster.local@HDFSCLUSTER.LOCAL \
--master=yarn \
--deploy-mode=client \
--client-id=trami-data-folder \
--target-table=ailab.candidates_transformed_hdfs \
--process-date=2023-11-19 \
--properties-file=job-application.properties \
--switch=1
```