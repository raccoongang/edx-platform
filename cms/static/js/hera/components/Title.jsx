import React from 'react';

import SingleWYSIWYGComponent from './SingleWYSIWYGComponent';


export default class Title extends React.Component{

    changeImgUrl(e) {
        this.props.titleChanged({
            ...this.props.titleData,
            imgUrl: e.target.value
        });
    }

    changeContent(content) {
        this.props.titleChanged({
            ...this.props.titleData,
            shouldReset: false,
            content: content
        });
    }

    changeHeading(e) {
        this.props.titleChanged({
            ...this.props.titleData,
            heading: e.target.value
        });
    }

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content-mod">
                    <div className="author-block-title">
                        <input
                            className="author-block-title__field"
                            type="text"
                            placeholder="Enter title here"
                            value={this.props.titleData.heading}
                            onChange={this.changeHeading.bind(this)} />
                    </div>
                    <div className="author-block__image">
                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true" />
                        </div>
                        <div className="author-block__image-holder">
                            <img src={this.props.titleData.imgUrl} alt=""/>
                        </div>
                    </div>
                    <div className="author-toolbar">
                        <div className="author-toolbar__row">
                            <div className="author-toolbar__row-holder">
                                <input
                                    className="author-toolbar__field"
                                    placeholder="Paste URL of the image"
                                    type="text"
                                    value={this.props.titleData.imgUrl}
                                    onChange={this.changeImgUrl.bind(this)} />
                            </div>
                        </div>
                    </div>
                    <div className="author-block__question">
                        <SingleWYSIWYGComponent
                            content={this.props.titleData.content}
                            changeHandler={this.changeContent.bind(this)}
                            shouldReset={this.props.titleData.shouldReset}
                            />
                    </div>
                </div>
            </div>
        )
    }
}
