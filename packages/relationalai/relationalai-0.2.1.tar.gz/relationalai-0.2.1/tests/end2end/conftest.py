import os
import random
import pytest
import relationalai as rai
from relationalai.clients import config as cfg

@pytest.fixture(scope="session")
def engine_config():
    # If there's a local config file, use it, including
    # the engine specified there.
    config = cfg.Config()
    if config.file_path is not None:
        yield config
        return

    client_id = os.getenv('RAI_CLIENT_ID')
    client_secret = os.getenv('RAI_CLIENT_SECRET')

    if client_id is None or client_secret is None:
        raise ValueError("RAI_CLIENT_ID and RAI_CLIENT_SECRET must be set")

    # Otherwise, create a new engine and delete it afterwards.
    random_number = random.randint(1000000000, 9999999999)
    engine_name = f"pyrel-test-{random_number}"
    
    config = make_config(engine_name, client_id, client_secret)
    
    print(f"Creating engine {engine_name}")
    provider = rai.Resources(config=config)
    provider.create_engine(engine_name, 'XS')
    
    yield config
    
    print(f"Deleting engine {engine_name}")
    provider.delete_engine(engine_name)

def make_config(engine_name: str, client_id: str, client_secret: str) -> cfg.Config:
    # Running against prod
    return cfg.Config({
        'platform': "azure",
        'host': "azure.relationalai.com",
        'port': "443",
        'region': "us-east",
        'scheme': "https",
        'client_credentials_url': "https://login.relationalai.com/oauth/token",
        'client_id': client_id,
        'client_secret': client_secret,
        'engine': engine_name,
    })
