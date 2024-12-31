from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID

from app.common.config import config

keycloak_openid = KeycloakOpenID(
    server_url=config.KEYCLOAK_SERVER_URL,
    client_id=config.KEYCLOAK_CLIENT_ID,
    realm_name=config.KEYCLOAK_REALM_NAME,
    client_secret_key=config.KEYCLOAK_SECRET_KEY,
)
