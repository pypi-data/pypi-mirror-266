import json
from odoo.addons.base_rest import restapi
from werkzeug.exceptions import BadRequest, NotFound
from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component
from odoo.addons.base_rest_base_structure.models.api_services_utils import (
    APIServicesUtils,
)
from odoo.tools.translate import _
from odoo.http import Response


class CmMapService(Component):
    _inherit = "base.rest.private_abstract_service"
    _name = "cm.map.service"
    _usage = "maps"
    _description = """
      Map Service
  """

    @restapi.method(
        [(["/<string:slug>/config"], "GET")],
        auth="api_key",
    )
    def config(self, _slug):
        record = self.env["cm.map"].search([("slug_id", "=", _slug)])
        if record:
            try:
                record.ensure_one()
            except (Exception):
                return Response(
                    json.dumps(
                        {"message": _(
                            "More than one map found for %s") % _slug}
                    ),
                    status=404,
                    content_type="application/json",
                )
            return record.get_config_datamodel_dict()
        else:
            return Response(
                json.dumps({"message": _("No map record for id %s") % _slug}),
                status=404,
                content_type="application/json",
            )
        return False

    @restapi.method(
        [(["/<string:_map_slug>/places"], "GET")],
        auth="api_key"
    )
    def places(self, _map_slug):
        record = self.env["cm.map"].search([("slug_id", "=", _map_slug)])
        if record:
            try:
                record.ensure_one()
            except (Exception):
                return Response(
                    json.dumps(
                        {"message": _(
                            "More than one map found for %s") % _map_slug}
                    ),
                    status=404,
                    content_type="application/json",
                )
            return record.get_places_datamodel_dict()
        else:
            return Response(
                json.dumps(
                    {"message": _("No map record for id %s") % _map_slug}),
                status=404,
                content_type="application/json",
            )
        return False

    @restapi.method(
        [(["/<string:_map_slug>/places/<string:_place_slug>"], "GET")],
        auth="api_key"
    )
    def places_single(self, _map_slug, _place_slug=None):
        record = self.env["cm.map"].search([("slug_id", "=", _map_slug)])
        if record:
            try:
                record.ensure_one()
            except (Exception):
                return Response(
                    json.dumps(
                        {"message": _(
                            "More than one map found for %s") % _map_slug}
                    ),
                    status=404,
                    content_type="application/json",
                )
            if _place_slug:
                place_record = self.env["cm.place"].search(
                    [
                        ("slug_id", "=", _place_slug),
                        ("type", "=", "place"),
                        ("status", "=", "published"),
                    ]
                )
                if place_record:
                    try:
                        place_record.ensure_one()
                    except (Exception):
                        return Response(
                            json.dumps(
                                {
                                    "message": _(
                                        "More than one place found for %s"
                                    ) % _place_slug
                                }
                            ),
                            status=404,
                            content_type="application/json",
                        )
                    return place_record.get_datamodel_dict(single_view=True)
                else:
                    place_child_record = self.env["cm.place.child"].search(
                        [
                            ("slug_id", "=", _place_slug)
                        ]
                    )
                    # import ipdb; ipdb.set_trace()
                    if place_child_record:
                        try:
                            place_child_record.ensure_one()
                        except (Exception):
                            return Response(
                                json.dumps(
                                    {
                                        "message": _(
                                            "More than one child place found for %s"
                                        ) % _place_slug
                                    }
                                ),
                                status=404,
                                content_type="application/json",
                            )
                        return place_child_record.parent_place_id.get_datamodel_dict(
                            single_view=True,
                            child=place_child_record
                        )
                    return Response(
                        json.dumps(
                            {"message": _("No place record for id %s") %
                             _place_slug}
                        ),
                        status=404,
                        content_type="application/json",
                    )
            else:
                return Response(
                    json.dumps(
                        {"message": _("No place record for id %s") %
                            _place_slug}
                    ),
                    status=404,
                    content_type="application/json",
                )

        else:
            return Response(
                json.dumps(
                    {"message": _("No map record for id %s") % _map_slug}),
                status=404,
                content_type="application/json",
            )
        return False
