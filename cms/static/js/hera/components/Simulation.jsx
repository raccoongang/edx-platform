import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Simulation extends PagesBaseComponent{

    constructor(props) {
        super(props);
        this.componentType = 'simulation';
        this.changeHandlerName = 'simulationChanged';
        this.addImageHandlerName = 'simulationImageAdd';
        this.removeImageHandlerName = 'simulationImageRemove';
        this.changeImageHandlerName = 'simulationImageChange';
        this.addContentHandler = 'simulationAddContent';
        this.removeContentHandler = 'simulationRemoveContent';
    }
}
