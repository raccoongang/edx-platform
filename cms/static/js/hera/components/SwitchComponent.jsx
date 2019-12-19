import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';


export default class SwitchComponent extends React.Component{

    handleClick(event) {
        event.preventDefault();
        this.props.switchComponent(this.props.title);
    }

    render() {
        const className = this.props.isActive ? 'nav-panel-list__link active' : 'nav-panel-list__link';
        return (
            <a href="#" className={className} onClick={this.handleClick.bind(this)}>{this.props.title}</a>
        )
    }
}
