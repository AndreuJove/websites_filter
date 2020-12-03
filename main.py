
import json
import logging
import os
import sys
import argparse
import requests

def extract_websites_to_crawl(websites):
    # Extract the problematic and return the good websites for crawl.
    problematic_websites = []
    websites_to_crawl = []
    for url in websites:
        if not url.startswith("http"):
            url = "https://www."  + url
        if url.endswith((".zip", ".pdf", "/pdf", "/png", "/.mp4", ".gz", ".bz2")) or url.startswith("ftp://") or len(url) < 7:
            problematic_websites.append(url)
        else:
            websites_to_crawl.append(url)
    return websites_to_crawl

def request_api(url, logger):
    # Make a request to an API to recieve format JSON
    headers = {'Accept' : 'application/json'}
    try:
        with requests.get(url, stream=True, headers = headers, timeout=20) as response:
            return response.json()
    except Exception as exception:
        logger.error(f"The website {url} to request is not available at this moment.")
        logger.error(f"Exception raised: {str(exception)}.")
        sys.exit()

def get_websites_unique(tools):
    # Get the uniques websites.
    return list(set([entry['web']['homepage'] for entry in tools]))

def create_dict_to_save(name, websites_array):
    # Create the final dict key value
    dict_for_json = {}
    dict_for_json.setdefault(name, websites_array)
    return dict_for_json

def write_json_file(data, path):
    # Write on a json file a list of dictionaries:
    with open(path, 'w') as file:
        json.dump(data, file)

def main(args):
    # Set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %y %H:%M:%S',
                        filename=f'{args.log_file_name}.log',
                        filemode='w')
    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # Set a format which is simpler for console use.
    formatter = logging.Formatter('%(levelname)-12s %(filename)-12s %(message)s')

    # Tell the handler to use this format.
    console.setFormatter(formatter)

    # Add the handler to the root logger.
    logging.getLogger().addHandler(console)

    logging.info("Starting the requests. ESTIMATED TIME: 8s.")

    # Request the API.
    tools = request_api(args.input_url_tools, logging)
    logging.info(f"Total entries: {len(tools)}.")

    # Get uniques websites from tools.
    unique_websites = get_websites_unique(tools)
    logging.info(f"Unique websites: {len(unique_websites)}.")

    # Filter websites for crawler.
    websites_for_crawling = extract_websites_to_crawl(unique_websites)
    logging.info(f"Websites to crawl: {len(websites_for_crawling)}.")

    # Create the final dict to save.
    final_dict = create_dict_to_save("websites_to_crawl", websites_for_crawling)

    # Save dict to JSON.
    write_json_file(final_dict, f"{args.output_directory}/{args.output_file_name_metrics}.json")

    logging.info(f"Saved websites ({len(websites_for_crawling)}) in {args.output_directory}/{args.output_file_name_metrics}.json")

if __name__ == "__main__":
    # Instance of the class ArgumentParser:
    parser = argparse.ArgumentParser(description="Python project to extract websites from API")

    # Add the argument of URL of the api to extract the data:
    parser.add_argument('-input_url_tools',
                        type=str,
                        metavar="",
                        default="https://openebench.bsc.es/monitor/tool",
                        help="The input API url of tools. Default https://openebench.bsc.es/monitor/tool"
                        )

    # Add the argument of output's directory name where the output files will be saved.
    parser.add_argument('-output_directory',
                        type=str,
                        metavar="",
                        default="output_data",
                        help="Name of the directory for the outputs files"
                        )

    # Add the argument of output's filename.
    parser.add_argument('-output_file_name_metrics',
                        type=str,
                        metavar="",
                        default="websites_to_crawl",
                        help="Name of the output file of the program"
                        )
    # Add the argument of output's filename of log.
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
