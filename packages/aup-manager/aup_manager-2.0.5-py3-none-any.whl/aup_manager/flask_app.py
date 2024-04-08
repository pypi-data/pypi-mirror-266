import base64
import importlib
import json
import time

import requests
import yaml
from connexion import FlaskApp
from flask import Response, render_template, redirect, session, url_for, request
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession
from markdown2 import markdown
from swagger_ui_bundle import swagger_ui_3_path
from werkzeug.exceptions import Unauthorized
from jwcrypto import jwk, jwt, jws
from urllib import parse

from aup_manager.connectors.ConnectorInterface import ConnectorInterface
from aup_manager.db.MongodbDatabase import MongodbDatabase
from aup_manager.models import Acceptance, Status, Aup, Admin, Request

with open("/etc/aup-manager.yaml", "r") as yaml_file:
    cfg = yaml.safe_load(yaml_file)

flask_app = FlaskApp(__name__)

DATABASE = MongodbDatabase(cfg["mongodb"])

CONNECTOR_MODULE, _, CONNECTOR_CLASS_NAME = cfg["connector_class"].rpartition(".")
connector_class = getattr(
    importlib.import_module(CONNECTOR_MODULE), CONNECTOR_CLASS_NAME
)
CONNECTOR: ConnectorInterface = connector_class(cfg["connectors"][CONNECTOR_CLASS_NAME])
EXT_SRC_NAME = cfg["connectors"].get("ext_source_name")

HOSTNAME = cfg["hostname"]
INTROSPECT_URL = cfg["OAuth2"]["introspect_url"]
AUTHORIZATION_URL = cfg["OAuth2"]["authorization_url"]
TOKEN_URL = cfg["OAuth2"]["token_url"]
CLIENT_ID = cfg["OAuth2"]["client_id"]
CLIENT_SECRET = cfg["OAuth2"]["client_secret"]

client_metadata = ClientMetadata(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
flask_app.app.config.update(
    OIDC_REDIRECT_URI=f"{HOSTNAME}/oidc_callback",
    SECRET_KEY=cfg["secret"],
    post_logout_redirect_uris=[f"{HOSTNAME}/logout", HOSTNAME],
)
provider_config = ProviderConfiguration(
    issuer=cfg["OIDC"]["issuer"], client_metadata=client_metadata
)
auth = OIDCAuthentication({"default": provider_config})

ACCEPT_AUPS_MESSAGE = cfg.get(
    "accept_aups_message",
    "Before proceeding to service, you have to accept following acceptable use "
    "policies. These policies restrict the ways in which the service may be used "
    "and set guidelines as to how it should be used.",
)

TOKEN_ALG = cfg["jwks"]["token_alg"]
KEY_ID = cfg["jwks"]["key_id"]
KEYSTORE = cfg["jwks"]["keystore"]

JWK_SET = jwk.JWKSet()
with open(KEYSTORE, "r") as file:
    JWK_SET.import_keyset(file.read())
JSON_WEB_KEY = JWK_SET.get_key(KEY_ID)


def token_info(token):
    b64_client_id_secret = base64.urlsafe_b64encode(
        f"{CLIENT_ID}:" f"{CLIENT_SECRET}".encode()
    ).decode()
    response = requests.get(
        INTROSPECT_URL,
        params={"token": token},
        headers={"Authorization": f"Basic {b64_client_id_secret}"},
    )
    if response.status_code != 200:
        raise Unauthorized
    return response.json()


def exception_handler(error):
    return {
        "detail": str(error),
        "status": 500,
        "title": "Internal Server Error",
    }, 500


def get_user_accepted_aups(user_id, entity_type_id):
    entity_type_ids = CONNECTOR.get_relevant_entity_id_types(entity_type_id, user_id)
    aups = DATABASE.get_user_accepted_aups_by_condition(user_id, entity_type_ids)
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def get_all_user_accepted_aups(user_id):
    aups = DATABASE.get_all_user_accepted_aups(user_id)
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def get_user_not_accepted_aups(user_id, entity_type_id):
    entity_type_ids = CONNECTOR.get_relevant_entity_id_types(entity_type_id, user_id)
    aups = DATABASE.get_user_not_accepted_aups_by_condition(user_id, entity_type_ids)
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def user_accepted_aups(body):
    __save_acceptances(body["user_id"], list(body["aup_ids"]))
    return Response("Success", 200)


def __save_acceptances(user_id, aup_ids):
    acceptances_list = []
    for aup_id in aup_ids:
        acceptance = Acceptance(
            aup_id,
            str(user_id),
            time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
        )
        acceptances_list.append(acceptance)
    if acceptances_list:
        DATABASE.insert_acceptances(acceptances_list)


def verify_jwt(token):
    return jwt.JWT(jwt=token, key=JSON_WEB_KEY).claims


@flask_app.route("/accept_aups/<message>")
def accept_aups(message):
    try:
        message = json.loads(verify_jwt(message))
    except jws.InvalidJWSSignature:
        return Response(json.dumps({"fail": "Invalid signature"}), 400)
    user_id = message.get("user_id")
    entity_type_id = message.get("entity_type_id")
    callback_url = message.get("callback_url")
    nonce = message.get("nonce")
    accept_aups_message = message.get("accept_aups_message", ACCEPT_AUPS_MESSAGE)

    if DATABASE.get_request_by_nonce(nonce):
        return Response(json.dumps({"fail": "Replay attack."}), 403)

    if not user_id or not entity_type_id or not callback_url or not nonce:
        return Response(json.dumps({"fail": "Missing request parameter."}), 400)
    entity_type_ids = CONNECTOR.get_relevant_entity_id_types(entity_type_id, user_id)
    aups = DATABASE.get_user_not_accepted_aups_by_condition(user_id, entity_type_ids)
    if len(aups) == 0:
        DATABASE.save_request(Request(nonce, user_id, status=Status.SUCCESS))
        return redirect(callback_url + "?" + parse.urlencode({"nonce": nonce}))
    aups_as_dict = [aup.__dict__ for aup in aups]

    session["accept_user_id"] = user_id
    session["callback_url"] = callback_url
    session["aup_ids"] = [aup["_id"] for aup in aups_as_dict]
    session["nonce"] = nonce

    DATABASE.save_request(Request(nonce, user_id))

    return render_template(
        "accept_aups.html", aups=aups_as_dict, accept_aups_message=accept_aups_message
    )


@flask_app.route("/save_acceptances")
def save_acceptances():
    user_id = session.pop("accept_user_id", None)
    nonce = session.pop("nonce", None)
    callback_url = session.pop("callback_url", None)
    aup_ids = session.pop("aup_ids", None)
    if not user_id or not nonce or not callback_url or not aup_ids:
        return Response(json.dumps({"fail": "Missing attribute in session."}), 400)

    internal_request = DATABASE.get_request_by_nonce(nonce)
    if (
        not internal_request
        or internal_request.status != internal_request.status.FAILURE
    ):
        return Response(json.dumps({"fail": "Invalid nonce."}), 403)
    __save_acceptances(user_id, aup_ids)
    DATABASE.make_request_success(internal_request.get_id())
    return redirect(callback_url + "?" + parse.urlencode({"nonce": nonce}))


@flask_app.route("/get_accept_result/<message>")
def get_accept_result(message):
    try:
        message = json.loads(verify_jwt(message))
    except jws.InvalidJWSSignature:
        return Response(json.dumps({"fail": "Invalid signature"}), 400)
    nonce = message.get("nonce")
    user_id = message.get("user_id")
    if not nonce or not user_id:
        return Response(json.dumps({"fail": "Missing request parameter."}), 400)
    internal_request = DATABASE.get_request_by_nonce(nonce)
    if (
        not internal_request
        or internal_request.user_id != user_id
        or internal_request.status == Status.FAILURE
    ):
        response = cfg["responses"]["failure"]
    elif internal_request.status == Status.SUCCESS:
        DATABASE.make_request_invalid(internal_request.get_id())
        response = cfg["responses"]["success"]
    elif internal_request.status == Status.INVALID:
        response = cfg["responses"]["invalid-request"]
    else:
        response = "error"
    response_dict = {
        "result": response,
        "nonce": internal_request.nonce,
    }
    return Response(json.dumps(response_dict), 200)


@flask_app.route("/")
def admin_login():
    user_session = UserSession(session, "default")
    if user_session.is_authenticated():
        return redirect(url_for("aup_overview"))
    return render_template("login.html")


@flask_app.route("/logout")
@auth.oidc_logout
def logout():
    session.clear()
    return render_template(
        "text_message.html", text_msg="You were successfully logged out."
    )


def gui_conditions_to_type_id(gui_conditions):
    result = []
    for outer in range(len(gui_conditions)):
        result.append([])
        for condition in gui_conditions[outer]:
            result[outer].append(condition["type_id"])
    return result


@flask_app.route("/save_aup", methods=["POST"])
@auth.oidc_auth("default")
def save_aup():
    result = _get_admin()
    if not isinstance(result, Admin):
        return Response(
            json.dumps(
                {
                    "error": "unauthorized",
                    "error_description": "you do not have rights to update this AUP",
                }
            ),
            403,
        )
    body = request.get_json()
    aup = Aup(
        body["name"],
        body["content"],
        markdown(body["content"]),
        gui_conditions_to_type_id(body["conditions"]),
        body.get("entitlement"),
        additional_data=body.get("additional_data"),
    )
    if DATABASE.insert_aup(aup):
        return Response(json.dumps({"redirect_url": url_for("aup_overview")}), 200)
    return Response(json.dumps({"status": "error occurred"}), 500)


@flask_app.route("/update_aup_name", methods=["POST"])
@auth.oidc_auth("default")
def update_aup_name():
    result = _get_admin()
    if not isinstance(result, Admin):
        return Response(
            json.dumps(
                {
                    "error": "unauthorized",
                    "error_description": "you do not have rights to update this AUP",
                }
            ),
            403,
        )
    body = request.get_json()
    DATABASE.set_aup_name(body["_id"], body["new_name"])
    return Response(json.dumps({"status": "ok"}), 200)


@flask_app.route("/update_aup_content", methods=["POST"])
@auth.oidc_auth("default")
def update_aup_content():
    result = _get_admin()
    if not isinstance(result, Admin):
        return Response(
            json.dumps(
                {
                    "error": "unauthorized",
                    "error_description": "you do not have rights to update this AUP",
                }
            ),
            403,
        )
    body = request.get_json()
    inserted_id = DATABASE.update_aup_text(
        body["_id"], body["content"], markdown(body["content"])
    )
    aup = DATABASE.get_aup_by_id(str(inserted_id))
    if aup:
        return Response(json.dumps(aup.to_dict()), 200)
    return Response(json.dumps({"status": "error occurred"}), 500)


@flask_app.route("/update_aup_conditions", methods=["POST"])
@auth.oidc_auth("default")
def update_aup_conditions():
    result = _get_admin()
    if not isinstance(result, Admin):
        return Response(
            json.dumps(
                {
                    "error": "unauthorized",
                    "error_description": "you do not have rights to update this AUP",
                }
            ),
            403,
        )
    body = request.get_json()
    DATABASE.set_aup_conditions(
        body["_id"], gui_conditions_to_type_id(body["conditions"])
    )
    return Response(json.dumps({"status": "ok"}), 200)


@flask_app.route("/delete_aup", methods=["POST"])
@auth.oidc_auth("default")
def delete_aup():
    result = _get_admin()
    if not isinstance(result, Admin):
        return Response(
            json.dumps(
                {
                    "error": "unauthorized",
                    "error_description": "you do not have rights to update this AUP",
                }
            ),
            403,
        )
    body = request.get_json()
    new_acutal_aup_id = DATABASE.delete_aup_by_id(body["_id"])
    return Response(json.dumps({"new_actual_aup_id": str(new_acutal_aup_id)}), 200)


@flask_app.route("/aup_overview")
@auth.oidc_auth("default")
def aup_overview():
    aups = DATABASE.get_all_aups()
    result = _get_admin()
    if not isinstance(result, Admin):
        return result
    admin = result
    return render_template("aup_overview.html", aups=aups, login=admin.ext_login)


@flask_app.route("/create_aup")
@auth.oidc_auth("default")
def create_aup():
    result = _get_admin()
    if not isinstance(result, Admin):
        return result
    admin = result
    entities = CONNECTOR.get_entities_for_admin(admin.get_id())
    entities_as_dict = {}
    for key, value in entities.items():
        new_value = []
        for entity in value:
            new_value.append(entity.__dict__)
        entities_as_dict[key] = new_value

    return render_template(
        "create_aup.html",
        entities=entities_as_dict,
        entity_types=list(entities.keys()),
    )


def find_entity_in_admin_entities_dict(type_id, entities_dict):
    ent_type, ent_id = type_id.split(":", 1)
    entity_list = entities_dict.get(ent_type)
    if not entity_list:
        return None
    for entity in entity_list:
        if entity.type_id == type_id:
            return entity
    return None


@flask_app.route("/manage_aups")
@auth.oidc_auth("default")
def manage_aups():
    result = _get_admin()
    if not isinstance(result, Admin):
        return result
    admin = result
    admin_entities = CONNECTOR.get_entities_for_admin(admin.get_id())

    entities_as_dict = {}
    for key, value in admin_entities.items():
        new_value = []
        for entity in value:
            entity_as_dict = entity.__dict__
            entity_as_dict["type"] = entity.get_entity_type()
            new_value.append(entity_as_dict)
        entities_as_dict[key] = new_value

    aups_dict = {"enabled": [], "disabled": []}
    all_aups = DATABASE.get_all_aups()
    for aup in all_aups:
        aup_as_dict = aup.to_dict()
        enabled = True
        for outer_ind in range(len(aup.conditions)):
            if not enabled:
                break
            for inner_ind in range(len(aup.conditions[outer_ind])):
                entity = find_entity_in_admin_entities_dict(
                    aup.conditions[outer_ind][inner_ind], admin_entities
                )
                if entity:
                    entity_as_dict = entity.__dict__
                    entity_as_dict["type"] = entity.get_entity_type()
                    aup_as_dict["conditions"][outer_ind][inner_ind] = entity_as_dict
                else:
                    enabled = False
                    aups_dict["disabled"].append(aup.to_dict())
                    break
        if enabled:
            aups_dict["enabled"].append(aup_as_dict)
    return render_template(
        "manage_aups.html",
        aups_dict=aups_dict,
        entities=entities_as_dict,
        entity_types=list(admin_entities.keys()),
    )


def _get_admin():
    sub = UserSession(session).userinfo["sub"]
    admin = session.get("admin")
    if admin:
        admin = Admin(**json.loads(admin))
    if not admin or admin.ext_login != sub:
        admin = CONNECTOR.get_admin(sub, EXT_SRC_NAME)
        if not admin:
            return render_template("unauthorized.html", login=sub)
        session["admin"] = admin.to_json()
    return admin


if __name__ == "__main__":
    auth.init_app(flask_app.app)
    flask_app.add_api(
        "openapi-specification.yaml",
        strict_validation=True,
        validate_responses=True,
        arguments={"authorizationUrl": AUTHORIZATION_URL, "tokenUrl": TOKEN_URL},
        options={
            "swagger_ui": True,
            "swagger_path": swagger_ui_3_path,
            "swagger_ui_config": {
                "oauth2RedirectUrl": f"{cfg['hostname']}/ui/oauth2-redirect.html",
                "persistAuthorization": True,
            },
        },
    )
    flask_app.add_error_handler(Exception, exception_handler)
    flask_app.run(port=8080)
