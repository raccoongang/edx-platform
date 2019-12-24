import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';


export default class SwitchComponent extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
            showInput: false
        };
        this.toggleShowInput = this.toggleShowInput.bind(this);
    }

    handleClick(event) {
        event.preventDefault();
        this.props.switchComponent(this.props.blockType, this.props.isQuestion, this.props.index);
    }

    toggleShowInput() {
        this.setState({
            showInput: !this.state.showInput
        });
    }

    changeTitle(e) {
        this.props.changeTitle(e, this.props.storeName, this.props.changeHandler);
    }

    render() {
        const className = this.props.isActive ? 'nav-panel-list__link active' : 'nav-panel-list__link';
        return (
            <div>
                <a href="#" className={className} onClick={this.handleClick.bind(this)}>
                    {this.props.title}
                </a>
                {
                    !this.props.isQuestion && (
                        <div>

                            <input 
                                className={`edit-input${!this.state.showInput ? ' is-hidden' : ''}`}
                                onBlur={this.toggleShowInput}
                                value={this.props.title}
                                type="text"
                                onChange={this.changeTitle.bind(this)} />
                            <i className="edit-btn fa fa-pencil" aria-hidden="true" onClick={this.toggleShowInput} />
                        </div>
                    )
                }
            </div>
        )
    }
}
