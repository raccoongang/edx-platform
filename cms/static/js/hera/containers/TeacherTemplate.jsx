import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';

import { connect } from 'react-redux';

import {getData, addSubsection, createUnit, createIntroductionXBlock, saveIntroductionXBlockData, getXblockData}from '../utils/api';

import { 
    TITLE_CHANGED,
    INTRODUCTION_CHANGED,
    SUBSECTION_DATA_CHANGED,
    INTRODUCTION_LOADED,
    INTRODUCTION_NEW,
    SIMULATION_CHANGED,
    SIMULATION_LOADED,
    SIMULATION_NEW,
 } from '../store/actionTypes';


import Title from '../components/Title';
import Introduction from '../components/Introduction';
import Simulation from '../components/Simulation';
import Question from '../components/Question';
import Questions from './Questions';
import EndServey from '../components/EndSurvey';
import SwitchComponent from '../components/SwitchComponent';

import '../sass/main.scss';


const ActiveComponentsMap = {
    'Title': Title,
    'Introduction': Introduction,
    'Simulation': Simulation,
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
        this.handleNewSubsection = this.handleNewSubsection.bind(this);
        this.handleEditSubsection = this.handleEditSubsection.bind(this);
        this.switchComponent = this.switchComponent.bind(this);
        this.closeBar = this.closeBar.bind(this);

        this.state = {
            activeComponent: 'Introduction',
            doSaveNewSubsection: true
        };
    }

    addSubsection(target) {
        this.props.subsectionDataChanged(target.dataset.parent, target.dataset.category, target.dataset.defaultName);
        this.props.introductionNew();
        this.props.simulationNew();
        this.setState({
            activeComponent: 'Introduction',
            doSaveNewSubsection: true
        });
    }

    closeBar() {
        const rootElement = document.getElementById('hera-popup');
        rootElement.classList.remove("popup-open");
        this.props.introductionNew();
        this.setState({
            activeComponent: 'Introduction'
        });
    }

    componentDidMount() {
        document.addEventListener('click', (e) => {
            this.handleNewSubsection(e);
            this.handleEditSubsection(e);
        });
    }

    switchComponent(title) {
        this.setState({
            activeComponent: title
        });
    }

    /**
     * Saving newly added or edited subsection.
     */
    save() {
        // Pages saving
        const introductionData = this.props.introduction;
        const simulationData = this.props.simulation;
        const subsectionData = this.props.subsectionData;

        /**
         * Auxiliary Promise function, we need to wait the backend to handle our requests.
         */
        function sleeper() {
            return function(x) {
              return new Promise(resolve => setTimeout(() => resolve(x), 1000));
            };
          }
        if (introductionData.xBlockID) { // if xBlockID is located we assume all data are being edited
            saveIntroductionXBlockData(introductionData.xBlockID, introductionData).then(sleeper()).then(()=>{
                saveIntroductionXBlockData(simulationData.xBlockID, simulationData).then(()=>{
                    this.closeBar();
                    window.location.reload();
                });
            });

        } else {
            addSubsection(subsectionData.parentLocator, subsectionData.category, subsectionData.displayName).then(sleeper()).then(response=>{
                const subsectionLocator = response.data.locator;
                createUnit(subsectionLocator).then(sleeper()).then(response=>{
                    createIntroductionXBlock(response.data.locator).then(sleeper()).then(response=>{
                        saveIntroductionXBlockData(response.data.locator, introductionData).then(sleeper()).then(()=>{
                            createUnit(subsectionLocator).then(sleeper()).then(response=>{
                                createIntroductionXBlock(response.data.locator).then(sleeper()).then(response=>{
                                    saveIntroductionXBlockData(response.data.locator, simulationData);
                                    this.closeBar();
                                    window.location.reload();
                                });
                            });
                        })
                    });
                });
            });
        }
    }

    /**
     * Click on "Edit Subsection"
     */
    handleEditSubsection(event) {
        if (event.target.parentElement.className.includes('xblock-field-value-edit')) {
            const locator = event.target.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.dataset.locator;
            if (locator.includes('sequential')) {
                getData(locator).then(data => {
                    this.props.subsectionDataChanged(data.id, data.category, data.display_name);
                    const subsectionChildren = data.child_info.children;
                    for (let childInfo in subsectionChildren) {
                        getXblockData(subsectionChildren[childInfo].child_info.children[0].id).then(response => {
                            const data = {
                                ...response.data,
                                shouldReset: true,
                                xBlockID: subsectionChildren[childInfo].child_info.children[0].id,
                            };
                            if (response.data.blockType === 'introduction') {
                                // save data into Introduction component
                                this.props.introductionLoaded(data);
                            } else if (response.data.blockType === 'Title') {
                                // save data into Title component
                            } else if (response.data.blockType === 'simulation') {
                                // save data into Simulation component
                                this.props.simulationLoaded(data);
                            }
                        })
                    }
                    document.getElementById('hera-popup').classList.add("popup-open");
                    this.setState({
                        doSaveNewSubsection: false
                    })
                });
            }
        }
    }

    /**
     * Click on "New subsection"
     */
    handleNewSubsection(event) {
        const target = event.target;
        if (event.target.className.includes('button-new') && target.dataset.category === 'sequential') {
            event.preventDefault();
            const rootElement = document.getElementById('hera-popup');
            rootElement.classList.add("popup-open");
            this.addSubsection(target);
        }
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
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'Simulation'} title="Simulation"/>
                            </li>
                            <li className="nav-panel-list__item with-add-list">
                                <Questions activeComponent={this.state.activeComponent} switchComponent={this.switchComponent} questions={this.props.questions}/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent switchComponent={this.switchComponent} isActive={this.state.activeComponent === 'End Servey'} title="End Servey"/>
                            </li>
                        </ul>
                        <div className="panel-btn-holder">
                            <button type="button" className="panel-btn" onClick={this.save.bind(this)}>
                                save
                                <span className="panel-btn__loader" />
                            </button>
                        </div>
                    </div>
                </div>
                <ActiveComponent

                    title={this.props.title}

                    introduction={this.props.introduction}
                    introductionChanged={this.props.introductionChanged}

                    simulation={this.props.simulation}
                    simulationChanged={this.props.simulationChanged}

                />
                <button className="close-popup" onClick={this.closeBar} />
            </div>
        );
    }
}


const mapStateToProps = (store) => {
    return {
        title: store.title,
        introduction: store.introduction,
        simulation: store.simulation,
        questions: store.questions.questions,
        subsectionData: store.subsectionData
    };
};

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        changeTitle: (content) => {
            return dispatch({type: TITLE_CHANGED, content: content});
        },
        // introduction
        introductionChanged: (data) => {
            return dispatch({type: INTRODUCTION_CHANGED, data: data});
        },
        introductionLoaded: (data) => {
            return dispatch({type: INTRODUCTION_LOADED, data: data});
        },
        introductionNew: () => {
            return dispatch({type: INTRODUCTION_NEW});
        },
        // simulation
        simulationChanged: (data) => {
            return dispatch({type: SIMULATION_CHANGED, data: data});
        },
        simulationLoaded: (data) => {
            return dispatch({type: SIMULATION_LOADED, data: data});
        },
        simulationNew: () => {
            return dispatch({type: SIMULATION_NEW});
        },
        subsectionDataChanged: (parentLocator, category, displayName) => {
            const data = {
                parentLocator: parentLocator,
                category: category,
                displayName: displayName
            }
            return dispatch({type: SUBSECTION_DATA_CHANGED, data: data});
        }
    };
};

export default connect(mapStateToProps, mapDispatchToProps)(TeacherTemplate);
