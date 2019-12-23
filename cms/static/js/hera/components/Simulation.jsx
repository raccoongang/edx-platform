import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Simulation extends PagesBaseComponent{

    constructor(props) {
        super(props);
        this.componentType = 'simulation';
    }

    saveContent(id, value) {
        this.props.simulationChanged({
            content: value,
            imgUrl: this.props.simulation.imgUrl,
            iframeUrl: this.props.simulation.iframeUrl,
            index: id
        });
    }
}
