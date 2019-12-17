import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';
import Title from './components/Title';
import Introduction from './components/Introduction';
import InteractiveSimulation from './components/InteractiveSimulation';
import Question from './components/Question';
import EndServey from './components/EndSurvey';

import './sass/_nav-panel.scss';


const rootUrl = '/xblock/';


export class HeraApp extends React.Component{

    constructor(props) {
        super(props);
        this.addSubsection = this.addSubsection.bind(this);
        this.handlerClick = this.handlerClick.bind(this);

        this.state = {
            showBar: false,
        }
    }

    addSubsection(target) {
        const parentLocator = target.dataset.parent,
                category = target.dataset.category,
                displayName = target.dataset.defaultName;
        fetch(rootUrl + parentLocator, {
            method: 'POST',
            credentials: "same-origin",
            body: JSON.stringify({
                category: category,
                parent_locator: parentLocator,
                display_name: displayName
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'YwFwBXmguKOSCCg621Vhc3Nyk3wMksjIuyEtH1qOqqZqY5OdzxrCjCCM9s7FgTPs',
                'Accept': 'application/json',
            },
        }).then(response=>response.json()).then((data) => {
            // do something with data
            console.log(data);
        }).catch(err=>console.log(err));
    }

    handlerClick(event) {
        const target = event.target;
        event.preventDefault();
        if (target.dataset.category === 'sequential') {
            this.setState({
                showBar: true
            })
            // this.addSubsection(target);
        }
    }

    closeBar() {
        this.setState({
            showBar: false
        });
    }

    componentDidMount() {
        setTimeout(()=>{
            let buttons = document.getElementsByClassName('button button-new');
            for (let i=0; i<buttons.length; i++) {
                buttons[i].addEventListener('click', this.handlerClick);
            }
        },3000);
    }

    render() {
        return (
            this.state.showBar ? <div className="nav-panel">
                <div className="nav-panel-wrapper">
                    <h3 className="nav-panel-title">Lesson Layer</h3>
                    <ul className="nav-panel-list">
                        <li className="nav-panel-list__item">
                            <Title/>
                        </li>
                        <li className="nav-panel-list__item">
                            <Introduction/>
                        </li>
                        <li className="nav-panel-list__item">
                            <InteractiveSimulation/>
                        </li>
                        <li className="nav-panel-list__item with-add-list">
                            <div className="nav-panel-accrd">
                                <a href="#" className="nav-panel-accrd__link">
                                    Questions
                                </a>
                            </div>
                            <ul className="nav-panel-questions-list nav-panel-accrd__content">
                                <li className="nav-panel-questions-list__item">
                                    <Question/>
                                </li>
                                
                            </ul>
                        </li>
                        <li className="nav-panel-list__item">
                            <EndServey/>
                        </li>
                    </ul>
                    <div className="adaptivity-section">
                        <h4 className="adaptivity-section-title">
                            adaptivity
                        </h4>
                        <ul className="adaptivity-section-list">
                            <li className="adaptivity-section-list__item">
                                <a href="/" className="adaptivity-section-list__link">
                                    Initial State
                                </a>
                            </li>
                            <li className="adaptivity-section-list__item">
                                <a href="/" className="adaptivity-section-list__link">
                                    Correct State
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div className="panel-btn-holder">
                        <button type="button" className="panel-btn" onClick={this.closeBar.bind(this)}>save</button>
                    </div>
                </div>
            </div> : null
        );
    }
}
