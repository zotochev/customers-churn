import requests
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime


def main():
    if len(sys.argv) == 3 \
            and sys.argv[2][sys.argv[2].rfind('.'):] == '.csv':
        file = Path(sys.argv[2])
        if file.is_file() \
                and not file.is_dir():
            csv_data = pd.read_csv(sys.argv[2])
            data = csv_data.to_json(orient="split")
        else:
            print('Error data to predict has wrong type, not a file or does not exist')
            return None

        url = sys.argv[1]
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.post(url, data=json.dumps(data), headers=headers)
        print("status code: ", r.status_code)

        if r.status_code == 200:
            parsed = json.loads(r.json())
            if set(parsed.keys()) != set(['index', 'columns', 'data']):
                print('insert_json_data: Json data has wrong keys')
                return None
            predictions = pd.DataFrame(
                    parsed['data'],
                    index=parsed['index'],
                    columns=parsed['columns']
                    )

            file_name = "{}_predictions_{}.csv".format(sys.argv[2][:sys.argv[2].rfind('.')], datetime.now().strftime('%m%d%Y_%H_%M_%S'))
            predictions.to_csv(file_name, index=False)
            print("Prediction is complite. Results in \"{}\" file".format(file_name))
        else:
            print("Error: Unexpected server answer.")

    else:
        print('Error: Wrong usage')
        print('Example: python3 {} "{}" "{}"'.format(sys.argv[0], 'http:://<api_ip>:<api_port>', '<data_to_predict>.csv'))


if __name__ == "__main__":
    main()
