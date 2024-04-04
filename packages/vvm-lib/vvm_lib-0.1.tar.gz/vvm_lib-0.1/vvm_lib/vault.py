import hvac



def read_secret_data(secret_path: str, vault_token_env: str = "DATA_VAULT_TOKEN"):
    client = hvac.Client(url='https://secure-vault.srv.goods.local',token=vault_token_env, verify=False)
    assert client.is_authenticated() 
    secret = client.secrets.kv.v1.read_secret(path=f'goods/merchants/DAS_team/{secret_path}', mount_point='secrets')
    return secret.get('data')
