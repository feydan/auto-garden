from datetime import datetime
from elasticsearch import Elasticsearch
import json

indices = 'garden,weather,watering,pisystem'
backup_path = '/backup/'

es = Elasticsearch()

now = datetime.now()

# Add this reading to the json
now_formatted = datetime.strftime(now, '%Y-%m-%d')

for index in indices.split(','):
    # Save the file
    with open(backup_path + index + '-' + now_formatted, 'w') as f:
        # Initialize the scroll
        page = es.search(
            index=index,
            scroll='2m',
            size=1000,
            body={}
        )
        scroll_size = page['hits']['total']
        print("Scroll size: " + str(scroll_size))

        # Start scrolling
        while len(page['hits']['hits']) > 0:
            # Do something with the obtained page
            for doc in page['hits']['hits']:
                f.write(json.dumps({'index': {'_index': doc['_index'], '_type': doc['_type'], '_id': doc['_id']}}) + '\n')
                f.write(json.dumps(doc['_source']) + '\n')

            page = es.scroll(scroll_id=page['_scroll_id'], scroll='2m')

