define([
    'js/views/baseview',
    'underscore',
    'text!templates/settings-intro-video.underscore'
], function(BaseView, _, introVideoTemplate) {
    var defaultIntroVideoData = {
        'all-rights-reserved': {
            'name': gettext('All Rights Reserved'),
            'tooltip': gettext('You reserve all rights for your work')
        }
    };

    var IntroVideoView = BaseView.extend({
        events: {
            'click .remove-course-introduction-video': 'removeVideo'
        },

        initialize: function(options) {
            this.introVideoData = options.introVideoData || defaultIntroVideoData;
            this.parent = options.parent;
        },

        render: function() {
            this.$el.html(_.template(introVideoTemplate)({
                model: this.model.attributes
            }));
            this.$el.find('.current-course-introduction-video iframe').attr('src', this.model.videosourceSample());
            this.$el.find('#course-introduction-video').val(this.model.get('intro_video') || '');
            if (this.model.has('intro_video')) {
                this.$el.find('.remove-course-introduction-video').show();
            } else {
                this.$el.find('.remove-course-introduction-video').hide();
            };
            return this;
        },

        removeVideo: function(event) {
            event.preventDefault();
            if (this.model.has('intro_video')) {
                this.model.set_videosource(null);
                this.$el.find('.current-course-introduction-video iframe').attr('src', '');
                this.$el.find('#course-introduction-video').val('');
                this.$el.find('.remove-course-introduction-video').hide();
            }
        }
    });
    return IntroVideoView;
});
