define([
    'js/views/baseview',
    'underscore',
    'text!templates/settings-intro-video-azure.underscore'
], function(BaseView, _, introVideoTemplate) {
    var IntroVideoView = BaseView.extend({
        defaultFailureMessage: gettext('This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.'),  // eslint-disable-line max-len

        initialize: function(options) {
            this.introVideoData = options.introVideoData;
            this.parent = options.parent;
            this.courseVideos = options.courseVideos;
            this.videoHandlerUrl = options.videoHandlerUrl;
        },

        render: function(responseData) {
            // helper to use in template
            var captionEnabled = function(caption) {
                var result = _.filter(JSON.parse(this.model.intro_video_captions), function(parsedCaption) {
                    return parsedCaption.lang === caption.language;
                });
                return !!result.length;
            };

            if (responseData) {
                var videoInfo = responseData.video_info;
                var captions = responseData.captions;
            }
            this.$el.html(_.template(introVideoTemplate)({
                model: this.model.attributes,
                courseVideos: this.courseVideos,
                videoInfo: videoInfo,
                captions: captions || [],
                captionEnabled: captionEnabled
            }));
            if (!videoInfo) {
                this.getIntroVideoData(this.model.get('intro_video_id'));
            }
            return this;
        },

        getIntroVideoData: function(edxVideoId) {
            if (!edxVideoId) return;
            $.ajax({
                type: 'GET',
                url: this.videoHandlerUrl + '/' + edxVideoId,
                contentType: 'application/json',
                context: this
            }).done(function(responseData) {
                this.model.set('intro_video_manifest', responseData.video_info.smooth_streaming_url);
                this.render(responseData);
            }).fail(function(response) {
                var errorMsg;
                try {
                    errorMsg = JSON.parse(response.responseText).error;
                } catch (error) {
                    errorMsg = this.defaultFailureMessage;
                }
                console.error(errorMsg);
            })
        },

        reset: function() {
            this.model.set('intro_video_id', '');
            this.model.set('intro_video_manifest', '');
            this.model.set('intro_video_captions', '[]');
        }

    });
    return IntroVideoView;
});
