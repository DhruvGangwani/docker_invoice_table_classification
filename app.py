from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTableQuestionAnswering
from mtranslate import translate
import json, os
import pandas as pd
from flask import Flask, request, jsonify

tokenizer = AutoTokenizer.from_pretrained("google/tapas-base-finetuned-wtq")
model = AutoModelForTableQuestionAnswering.from_pretrained("google/tapas-base-finetuned-wtq")
tb_model = pipeline('table-question-answering', model=model, tokenizer=tokenizer)

app = Flask(__name__)


def table_translation(df):
	header = df.columns
	translated_header = [translate(element, 'en') for element in header]
	df.columns = translated_header
	return df


def logs(file_name, ques_answer, logs_file):
	start_line = "***********START***********\n"
	with open(logs_file, 'a') as f:
		f.write(start_line)
		f.write(f'File name : {file_name}\n')
		for element in ques_answer:
	  		f.write(f'question : {element}\n')
	  		f.write(f'answer : {ques_answer[element]}\n')


@app.route('/table', methods=['POST', 'GET']) #df, table_classes, file_name, logs_dir = 'logs_directory'
def table_classification():
	table_classes = request.form.get('classes', None).split(',')
	
	if not table_classes:
		return {"status": "Failed", "message": "List of classes not found"}, 400

	if table_classes == ['']:
		return {"status": "Failed", "message": "List of table_classes is empty"}, 400
	
	logs_dir = 'logs_directory'
	file_name = request.files['file_name']
	content = pd.read_csv(file_name)
	content.to_csv(os.path.join(logs_dir, file_name.filename))
	
	
	#translation
	translated_df = table_translation(content) #translation
	
	#preprocess
	result = translated_df.to_dict("list")
	preprocess_result = {str(k): [str(value) for value in v] for k,v in result.items()}
	result_df = pd.DataFrame.from_dict(preprocess_result)
	
	structured_queries = [f'values of {query} column' for query in table_classes]

	#model
	result = tb_model(table = result_df, query = structured_queries)
	answers = [x['cells'] for x in result]
	ques_answer = dict(zip(structured_queries, answers))

	#logs
	if not os.path.exists(logs_dir):
		os.makedirs(logs_dir)
	logs_file = 'logs.txt'
	logs(os.path.join(logs_dir, file_name.filename), ques_answer, os.path.join(logs_dir, logs_file))

	return {'status': "success", "result": json.dump(ques_answer)}, 200

if __name__ == '__main__':
	app.run('0.0.0.0', port=5000, debug=True)