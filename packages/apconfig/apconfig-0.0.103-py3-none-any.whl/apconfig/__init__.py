import os

import requests


def get_api_setup_data():
    try:
        with requests.Session() as session:
            response = session.get(url=f"http://{os.getenv('TSO_SETUP_URL')}/setup")
            response.raise_for_status()
            setup = response.json()
            return setup

    except Exception as e:
        raise


setup_data = get_api_setup_data()

# TSO Configuration
chains = ['coston', 'coston2', 'songbird', 'flare']

# Data Service Streamers and APIs
WS = 'ws://'
WSS = 'wss://'
HTTP = 'http://'
HTTPS = 'https://'

tso_utilities_streamer_endpoint = setup_data["algorithms"]["streamers"]["utilities"]["url"]
tso_prepared_streamer_endpoint = setup_data["algorithms"]["streamers"]["prepared"]["url"]
tso_trades_streamer_endpoint = setup_data["algorithms"]["streamers"]["trades"]["url"]

streams = {
    'utilities': tso_utilities_streamer_endpoint,
    'prepared': tso_prepared_streamer_endpoint,
    'trades': tso_trades_streamer_endpoint
}

tso_utility_topics = [topic for topic in setup_data["algorithms"]["tso"]["utility_topics"]]
print(tso_utility_topics)

# voting_round_symbol_data_endpoint = setup_data["algorithms"]["data"]["voting_round_symbol_data"]["url"]


# CHAIN VOTING ROUNDS
algorithm_prepared_data_buffer = 17
ml_predictions_buffer = 12
submission_commit_buffer = 7

# Web3 Providers
web3_provider_list: dict = {}
web3_websocket_list: dict = {}
for chain in chains:
    try:
        web3_provider_list[chain] = setup_data["chains"][chain]["providers"]["rpc"]
        web3_websocket_list[chain] = setup_data["chains"][chain]["providers"]["ws"]
    except Exception as e:
        print(e)

test_web3_provider_list = [os.getenv("WEB3_PROVIDER")]
test_web3_websocket_list = [os.getenv("WEB3_WEBSOCKETS")]

# Chain Wallet Configuration
ftso_reward_offers_manager_addresses = {}
for chain in chains:
    try:
        ftso_reward_offers_manager_addresses[chain] \
            = setup_data["chains"][chain]["ftso_reward_offers_manager_address"]
    except Exception as e:
        print(e)

# Database Configuration
environment = os.getenv("ENVIRONMENT")

assert environment is not None, "Environment not set. "
assert environment in ['development', 'production'], f"Environment has invalid value. Must be 'development' or 'production'."
assert environment in setup_data["environments"], f"Environment {environment} not found in setup data. "

mongo_database_name = setup_data["environments"][environment]["databases"]["mongo"]["name"]
mongo_database_uri = setup_data["environments"][environment]["databases"]["mongo"]["uri"]

# Chain Feeds and Symbols
all_chain_feeds = setup_data["assets"]
all_chain_symbols = setup_data["symbols"]

active_feed = os.getenv("FEED")
# assert active_feed in all_chain_feeds, f"Feed {active_feed} not found in setup data. "
