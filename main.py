
import os
import sys
import argparse
import requests
import logging
import json

def extract_websites_to_crawl(websites):
    # This functions parses the urls of the tools given. Extract the problematic urls for crawling and extract the tools with unique url:
    passing = True
    error_tool = False
    problematic_websites = []
    websites_to_crawl = []
    for url in websites:
        if not url.startswith("http"):
            url = "https://www."  + url
        if url.endswith(".zip") or url.endswith(".pdf") or url.endswith("/pdf") or url.endswith("/png") or url.endswith(".mp4") or url.endswith(".gz") or url.endswith(".bz2") or url.startswith("ftp://") or len(url) < 7:
            problematic_websites.append(url)
        else:
            websites_to_crawl.append(url)
    return problematic_websites, websites_to_crawl

def request_api(url):
    # Make a request to an API to recieve format JSON
    headers = {'Accept' : 'application/json'}
    try:
        with requests.get(url, stream=True, headers = headers ) as r:
            return r.json()
    except Exception as e:
        print(f"ERROR: the website {url} to request is not available at this moment.")
        print(f"INFO: Exception raised: {str(e)}.")
        sys.exit()

def get_websites_unique(tools):
    # Get the uniques websites.
    return list(set([entry['web']['homepage'] for entry in tools]))

def create_dict_to_save(name, websites_array):
    dict_for_json = {}
    dict_for_json.setdefault(name, websites_array)
    return dict_for_json

def write_json_file(data, path):
    # Write on a json file a list of dictionaries:
    with open(path, 'w') as f:
        json.dump(data, f)

def main(args):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %y %H:%M:%S',
                        filename=f'{args.output_directory}/{args.log_file_name}.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(levelname)-12s %(filename)-12s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger().addHandler(console)

    logging.info("Starting the requests. ESTIMATED TIME: 8s.")
    tools = request_api(args.input_url_tools)
    logging.info(f"Total entries: {len(tools)}.")

    unique_websites = get_websites_unique(tools)
    logging.info(f"Unique websites: {len(unique_websites)}.")

    problematic_websites, websites_for_crawling = extract_websites_to_crawl(unique_websites)
    logging.info(f"Websites to crawl: {len(websites_for_crawling)}.")

    final_dict = create_dict_to_save("websites_to_crawl", websites_for_crawling)

    write_json_file(final_dict, f"{args.output_directory}/{args.output_file_name_metrics}.json")
    logging.info(f"Saved websites in {len(websites_for_crawling)}.")

if __name__ == "__main__":
    # Instance of the class ArgumentParser:
    parser = argparse.ArgumentParser(description="Python project to extract websites from API")

    # Add the argument of URL of the api to extract the data:
    parser.add_argument('-input_url_tools',
                        type=str,
                        metavar="",
                        default="https://openebench.bsc.es/monitor/tool",
                        help="The input API url of tools. DEFAULT: https://openebench.bsc.es/monitor/tool"
                        )

    # Add the argument of output's directory name where the output files will be saved:
    parser.add_argument('-output_directory',
                        type=str,
                        metavar="",
                        default="output_data",
                        help="Name of the directory for the outputs files"
                        )

    # Add the argument of output's directory name where the output files will be saved:
    parser.add_argument('-output_file_name_metrics',
                        type=str,
                        metavar="",
                        default="websites_to_crawl",
                        help="Name of the output file of the program"
                        )
    # Add the argument of output's directory name where the output files will be saved:
    parser.add_argument('-log_file_name',
                        type=str,
                        metavar="",
                        default="websites_filer",
                        help="Name of the output log file of the program"
                        )

    args = parser.parse_args()

    # If directory does not exist. Create the directory.
    if not os.path.isdir(args.output_directory):
        os.mkdir(args.output_directory)

    main(args)
    