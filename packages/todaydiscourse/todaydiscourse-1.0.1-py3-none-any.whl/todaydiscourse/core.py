from todaydiscourse import config
import os
import json
import random


def get_discourse(path):
    directory = config.get_discourse_path(path)
    json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
    discourse_file = random.choice(json_files)
    with open(os.path.join(directory, discourse_file), 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        selected_data = random.choice(data)

        final_data = {
            'status': '200',
            'msg': '成功',
            'category': os.path.splitext(discourse_file)[0],
            'content': selected_data.get('content'),
            'from': selected_data.get('from'),
            'creator': selected_data.get('creator'),
            'date': selected_data.get('date')
        }

    return final_data