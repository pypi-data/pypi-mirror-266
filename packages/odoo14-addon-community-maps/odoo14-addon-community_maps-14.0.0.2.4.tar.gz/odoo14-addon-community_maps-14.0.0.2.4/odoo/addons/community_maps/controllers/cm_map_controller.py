
from odoo.addons.base_rest.controllers import main
from odoo.http import route


class CmMapController(main.RestController):
    _root_path = "/api/private/maps/"
    _collection_name = "community_maps.services"
    _default_auth = "api_key"

    @route(
        [
            _root_path + "forms",
        ],
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def forms(self, **params):
        return self._process_method("forms", "submit", params)
