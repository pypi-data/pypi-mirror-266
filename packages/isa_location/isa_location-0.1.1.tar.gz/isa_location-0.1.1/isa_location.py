from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk

es = Elasticsearch(['http://192.168.150.196:9900'], http_auth=('syahidah', 'Sy4h1d@ha2k24'), timeout=3200)

def get_data_from_index():
    index_name = 'isa-location-*'
    query_text = {
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "must_not": [
                                {
                                    "exists": {
                                        "field": "content_location_location_coordinate"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "exists": {
                            "field": "content_location_location_longitude"
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "created_at": {
                    "order": "desc"
                }
            }
        ]
    }

    try:
        scanner = scan(client=es, preserve_order=True, query=query_text, index=index_name, scroll='100m', raise_on_error=False)
        for hit in scanner:
            yield {'_index': hit['_index'], 'data': hit['_source']}
    except Exception as e:
        print(f"Error: {e}")


def get_data_from_api(datas):
    try:
        for data in datas:
            index_name = data['_index']
            source = data['data']
            document_id = source.get('id')
            longitude = source.get('content_location_location_longitude')
            latitude = source.get('content_location_location_latitude')
            coordinate = [longitude, latitude]

            if latitude < -90 or latitude > 90:        
                coordinate = [latitude, longitude]

            update_doc = {
                "_op_type": "update",
                "_index": index_name, 
                "_id": document_id,
                "doc": {"content_location_location_coordinate": coordinate}
            }
            yield update_doc

    except Exception as e:
        print(f"error : {e}")

def update_data():
    for success, info in streaming_bulk(es, get_data_from_api(get_data_from_index()), chunk_size=1000):
        if not success:
            print(f"error {info}")
        else:
            print(f"Document with ID {info['update']['_id']} updated.")

for data in get_data_from_index():
    print(data)
