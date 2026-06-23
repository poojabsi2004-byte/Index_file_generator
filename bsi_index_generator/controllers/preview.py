import base64

from odoo import http
from odoo.http import request


class IndexGeneratorPreview(http.Controller):

    @http.route('/bsi_index_generator/preview/<int:generator_id>', type='http', auth='user')
    def index_generator_preview(self, generator_id):
        generator = request.env['index.file.generator'].browse(generator_id).exists()
        if not generator or not generator.generated_file:
            return request.not_found()

        html = base64.b64decode(generator.generated_file)
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
            ('X-Frame-Options', 'SAMEORIGIN'),
        ])
