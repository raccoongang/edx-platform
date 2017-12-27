define([
    'js/views/baseview',
    'underscore',
    'text!templates/settings-intro-video-azure.underscore'
], function(BaseView, _, introVideoTemplate) {
    var defaultIntroVideoData = {};

    var IntroVideoView = BaseView.extend({

        initialize: function(options) {
            this.introVideoData = options.introVideoData || defaultIntroVideoData;
            this.parent = options.parent;
        },

        render: function() {
            this.$el.html(_.template(introVideoTemplate)({
                model: this.model.attributes
            }));
            return this;
        }

    });
    return IntroVideoView;
});
