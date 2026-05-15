from odoo import http
from odoo.http import request

class Features(http.Controller):
    
    @http.route('/module/features', type="http", auth='public', website=True)
    def module_features(self):
        
        features = self.env['index.generator.feature'].sudo().search([])
        
        print("- --/n/n/n - -- -- - -- features ---------/n/n/n", features)
        
        return request.render('bsi_index_generator.features_listing_section', {'features': features})