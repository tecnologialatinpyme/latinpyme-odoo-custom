# -*- coding: utf-8 -*-

import re
from urllib.parse import unquote, urljoin, urlsplit

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


REVISTA_BLOG_NAME = "Revista LatinPyme"
HTTP_TIMEOUT = (5, 15)
BLOCKED_OLD_PATH_PREFIXES = (
    "/shop",
    "/tienda",
    "/cart",
    "/checkout",
    "/payment",
    "/product",
    "/productos",
    "/store",
    "/blog",
    "/revista",
    "/web",
    "/my",
)
PRIORITY_SEQUENCE = {
    "high": 10,
    "medium": 50,
    "low": 90,
}


class LatinpymeRevistaSeoRedirect(models.Model):
    _name = "latinpyme.revista.seo.redirect"
    _description = "Redireccion SEO de nota Revista LatinPyme"
    _order = "priority_sequence, post_title, id"
    _rec_name = "post_title"

    post_id = fields.Many2one(
        "blog.post",
        string="Nota Odoo",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("blog_id.name", "=", REVISTA_BLOG_NAME)],
    )
    post_title = fields.Char(
        string="Titulo de nota",
        related="post_id.name",
        store=True,
        readonly=True,
    )
    new_path = fields.Char(
        string="URL nueva Odoo",
        compute="_compute_new_urls",
        readonly=True,
    )
    new_url = fields.Char(
        string="URL nueva completa",
        compute="_compute_new_urls",
        readonly=True,
    )
    old_url = fields.Char(
        string="URL antigua WordPress",
        help="Acepta una URL completa de LatinPyme o un path, por ejemplo /nota-antigua/.",
    )
    old_path = fields.Char(
        string="Path antiguo normalizado",
        compute="_compute_old_path",
        store=True,
        readonly=True,
        index=True,
    )
    website_id = fields.Many2one(
        "website",
        string="Sitio web",
        required=True,
        default=lambda self: self._default_website_id(),
        ondelete="cascade",
        index=True,
    )
    rewrite_id = fields.Many2one(
        "website.rewrite",
        string="Redireccion nativa Odoo",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    redirect_active = fields.Boolean(
        string="Redireccion activa",
        related="rewrite_id.active",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Pendiente"),
            ("active", "Redireccion creada"),
            ("validated", "Validada correctamente"),
            ("error", "Error"),
            ("disabled", "Desactivada"),
        ],
        string="Estado",
        default="draft",
        required=True,
        index=True,
        copy=False,
    )
    validation_status = fields.Selection(
        [
            ("pending", "Pendiente"),
            ("ok", "301 OK"),
            ("warning", "Advertencia"),
            ("error", "Error"),
        ],
        string="Validacion",
        default="pending",
        required=True,
        index=True,
        copy=False,
    )
    old_http_code = fields.Integer(string="HTTP URL antigua", readonly=True, copy=False)
    new_http_code = fields.Integer(string="HTTP URL nueva", readonly=True, copy=False)
    last_validation = fields.Datetime(string="Ultima validacion", readonly=True, copy=False)
    validation_message = fields.Text(string="Mensaje de validacion", readonly=True, copy=False)
    priority = fields.Selection(
        [
            ("high", "Alta"),
            ("medium", "Media"),
            ("low", "Baja"),
        ],
        string="Prioridad",
        default="medium",
        required=True,
        index=True,
    )
    priority_sequence = fields.Integer(
        compute="_compute_priority_sequence",
        store=True,
    )
    search_console_clicks = fields.Integer(string="Clics Search Console")
    search_console_impressions = fields.Integer(string="Impresiones Search Console")
    notes = fields.Text(string="Observaciones")

    _sql_constraints = [
        (
            "post_unique",
            "unique(post_id)",
            "Cada nota Odoo solo puede tener una fila en la matriz de redirecciones.",
        ),
        (
            "old_path_website_unique",
            "unique(old_path, website_id)",
            "Ya existe una redireccion con ese path antiguo para este sitio web.",
        ),
    ]

    @api.model
    def _default_website_id(self):
        website = self._revista_website()
        return website.id if website else False

    @api.model
    def _revista_website(self):
        Config = self.env["latinpyme.revista.config"].sudo()
        config = Config.get_primary_config()
        if config and config.website_id:
            return config.website_id
        Website = self.env["website"].sudo()
        website = Website.browse()
        for candidate in Website.search([("domain", "!=", False)], order="id"):
            if Config._domain_to_host(candidate.domain) in ("latinpyme.com", "www.latinpyme.com"):
                website = candidate
                break
        return website or Website.search([("name", "ilike", "Revista")], limit=1)

    @api.model
    def _production_base_url(self, website=None):
        Config = self.env["latinpyme.revista.config"].sudo()
        config = Config.get_active_config(website) if website else Config.get_primary_config()
        if config:
            return config.production_base_url()
        return "https://latinpyme.com"

    @api.depends("post_id", "post_id.website_url", "website_id")
    def _compute_new_urls(self):
        for record in self:
            new_path = record._normalize_destination_path(record.post_id.website_url if record.post_id else "")
            record.new_path = new_path
            record.new_url = "%s%s" % (record._production_base_url(record.website_id), new_path) if new_path else False

    @api.depends("old_url")
    def _compute_old_path(self):
        for record in self:
            record.old_path = record._normalize_old_path(record.old_url)

    @api.depends("priority")
    def _compute_priority_sequence(self):
        for record in self:
            record.priority_sequence = PRIORITY_SEQUENCE.get(record.priority, 50)

    @api.model
    def _normalize_old_path(self, value):
        value = (value or "").strip()
        if not value:
            return False
        parsed = urlsplit(value if "://" in value or value.startswith("//") else "/%s" % value.lstrip("/"))
        path = unquote(parsed.path or "/")
        path = re.sub(r"/{2,}", "/", path)
        path = "/%s" % path.lstrip("/")
        if path != "/" and not path.endswith("/"):
            path += "/"
        return path

    @api.model
    def _normalize_destination_path(self, value):
        value = (value or "").strip()
        if not value:
            return False
        parsed = urlsplit(value if "://" in value or value.startswith("//") else "/%s" % value.lstrip("/"))
        path = re.sub(r"/{2,}", "/", parsed.path or "/")
        return "/%s" % path.lstrip("/")

    @api.model
    def normalize_request_path(self, value):
        return self._normalize_old_path(value)

    @api.constrains("old_url")
    def _check_old_url_host(self):
        for record in self:
            value = (record.old_url or "").strip()
            if not value or "://" not in value:
                continue
            host = (urlsplit(value).hostname or "").lower()
            allowed_hosts = {
                "latinpyme.com",
                "www.latinpyme.com",
                "portalold.latinpyme.com",
            }
            if host not in allowed_hosts:
                raise ValidationError(
                    "La URL antigua debe pertenecer a latinpyme.com o portalold.latinpyme.com."
                )

    def write(self, vals):
        critical_fields = {"post_id", "old_url", "website_id"}
        if critical_fields.intersection(vals) and not self.env.context.get("lp_seo_redirect_internal"):
            if any(record.redirect_active for record in self):
                raise ValidationError(
                    "Desactiva la redireccion antes de cambiar la nota, la URL antigua o el sitio web."
                )
            vals = dict(
                vals,
                state="draft",
                validation_status="pending",
                old_http_code=0,
                new_http_code=0,
                last_validation=False,
                validation_message=False,
            )
        result = super().write(vals)
        if "priority" in vals:
            for record in self.filtered("rewrite_id"):
                record.rewrite_id.sudo().write({
                    "sequence": PRIORITY_SEQUENCE.get(record.priority, 50),
                })
        return result

    def unlink(self):
        rewrites = self.mapped("rewrite_id").filtered("active")
        if rewrites:
            rewrites.write({"active": False})
        return super().unlink()

    def _validate_activation_data(self):
        self.ensure_one()
        if not self.old_path:
            raise UserError("Ingresa la URL antigua de WordPress antes de activar la redireccion.")
        if self.old_path == "/":
            raise UserError("No se permite redirigir la home.")
        if "\\" in self.old_path or any(part in (".", "..") for part in self.old_path.split("/")):
            raise UserError("El path antiguo contiene segmentos no permitidos.")
        lower_path = self.old_path.lower().rstrip("/")
        if any(lower_path == prefix or lower_path.startswith("%s/" % prefix) for prefix in BLOCKED_OLD_PATH_PREFIXES):
            raise UserError("La URL antigua pertenece a Tienda, ecommerce o una ruta tecnica fuera de alcance.")
        if not self.new_path or not self.new_path.startswith("/blog/"):
            raise UserError("La nota seleccionada no tiene una URL individual valida de Odoo Blog.")
        if self.new_path.rstrip("/") == self.old_path.rstrip("/"):
            raise UserError("La URL antigua no puede coincidir con la URL nueva.")
        if self.new_path.rstrip("/") == "":
            raise UserError("La redireccion no puede apuntar a la home.")
        if self.post_id.blog_id.name != REVISTA_BLOG_NAME:
            raise UserError("La nota seleccionada no pertenece al blog Revista LatinPyme.")
        if (
            "website_id" in self.post_id.blog_id._fields
            and self.post_id.blog_id.website_id
            and self.post_id.blog_id.website_id != self.website_id
        ):
            raise UserError("El blog de la nota no pertenece al sitio web de Revista.")
        if not self._post_is_public():
            raise UserError("La nota nueva debe estar publicada, vigente y asignada al sitio web de Revista.")

    def _post_is_public(self):
        self.ensure_one()
        post = self.post_id.sudo()
        if not post:
            return False
        if "active" in post._fields and not post.active:
            return False
        if "website_published" in post._fields and not post.website_published:
            return False
        if "is_published" in post._fields and not post.is_published:
            return False
        if "post_date" in post._fields and post.post_date and post.post_date > fields.Datetime.now():
            return False
        if "website_id" in post._fields and post.website_id and post.website_id != self.website_id:
            return False
        return True

    def _rewrite_candidates(self):
        self.ensure_one()
        variants = list({self.old_path, self.old_path.rstrip("/")})
        return self.env["website.rewrite"].sudo().search([
            ("url_from", "in", variants),
            ("redirect_type", "in", ("301", "302", "308", "404")),
            ("website_id", "in", [False, self.website_id.id]),
        ])

    def _rewrite_is_consistent(self):
        self.ensure_one()
        rewrite = self.rewrite_id.sudo().exists()
        if (
            not rewrite
            or not rewrite.active
            or rewrite.redirect_type != "301"
            or rewrite.website_id != self.website_id
        ):
            return False
        return (
            self._normalize_old_path(rewrite.url_from) == self.old_path
            and self._normalize_destination_path(rewrite.url_to) == self.new_path
        )

    def _activate_one(self):
        self.ensure_one()
        self._validate_activation_data()
        owned_rewrite = self.rewrite_id.sudo().exists()
        conflicts = self._rewrite_candidates() - owned_rewrite
        if conflicts:
            reusable = conflicts.filtered(
                lambda rewrite: rewrite.website_id == self.website_id
                and rewrite.redirect_type == "301"
                and rewrite.url_to.rstrip("/") == self.new_path.rstrip("/")
            )
            if len(reusable) == 1 and len(conflicts) == 1:
                owned_rewrite = reusable
            else:
                conflict = conflicts[:1]
                raise UserError(
                    "Ya existe una redireccion para %s hacia %s."
                    % (conflict.url_from, conflict.url_to or "sin destino")
                )

        rewrite_values = {
            "name": "WordPress a Odoo | %s" % self.post_title,
            "website_id": self.website_id.id,
            "url_from": self.old_path,
            "url_to": self.new_path,
            "redirect_type": "301",
            "active": True,
            "sequence": PRIORITY_SEQUENCE.get(self.priority, 50),
        }
        if owned_rewrite:
            owned_rewrite.write(rewrite_values)
        else:
            owned_rewrite = self.env["website.rewrite"].sudo().create(rewrite_values)
        self.with_context(lp_seo_redirect_internal=True).write({
            "rewrite_id": owned_rewrite.id,
            "state": "active",
            "validation_status": "pending",
            "old_http_code": 0,
            "new_http_code": 0,
            "last_validation": False,
            "validation_message": "Redireccion 301 creada. Ejecuta la validacion despues de guardar.",
        })

    def action_activate_301(self):
        success_count = 0
        error_messages = []
        for record in self:
            try:
                with self.env.cr.savepoint():
                    record._activate_one()
                success_count += 1
            except (UserError, ValidationError) as error:
                message = str(error)
                record.with_context(lp_seo_redirect_internal=True).write({
                    "state": "error",
                    "validation_status": "error",
                    "validation_message": message,
                })
                error_messages.append("%s: %s" % (record.post_title, message))
        return self._batch_notification(
            "Activacion de redirecciones",
            success_count,
            error_messages,
        )

    def action_disable_redirect(self):
        disabled_count = 0
        for record in self:
            if record.rewrite_id:
                record.rewrite_id.sudo().write({"active": False})
            record.with_context(lp_seo_redirect_internal=True).write({
                "state": "disabled",
                "validation_status": "pending",
                "validation_message": "Redireccion desactivada.",
            })
            disabled_count += 1
        return self._notification(
            "Redirecciones desactivadas",
            "%s redirecciones fueron desactivadas." % disabled_count,
            "success",
        )

    def _http_get(self, url):
        return requests.get(
            url,
            allow_redirects=False,
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": "LatinPyme-SEO-Redirect-Validator/1.0"},
        )

    def _normalized_absolute_url(self, url):
        parsed = urlsplit(url)
        path = unquote(parsed.path or "/").rstrip("/") or "/"
        return (
            parsed.scheme.lower(),
            (parsed.hostname or "").lower(),
            path,
            parsed.query,
        )

    def _response_is_noindex(self, response):
        if "noindex" in (response.headers.get("X-Robots-Tag") or "").lower():
            return True
        html = (response.text or "")[:300000]
        for meta_tag in re.findall(r"<meta\b[^>]*>", html, flags=re.IGNORECASE):
            lower_tag = meta_tag.lower()
            if "robots" in lower_tag and "noindex" in lower_tag:
                return True
        return False

    def _validate_one(self):
        self.ensure_one()
        self._validate_activation_data()
        if not self.rewrite_id or not self.rewrite_id.active:
            raise UserError("La redireccion 301 no esta activa.")

        old_url = "%s%s" % (self._production_base_url(self.website_id), self.old_path)
        expected_url = self.new_url
        old_response = self._http_get(old_url)
        new_response = self._http_get(expected_url)
        values = {
            "old_http_code": old_response.status_code,
            "new_http_code": new_response.status_code,
            "last_validation": fields.Datetime.now(),
        }

        if old_response.status_code == 404:
            return values, "error", "La URL antigua devuelve 404 y no esta redirigiendo."
        if old_response.status_code == 200:
            return values, "warning", "La URL antigua devuelve 200; existe contenido en vez de una redireccion."
        if old_response.status_code != 301:
            return values, "error", "La URL antigua devuelve HTTP %s; se esperaba 301." % old_response.status_code

        location = old_response.headers.get("Location")
        if not location:
            return values, "error", "La respuesta 301 no incluye cabecera Location."
        destination_url = urljoin(old_url, location)
        if self._normalized_absolute_url(destination_url) != self._normalized_absolute_url(expected_url):
            return values, "error", "La URL antigua redirige a %s y no a la nota esperada." % destination_url
        if new_response.status_code != 200:
            return values, "error", "La URL nueva devuelve HTTP %s; se esperaba 200." % new_response.status_code
        if self._response_is_noindex(new_response):
            return values, "error", "La nota nueva responde 200 pero contiene una directiva noindex."
        return values, "ok", "301 OK: destino exacto, sin cadena y nota nueva HTTP 200."

    def action_validate_redirect(self):
        success_count = 0
        error_messages = []
        warning_count = 0
        for record in self:
            try:
                values, result, message = record._validate_one()
            except (requests.RequestException, UserError, ValidationError) as error:
                values = {
                    "old_http_code": 0,
                    "new_http_code": 0,
                    "last_validation": fields.Datetime.now(),
                }
                result = "error"
                message = "No fue posible validar: %s" % error

            if result == "ok":
                values.update({
                    "state": "validated",
                    "validation_status": "ok",
                    "validation_message": message,
                })
                success_count += 1
            else:
                values.update({
                    "state": "error",
                    "validation_status": result,
                    "validation_message": message,
                })
                if result == "warning":
                    warning_count += 1
                error_messages.append("%s: %s" % (record.post_title, message))
            record.with_context(lp_seo_redirect_internal=True).write(values)

        title = "Validacion de redirecciones"
        message = "%s redirecciones validadas correctamente." % success_count
        if warning_count:
            message += " %s con advertencia." % warning_count
        if error_messages:
            message += " %s con error. Revisa el mensaje de cada fila." % (len(error_messages) - warning_count)
        return self._notification(title, message, "warning" if error_messages else "success")

    @api.model
    def action_sync_posts(self):
        website = self._revista_website()
        if not website:
            raise UserError("No se encontro el sitio web configurado para Revista LatinPyme.")
        Blog = self.env["blog.blog"].sudo()
        blog_domain = [("name", "=", REVISTA_BLOG_NAME)]
        if "website_id" in Blog._fields:
            blog_domain.append(("website_id", "in", [False, website.id]))
        blogs = Blog.search(blog_domain)
        if not blogs:
            raise UserError("No se encontro el blog Revista LatinPyme.")

        Post = self.env["blog.post"].sudo()
        post_domain = [("blog_id", "in", blogs.ids)]
        if "active" in Post._fields:
            post_domain.append(("active", "=", True))
        if "website_published" in Post._fields:
            post_domain.append(("website_published", "=", True))
        elif "is_published" in Post._fields:
            post_domain.append(("is_published", "=", True))
        if "post_date" in Post._fields:
            post_domain.append(("post_date", "<=", fields.Datetime.now()))
        if "website_id" in Post._fields:
            post_domain.append(("website_id", "in", [False, website.id]))
        posts = Post.search(post_domain, order="post_date desc, id desc")
        existing_post_ids = set(self.sudo().search([("post_id", "in", posts.ids)]).mapped("post_id").ids)
        values_list = [
            {
                "post_id": post.id,
                "website_id": website.id,
                "state": "draft",
                "validation_status": "pending",
            }
            for post in posts
            if post.id not in existing_post_ids
        ]
        if values_list:
            self.sudo().create(values_list)
        return self._notification(
            "Sincronizacion completada",
            "%s notas publicadas agregadas. %s ya estaban registradas."
            % (len(values_list), len(posts) - len(values_list)),
            "success",
            reload_view=True,
        )

    @api.model
    def _notification(self, title, message, notification_type, reload_view=False):
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": notification_type,
                "sticky": notification_type in ("warning", "danger"),
            },
        }
        if reload_view:
            action["params"]["next"] = {"type": "ir.actions.client", "tag": "reload"}
        return action

    def _batch_notification(self, title, success_count, error_messages):
        message = "%s redirecciones activadas." % success_count
        if error_messages:
            message += " %s filas quedaron con error; revisa su mensaje de validacion." % len(error_messages)
        return self._notification(
            title,
            message,
            "warning" if error_messages else "success",
        )
