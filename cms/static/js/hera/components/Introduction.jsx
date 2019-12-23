import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Introduction extends PagesBaseComponent {

    constructor(props) {
        super(props);
        this.componentType = 'introduction';
    }

    changeImgUrl(e) {
        this.setState({
            imgUrl: e.target.value,
            imgUrlChanged: true
        });
    }

    changeIframeUrl(e) {
        this.setState({
            iframeUrl: e.target.value,
            iframeUrlChanged: true
        });
    }

    confirmImgUrl() {
        this.props.introductionChanged({
            ...this.props.introduction,
            imgUrl: this.state.imgUrl,
        });
    }

    confirmIframeUrl() {
        this.props.introductionChanged({
            ...this.props.introduction,
            iframeUrl: this.state.iframeUrl,
        });
    }

    cancelImgUrl() {
        this.setState({
            imgUrlChanged: false
        }, () => {
            this.props.introductionChanged({
                ...this.props.introduction,
                imgUrl: this.props.introduction.imgUrl,
            });
        })
    }

    cancelIframeUrl() {
        this.setState({
            iframeUrlChanged: false
        }, () => {
            this.props.introductionChanged({
                ...this.props.introduction,
                iframeUrl: this.props.introduction.iframeUrl,
            });
        })
    }

    saveContent(id, value) {
        this.props.introductionChanged({
            content: value,
            imgUrl: this.props.introduction.imgUrl,
            iframeUrl: this.props.introduction.iframeUrl,
            index: id
        });
    }
}
