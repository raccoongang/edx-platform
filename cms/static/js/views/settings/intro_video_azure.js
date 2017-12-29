define([
    'js/views/baseview',
    'underscore',
    'text!templates/settings-intro-video-azure.underscore'
], function(BaseView, _, introVideoTemplate) {
    var defaultIntroVideoData = {};

    var IntroVideoView = BaseView.extend({
        events: {
            'click .remove-course-introduction-azure-video': 'removeVideo'
        },

        initialize: function(options) {
            this.introVideoData = options.introVideoData || defaultIntroVideoData;
            this.parent = options.parent;
            this.courseVideos = options.courseVideos;
        },

        render: function() {
            this.$el.html(_.template(introVideoTemplate)({
                model: this.model.attributes,
                courseVideos: this.courseVideos
            }));
            return this;
        },

        removeVideo: function(event) {
            event.preventDefault();
            if (this.model.has('intro_video_id')) {
                this.$el.find('#course-video-list').val('');
                this.$el.find('.azuremediaplayer').hide();
                this.$el.find('.remove-course-introduction-azure-video').hide();
                this.model.set('intro_video_id', '');
            }
        }

    });
    return IntroVideoView;
});
