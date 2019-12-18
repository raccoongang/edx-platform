import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';




import Title from './components/Title';
import Introduction from './components/Introduction';
import InteractiveSimulation from './components/InteractiveSimulation';
import Question from './components/Question';
import EndServey from './components/EndSurvey';

import {addElement} from './utils/api';

import './sass/_nav-panel.scss';


export class HeraApp extends React.Component{

    constructor(props) {
        super(props);
        this.addSubsection = this.addSubsection.bind(this);
        this.handlerClick = this.handlerClick.bind(this);

        this.state = {
            showBar: false,
        };
    }

    addSubsection(target) {
        addElement(target.dataset.parent, target.dataset.category, target.dataset.defaultName).then((response) => {
            this.setState({...response.data});
        });
    }

    initTinyMCE() {
        tinymce.init({
            selector: '.title-xblock',
            plugins: "table",
            init_instance_callback: function (editor) {
                editor.on('change', function (e) {
                    console.log(e.target.getContent());
                });
            }
        });

    }

    handlerClick(event) {
        const target = event.target;
        if (target.dataset.category === 'sequential') {
            event.preventDefault();
            this.setState({
                showBar: true
            }, this.initTinyMCE);
            this.addSubsection(target);
        }
    }

    closeBar() {
        this.setState({
            showBar: false
        }, () => {
            tinymce.remove('.title-xblock');
        });
    }

    componentDidMount() {
        setTimeout(() => {
            const buttons = document.getElementsByClassName('button button-new');
            for (let i=0; i<buttons.length; i++) {
                const element = buttons[i];
                const category = element.getAttribute('data-category');
                if (category === 'sequential') {
                    element.addEventListener('click', this.handlerClick);
                }
            };
        },2000);
    }

    render() {
        return (
            this.state.showBar ? <div className="nav-panel">
                <div className="nav-panel-wrapper">
                    <h3 className="nav-panel-title">Lesson Layer</h3>
                    <ul className="nav-panel-list">
                        <li className="nav-panel-list__item">
                            <textarea class="title-xblock" name="" id="title-xblock" cols="30" rows="10"></textarea>
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
