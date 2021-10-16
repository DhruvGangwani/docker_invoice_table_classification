# invoice_table_classification
Classify Invoice table on multiple column classes such as item name, item number, discount, unit price

**To build docker image :**

sudo docker build -t table_classification .

**To create docker container :**

sudo docker run -d -p 5000:8000 -v tb_volume:/logs_directory/

**Inputs** : csv file (invoice table), list of classes 

**Note**: See tb_api_request.png for request info.

**Docker volume** is used to persist logs and input csv files

Uses **google/tapas-base-finetuned-wtq** model to query input table. **No language barrier.**
