import hvac


def read_secret_data(secret_path: str, vault_token_env: str = "DATA_VAULT_TOKEN",
                     url: str='https://secure-vault.srv.goods.local'):
    """
    Функция для получения доступов из vault
    :param secret_path: Название секрета в DAS_team
    :param vault_token_env: токент доступа
    :param url: url vault
    :return: Словарь с секретами

    пример:
        secret_data = read_secret_data('ИМЯ', token_vault)
    """
    client = hvac.Client(url, token=vault_token_env, verify=False)
    assert client.is_authenticated()
    secret = client.secrets.kv.v1.read_secret(path=f'goods/merchants/DAS_team/{secret_path}', mount_point='secrets')
    return secret.get('data')
