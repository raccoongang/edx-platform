import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';

import { connect } from 'react-redux';

import { TITLE_CHANGED } from '../store/actionTypes';


import Title from '../components/Title';
import Introduction from '../components/Introduction';
import InteractiveSimulation from '../components/InteractiveSimulation';
import Question from '../components/Question';
import EndServey from '../components/EndSurvey';

import {addElement} from '../utils/api';

import '../sass/_nav-panel.scss';


export class TeacherTemplate extends React.Component{

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
                this.state.showBar ? <div className="author-holder">
                <div className="nav-panel">
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
                        <div className="panel-btn-holder">
                            <button type="button" className="panel-btn" onClick={this.closeBar.bind(this)}>save</button>
                        </div>
                    </div>
                </div>

                <div className="author-block__wrapper">
                    <div className="author-block__content">
                        <div className="author-block__image">
                            <img src="https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/scenario_page/u620.png?token=937ef3394f9bbd5177382de1fe4cbf677b95681186e42c8b44b00217fe8c6834" alt="/"/>
                        </div>
                        <div className="author-block__question">
                            <div className="author-block__question-title">
                                Hooke's Law
                            </div>
                            <div className="author-block__question-text">
                                Imagine that you are standing on a cliff, and you've just been hooked up to a bungee cord. The instructor gives you a pat on the back and then it's time to jump. What will happen?
                            </div>
                        </div>
                    </div>
                    <div className="author-block__buttons">
                        <button type="button" className="author-block__btn">
                            Next
                        </button>
                    </div>
                </div>

                <button className="close-popup">&#2715;</button>
            </div> : null
            
        );
    }
}


const mapStateToProps = (store) => {
    return {
        titleContent: store.title.content
    }
}

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        changeTitle: (content) => {
            return dispatch({type: TITLE_CHANGED, content: content})
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(TeacherTemplate);
