import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Simulation extends PagesBaseComponent{

    constructor(props) {
        super(props);
        this.componentType = 'simulation';
        this.changeHandlerName = 'simulationChanged';
    }

    
}
