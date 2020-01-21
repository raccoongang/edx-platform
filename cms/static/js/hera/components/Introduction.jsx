import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Introduction extends PagesBaseComponent {

    constructor(props) {
        super(props);
        this.componentType = 'introduction';
        this.changeHandlerName = 'introductionChanged';
        this.addImageHandlerName = 'introductionImageAdd';
        this.removeImageHandlerName = 'introductionImageRemove';
        this.changeImageHandlerName = 'introductionImageChange';
        this.addContentHandler = 'introductionAddContent';
        this.removeContentHandler = 'introductionRemoveContent';
    }
}
