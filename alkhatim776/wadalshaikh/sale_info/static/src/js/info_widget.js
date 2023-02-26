odoo.define('sale_info.partner_info',function(require) {
    'use strict';

   
    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');
    const field_utils = require('web.field_utils');
    const utils = require('web.utils');
    const core = require('web.core');
    const QWeb = core.qweb;
    const _t = core._t;

    
    const partner_info = AbstractField.extend({
        supportedFieldTypes: ['char'],
    
        _render: function () {
            var data = 0
            var self = this;
          
            this.$el.html(QWeb.render('partner_info.partner_info', this.value));
            $('[data-toggle="tooltip"]').popover('dispose');

            this.$('.o_partner_info_button').on('click', self._show_info.bind(self));
            
        },
    
        isSet: function () {
            return true;
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * Opens the Forecast Report for the `stock.move` product.
         *
         * @param {MouseEvent} ev
         */
        _show_info: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            console.log('????????????')
            var self = this;
          
            this._rpc({
                model: 'sale.order.line',
                method: 'show_info',
                args: [this.recordData.id],
            }).then(function(data) {
               
                var isRTL = _t.database.parameters.direction === "rtl";
                var content = data;
                
                
                var options = {
                    
                    content: function () {
                        var $content = $(QWeb.render('partner_info.PaymentPopOver', data));
                            return $content;
                    },
                    html: true,
                    placement: isRTL ? 'bottom' : 'left',
                        title: ' تفاصيل المنتج:',
                        // trigger: '',
                        delay: {'show': 0, 'hide': 100},
                   
                };
                console.log("******************",data);
    
                $('[data-toggle="tooltip"]').popover(options);
            });
        },
    });
    
    const JsonWidget = AbstractField.extend({
        supportedFieldTypes: ['char'],
    
        _render: function () {
            var value = JSON.parse(this.value);
            if (!value || !value.template) {
                this.$el.html('');
                return;
            }
            $(QWeb.render(value.template, value)).appendTo(this.$el);
        },
    });
    
    fieldRegistry.add('partner_info', partner_info);
    fieldRegistry.add('json_widget', JsonWidget);
    
    return partner_info;
    });
    