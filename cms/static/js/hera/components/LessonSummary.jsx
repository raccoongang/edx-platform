import React from 'react';

export default class LessonSummary extends React.Component{

    changeImgUrl(e) {
        this.props.lessonSummaryChanged({
            ...this.props.lessonSummary,
            imgUrl: e.target.value
        })
    }

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content is-mod">
                    <div className="field">
                        <label className="field__label">
                           Add mascot for this page here
                        </label>
                    </div>
                    <div className="author-block__image is-full-width">
                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true" />
                        </div>
                        <img src={this.props.lessonSummary.imgUrl} alt=""/>
                    </div>
                </div>
                <div className="author-toolbar">
                    <div className="author-toolbar__row is-full">
                        <div className="author-toolbar__row-holder">
                            <input
                                className="author-toolbar__field is-full"
                                type="text"
                                placeholder='Paste URL of the image'
                                value={this.props.lessonSummary.imgUrl}
                                onChange={this.changeImgUrl.bind(this)}
                            />
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
