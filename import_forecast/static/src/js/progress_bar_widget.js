/** @odoo-module **/
import AbstractField from "web.AbstractField";
import fieldRegistry from "web.field_registry";
var ProgressBarWidget = AbstractField.extend({
    template: "ProgressBarWidget",
    start: function () {
        this._super.apply(this, arguments);
        if (this.recordData[this.nodeOptions.currentValue]) {
            this.value = this.recordData[this.nodeOptions.currentValue];
        }
    },
    _render: function () {
        var self = this;
        var value = this.value;
        var max_value = 100;
        value = value || 0;
        var widthComplete;
        if (value <= max_value) {
            widthComplete = parseInt((value / max_value) * 100);
        } else {
            widthComplete = 100;
        }
        this.$(".progress_number").text(widthComplete.toString() + "%");
        this.$(".progress-bar-inner").css("width", widthComplete + "%");
    },
});
fieldRegistry.add("progress_bar_widget", ProgressBarWidget);
