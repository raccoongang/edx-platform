import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';


export default class SwitchComponent extends React.Component{

    handleClick(event) {
        event.preventDefault();
        this.props.switchComponent(this.props.title)
    }

    render() {
        return (
            <a href="#" className="nav-panel-list__link" onClick={this.handleClick.bind(this)}>{this.props.title}</a>
        )
    }
}
