odoo.define('project_labor_planning.project_labor_planning', function (require) {
'use strict';

var core = require('web.core');
var session = require('web.session');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var SearchView = require('web.SearchView');
var data = require('web.data');
var pyUtils = require('web.py_utils');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var project_labor_planning = AbstractAction.extend(ControlPanelMixin, {
    custom_events: {
        search: '_onSearch',
    },
    events:{
        'change .o_plp_save_input_text': 'plp_allocation_save',
//        'change .o_plp_save_not_attended_text': 'plp_not_not_attended_save',
        'click .o_plp_project_name': 'open_plp_project',
    },
    init: function(parent, action) {
        this.actionManager = parent;
        this.action = action;
        this.domain = [];
        return this._super.apply(this, arguments);
    },
    render_search_view: function(){
        var self = this;
        var defs = [];
        return this._rpc({
                model: 'ir.model.data',
                method: 'get_object_reference',
                args: ['project', 'view_project_project_filter'],
                kwargs: {context: session.user_context},
            })
            .then(function(view_id){
                self.dataset = new data.DataSetSearch(this, 'project.project');
                return self.loadFieldView(self.dataset, view_id[1], 'search')
                .then(function (fields_view) {
                    self.fields_view = fields_view;
                    var options = {
                        $buttons: $("<div>"),
                        action: this.action,
                        disable_groupby: true,
                    };
                    self.searchview = new SearchView(self, self.dataset, self.fields_view, options);
                    return self.searchview.appendTo($("<div>")).then(function () {
                        defs.push(self.update_cp());
                        self.$searchview_buttons = self.searchview.$buttons.contents();
                    });
                });
            });
    },
    willStart: function() {
        return this.get_html();
    },
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return self.render_search_view().then(function () {
                self.$el.html(self.html);
            });
        });
    },
    re_renderElement: function() {
        var self = this;
        this.$el.html(this.html);
    },
    option_plp_period: function(e){
        var self = this;
        this.period = $(e.target).data('value');
        return this._rpc({
                model: 'project.labor.planning',
                method: 'search',
                args: [[]],
                kwargs: {context: session.user_context},
            })
            .then(function(res){
                return self._rpc({
                        model: 'project.labor.planning',
                        method: 'write',
                        args: [res, {'period': self.period}],
                        kwargs: {context: session.user_context},
                    })
                    .done(function(result){
                        self.get_html().then(function() {
                            self.update_cp();
                            self.re_renderElement();
                        });
                    });
        });
    },
    option_plp_project_type: function(e){
        var self = this;
        this.project_type = $(e.target).data('value');
        return this._rpc({
                model: 'project.labor.planning',
                method: 'search',
                args: [[]],
                kwargs: {context: session.user_context},
            })
            .then(function(res){
                return self._rpc({
                        model: 'project.labor.planning',
                        method: 'write',
                        args: [res, {'project_type': self.project_type}],
                        kwargs: {context: session.user_context},
                    })
                    .done(function(result){
                        self.get_html().then(function() {
                            self.update_cp();
                            self.re_renderElement();
                        });
                    });
        });
    },
    open_plp_project: function(e){
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: "project.project",
            res_id: parseInt($(e.target).data('project')),
            views: [[false, 'form']],
        });
    },
    plp_allocation_save: function(e){
        var self = this;
        var $input = $(e.target);
        var target_value;
        try {
            target_value = field_utils.parse.float($input.val().replace(String.fromCharCode(8209), '-'));
        } catch(err) {
            return this.do_warn(_t("Wrong value entered!"), err);
        }
        return this._rpc({
            model: 'project.allocation',
            method: 'save_allocation_data',
            args: [parseInt($input.data('project')),$input.data('project_type'), target_value, $input.data('date'), $input.data('date_to'), $input.data('name')],
            kwargs: {context: session.user_context},
        })
        .done(function(res){
            self.get_html().then(function() {
                self.re_renderElement();
            });
        });
    },
//    plp_not_not_attended_save: function(e){
//        var self = this;
//        var $input = $(e.target);
//        var target_value;
//        try {
//            target_value = field_utils.parse.float($input.val().replace(String.fromCharCode(8209), '-'));
//        } catch(err) {
//            return this.do_warn(_t("Wrong value entered!"), err);
//        }
//        return this._rpc({
//            model: 'not.attended.staff',
//            method: 'save_not_attended_data',
//            args: [$input.data('project_type'), target_value, $input.data('date'), $input.data('date_to'), $input.data('name')],
//            kwargs: {context: session.user_context},
//        })
//        .done(function(res){
//            self.get_html().then(function() {
//                self.re_renderElement();
//            });
//        });
//    },
    // Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        return this._rpc({
                model: 'project.labor.planning',
                method: 'get_html',
                args: [this.domain],
                kwargs: {context: session.user_context},
            })
            .then(function (result) {
                self.html = result.html;
                self.report_context = result.report_context;
            });
    },
    // Updates the control panel and render the elements that have yet to be rendered
    update_cp: function() {
        var self = this;
        this.$searchview_buttons = $(QWeb.render("PLP.optionButton", {period: self.report_context.period,project_type: self.report_context.project_type}));
        this.$searchview_buttons.siblings('.o_plp_period_filter');
        this.$searchview_buttons.siblings('.o_plp_project_type_filter');
        this.$searchview_buttons.find('.o_plp_option_plp_period').bind('click', function (event) {
            self.option_plp_period(event);
        });
        this.$searchview_buttons.find('.o_plp_option_plp_project_type').bind('click', function (event) {
            self.option_plp_project_type(event);
        });
        this.update_control_panel({
            cp_content: {
                $buttons: this.$buttons,
                $searchview: this.searchview.$el,
                $searchview_buttons: this.$searchview_buttons
            },
            searchview: this.searchview,
        });
    },
    do_show: function() {
        this._super();
        this.update_cp();
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {OdooEvent} event
     */
    _onSearch: function (event) {
        event.stopPropagation();
        var session = this.getSession();
        var result = pyUtils.eval_domains_and_contexts({
            contexts: [session.user_context],
            domains: event.data.domains
        });
        this.domain = result.domain;
        this.get_html().then(this.re_renderElement.bind(this));
    },
});

core.action_registry.add("project_labor_planning", project_labor_planning);
return project_labor_planning;
});
