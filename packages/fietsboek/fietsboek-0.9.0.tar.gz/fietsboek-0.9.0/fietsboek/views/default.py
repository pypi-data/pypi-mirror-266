"""Home views."""

from markupsafe import Markup
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.interfaces import ISecurityPolicy
from pyramid.renderers import render_to_response
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import forget, remember
from pyramid.view import view_config
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased

from .. import actions, email, models, summaries, util
from ..models.track import TrackType, TrackWithMetadata
from ..models.user import TOKEN_LIFETIME, PasswordMismatch, TokenType


@view_config(route_name="home", renderer="fietsboek:templates/home.jinja2")
def home(request: Request) -> Response:
    """Renders the home page.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    if not request.identity:
        # See if the admin set a custom home page
        page = request.pages.find("/", request)
        if page is not None:
            return render_to_response(
                "fietsboek:templates/static-page.jinja2",
                {
                    "title": page.title,
                    "content": Markup(page.content),
                },
                request,
            )

        # Show the default home page
        locale = request.localizer.locale_name
        content = util.read_localized_resource(
            locale,
            "html/home.html",
            locale_packages=request.config.language_packs,
        )
        return {
            "home_content": content,
        }

    sorting = request.cookies.get("home_sorting", "asc")
    ascending = sorting == "asc"

    query = request.identity.all_tracks_query()
    query = select(aliased(models.Track, query)).where(query.c.type == TrackType.ORGANIC)
    summary = summaries.Summary(ascending=ascending)

    for track in request.dbsession.execute(query).scalars():
        if track.cache is None:
            gpx_data = request.data_manager.open(track.id).decompress_gpx()
            track.ensure_cache(gpx_data)
            request.dbsession.add(track.cache)
        summary.add(TrackWithMetadata(track, request.data_manager))

    unfinished_uploads = request.identity.uploads

    return {
        "summary": summary,
        "month_name": util.month_name,
        "unfinished_uploads": unfinished_uploads,
        "sorted_ascending": ascending,
    }


@view_config(route_name="static-page", renderer="fietsboek:templates/static-page.jinja2")
def static_page(request: Request) -> Response:
    """Renders a static page.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    page = request.pages.find(request.matchdict["slug"], request)
    if page is None:
        return HTTPNotFound()

    return {
        "title": page.title,
        "content": Markup(page.content),
    }


@view_config(route_name="login", renderer="fietsboek:templates/login.jinja2", request_method="GET")
def login(request: Request) -> Response:
    """Renders the login page.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    # pylint: disable=unused-argument
    return {}


@view_config(route_name="login", request_method="POST")
def do_login(request: Request) -> Response:
    """Endpoint for the login form.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    query = models.User.query_by_email(request.params["email"])
    try:
        user = request.dbsession.execute(query).scalar_one()
        user.check_password(request.params["password"])
    except (NoResultFound, PasswordMismatch):
        request.session.flash(request.localizer.translate(_("flash.invalid_credentials")))
        return HTTPFound(request.route_url("login"))

    if not user.is_verified:
        request.session.flash(request.localizer.translate(_("flash.account_not_verified")))
        return HTTPFound(request.route_url("login"))

    request.session.flash(request.localizer.translate(_("flash.logged_in")))
    user_id = user.authenticated_user_id()
    headers = remember(request, user_id)

    if request.params.get("remember-me") == "on":
        # We don't want this logic to be the default in
        # SecurityPolicy.remember, so we manually fake it here:
        policy = request.registry.getUtility(ISecurityPolicy)
        headers += policy.remember_cookie(request, user_id)

    response = HTTPFound("/", headers=headers)
    return response


@view_config(route_name="logout")
def logout(request: Request) -> Response:
    """Logs the user out.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    request.session.flash(request.localizer.translate(_("flash.logged_out")))
    headers = forget(request)
    return HTTPFound("/", headers=headers)


@view_config(
    route_name="password-reset",
    request_method="GET",
    renderer="fietsboek:templates/request_password.jinja2",
)
def password_reset(request: Request) -> Response:
    """Form to request a new password.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    # pylint: disable=unused-argument
    return {}


@view_config(route_name="password-reset", request_method="POST")
def do_password_reset(request: Request) -> Response:
    """Endpoint for the password request form.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    query = models.User.query_by_email(request.params["email"])
    user = request.dbsession.execute(query).scalar_one_or_none()
    if user is None:
        request.session.flash(request.localizer.translate(_("flash.reset_invalid_email")))
        return HTTPFound(request.route_url("password-reset"))

    token = models.Token.generate(user, TokenType.RESET_PASSWORD)
    request.dbsession.add(token)
    request.session.flash(request.localizer.translate(_("flash.password_token_generated")))

    mail = email.prepare_message(
        request.config.email_from,
        user.email,
        request.localizer.translate(_("page.password_reset.email.subject")),
    )
    mail.set_content(
        request.localizer.translate(_("page.password_reset.email.body")).format(
            request.route_url("use-token", uuid=token.uuid)
        )
    )
    email.send_message(
        request.config.email_smtp_url,
        request.config.email_username,
        request.config.email_password.get_secret_value(),
        mail,
    )

    return HTTPFound(request.route_url("password-reset"))


@view_config(
    route_name="resend-verification",
    request_method="GET",
    renderer="fietsboek:templates/resend_verification.jinja2",
)
def resend_verification(_request: Request) -> Response:
    """Form to request a new verification mail.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    return {}


@view_config(route_name="resend-verification", request_method="POST")
def do_resend_verification(request: Request) -> Response:
    """Endpoint for the verification resend form.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    query = models.User.query_by_email(request.params["email"])
    user = request.dbsession.execute(query).scalar_one_or_none()
    if user is None or user.is_verified:
        request.session.flash(
            request.localizer.translate(_("flash.resend_verification_email_fail"))
        )
        return HTTPFound(request.route_url("resend-verification"))

    actions.send_verification_token(request, user)
    request.session.flash(request.localizer.translate(_("flash.verification_token_generated")))

    return HTTPFound(request.route_url("login"))


@view_config(route_name="use-token")
def use_token(request: Request) -> Response:
    """Endpoint with which a user can use a token for a password reset or email
    verification.

    :param request: The Pyramid request.
    :return: The HTTP response.
    """
    token = request.dbsession.execute(
        select(models.Token).filter_by(uuid=request.matchdict["uuid"])
    ).scalar_one_or_none()
    if token is None:
        return HTTPNotFound()

    if token.age() > TOKEN_LIFETIME:
        request.session.flash(request.localizer.translate(_("flash.token_expired")))
        return HTTPFound(request.route_url("home"))

    if token.token_type == TokenType.VERIFY_EMAIL:
        token.user.is_verified = True
        request.dbsession.delete(token)
        request.session.flash(request.localizer.translate(_("flash.email_verified")))
        return HTTPFound(request.route_url("login"))
    if request.method == "GET" and token.token_type == TokenType.RESET_PASSWORD:
        return render_to_response("fietsboek:templates/password_reset.jinja2", {}, request)
    if request.method == "POST" and token.token_type == TokenType.RESET_PASSWORD:
        password = request.params["password"]
        try:
            util.check_password_constraints(password, request.params["repeat-password"])
        except ValueError as exc:
            request.session.flash(request.localizer.translate(exc.args[0]))
            return HTTPFound(request.route_url("use-token", uuid=token.uuid))

        token.user.set_password(password)
        request.dbsession.delete(token)
        request.session.flash(request.localizer.translate(_("flash.password_updated")))
        return HTTPFound(request.route_url("login"))
    raise NotImplementedError("No matching action found")
