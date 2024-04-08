import json
import time

import requests
from requests.exceptions import HTTPError


def do_api_query(args, api_key):
    attempts = 0
    while attempts < 3:
        try:
            query_string = args["query_string"]
            print("Query string: " + query_string)  # Do not log the API key

            all_data = []
            url = query_string.replace("YOUR_API_KEY", api_key)
            n = 0

            while url:
                response = requests.get(url)
                if response.status_code == 401 or response.status_code == 403:
                    return json.dumps(response.json(), default=vars)

                response.raise_for_status()  # Will raise HTTPError for 4XX/5XX responses
                data = response.json()

                if 'results' in data:
                    if type(data['results']) is list:
                        all_data.extend(data['results'])
                    else:
                        all_data.append(json.dumps(data['results']))

                    n += 1
                    if n > 20 or len(all_data) > 1000:
                        print("Too many queries: " + str(n) + " or results: " + str(len(all_data)) + ". Stopping.")
                        break
                else:
                    all_data.append(json.dumps(data))

                # Check if there's a next URL and update the url variable
                url = data.get('next_url', None)
                print("Next URL: " + str(url))  # Do not log the API key
                url = url + "&apiKey=" + api_key if url else None

            return json.dumps(all_data, default=vars)

        except HTTPError as e:
            if e.response.status_code in [429, 502]:
                print("Attempt #" + str(attempts) + " Error: " + str(e))
                print("Rate limit exceeded or server error. Waiting for 5 seconds...")
                time.sleep(5)
                attempts += 1
            else:
                # Reraise the exception for any other HTTP errors
                return str(e)

        except Exception as e:
            return str(e)
