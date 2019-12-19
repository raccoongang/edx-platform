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
import SwitchComponent from '../components/SwitchComponent';

import {addElement} from '../utils/api';

import '../sass/main.scss';
import Questions from './Questions';


const ActiveComponentsMap = {
    'Title': Title,
    'Introduction': Introduction,
    'Interactive Simulation': InteractiveSimulation,
    'Question': Question,
    'End Servey': EndServey,
};

const getComponentByTitle = (title) => {
    if (title.includes('Question')) {
        return ActiveComponentsMap['Question'];
    } else {
        return ActiveComponentsMap[title];
    }
}


export class TeacherTemplate extends React.Component{

    constructor(props) {
        super(props);
        this.addSubsection = this.addSubsection.bind(this);
        this.handlerClick = this.handlerClick.bind(this);
        this.switchComponent = this.switchComponent.bind(this);
        this.closeBar = this.closeBar.bind(this);

        this.state = {
            showBar: false,
            activeComponent: 'Introduction'
        };
    }

    addSubsection(target) {
        addElement(target.dataset.parent, target.dataset.category, target.dataset.defaultName).then((response) => {
            this.setState({...response.data});
        });
    }

    initTinyMCE(selector) {
        tinymce.init({
            selector: selector,
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
            const rootElement = document.getElementById('hera-popup');
            rootElement.classList.add("popup-open");
            this.addSubsection(target);
        }
    }

    closeBar() {
        const rootElement = document.getElementById('hera-popup');
        rootElement.classList.remove("popup-open");
        tinymce.remove('.title-xblock');
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

    switchComponent(title) {
        this.setState({
            activeComponent: title
        });
    }

    render() {
        const ActiveComponent = getComponentByTitle(this.state.activeComponent);
        return (
            <div className="author-holder">
                <div className="nav-panel">
                    <div className="nav-panel-wrapper">
                        <h3 className="nav-panel-title">Lesson Layer</h3>
                        <ul className="nav-panel-list">
                            <li className="nav-panel-list__item">
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'Title'} title="Title"/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'Introduction'} title="Introduction"/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'Interactive Simulation'} title="Interactive Simulation"/>
                            </li>
                            <li className="nav-panel-list__item with-add-list">
                                <Questions activeComponent={this.state.activeComponent} switchComponent={this.switchComponent} questions={this.props.questions}/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'End Servey'} title="End Servey"/>
                            </li>
                        </ul>
                        <div className="panel-btn-holder">
                            <button type="button" className="panel-btn" onClick={this.closeBar}>save</button>
                        </div>
                    </div>
                </div>
                <ActiveComponent 
                    initTinyMCE={this.initTinyMCE} 
                    title={this.props.title}
                    introduction={this.props.introduction}
                    {...this.props}/>
                <button className="close-popup" onClick={this.closeBar}>&#2715;</button>
            </div>
        );
    }
}


const mapStateToProps = (store) => {
    return {
        title: store.title,
        introduction: store.introduction,
        questions: store.questions.questions
    };
};

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        changeTitle: (content) => {
            return dispatch({type: TITLE_CHANGED, content: content});
        }
    };
};

export default connect(mapStateToProps, mapDispatchToProps)(TeacherTemplate);
