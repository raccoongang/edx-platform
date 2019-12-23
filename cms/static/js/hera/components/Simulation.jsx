import React from 'react';

import PagesBaseComponent from './PagesBaseComponent';


export default class Simulation extends PagesBaseComponent{

    constructor(props) {
        super(props);
        this.componentType = 'simulation';
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
        this.props.simulationChanged({
            ...this.props.simulation,
            imgUrl: this.state.imgUrl,
        });
    }

    confirmIframeUrl() {
        this.props.simulationChanged({
            ...this.props.simulation,
            iframeUrl: this.state.iframeUrl,
        });
    }

    cancelImgUrl() {
        this.setState({
            imgUrlChanged: false
        }, () => {
            this.props.simulationChanged({
                ...this.props.simulation,
                // imgUrl: this.props.simulation.imgUrl,
            });
        })
    }

    cancelIframeUrl() {
        this.setState({
            iframeUrlChanged: false
        }, () => {
            this.props.simulationChanged({
                ...this.props.simulation,
                // iframeUrl: this.props.simulation.iframeUrl,
            });
        })
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
