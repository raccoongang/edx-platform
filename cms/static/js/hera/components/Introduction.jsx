import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Introduction extends PagesBaseComponent {

    constructor(props) {
        super(props);
        this.componentType = 'introduction';
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
