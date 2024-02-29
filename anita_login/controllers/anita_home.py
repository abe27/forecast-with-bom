# -*- coding: utf-8 -*-

import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.home import Home, SIGN_UP_REQUEST_PARAMS
from odoo.addons.web.controllers.utils import ensure_db, is_user_internal
from odoo import http
from odoo.http import request

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

import os
import logging

_logger = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


class AdminHome(Home):
    '''
    inherit home to extend web.login style
    '''

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # so it is correct if overloaded with auth="public"
        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            try:
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        # add extra info to login page
        ir_config = request.env['ir.config_parameter'].sudo()
        login_style = ir_config.get_param(
            key='anita_theme_settting.login_style', default='login_style1')
        login_template = 'anita_login.{login_style}'.format(login_style=login_style)
        
        # add extra info to login page
        values['title'] = ir_config.get_param(
            "anita_theme_setting.window_default_title", "OpenErpNext")
        values['powered_by'] = ir_config.get_param("powered_by", "OpenErpNext")

        response = request.render(login_template, values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
