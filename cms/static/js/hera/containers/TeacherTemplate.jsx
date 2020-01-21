import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';

import { connect } from 'react-redux';

import {getData, addSubsection, createUnit, createIntroductionXBlock, saveIntroductionXBlockData, getXblockData, changeUnitName} from '../utils/api';

import * as actionTypes from '../store/actionTypes';


import Title from '../components/Title';
import Introduction from '../components/Introduction';
import Simulation from '../components/Simulation';
import Question from '../components/Question';
import LeftSidebarQuestions from './LeftSidebarQuestions';
import EndSurvey from '../components/EndSurvey';
import SwitchComponent from '../components/SwitchComponent';

import '../sass/main.scss';


const ActiveComponentsMap = {
    'title': Title,
    'introduction': Introduction,
    'simulation': Simulation,
    'question': Question,
    'endSurvey': EndSurvey,
};

const getComponentByTitle = (title) => {
    if (title.includes('question')) {
        return ActiveComponentsMap['question'];
    } else {
        return ActiveComponentsMap[title] || ActiveComponentsMap['introduction'];
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
        this.changeTitle = this.changeTitle.bind(this);
        this.changeQuestionTitle = this.changeQuestionTitle.bind(this);

        this.state = {
            activeComponent: 'introduction',
            isQuestion: false
        };
    }

    addSubsection(target) {
        this.props.subsectionDataChanged(target.dataset.parent, target.dataset.category, target.dataset.defaultName);
        this.props.introductionNew();
        this.props.simulationNew();
        this.setState({
            activeComponent: 'introduction',
            doSaveNewSubsection: true
        });
    }

    closeBar() {
        const rootElement = document.getElementById('hera-popup');
        rootElement.classList.remove("popup-open");
        this.props.introductionNew();
        this.setState({
            activeComponent: 'introduction',
            isQuestion: false,
            activeQuestionIndex: null, // clean activeQuestionIndex to unset an active mark from the last active question.
            isSaving: false
        });
    }

    componentDidMount() {
        document.addEventListener('click', (e) => {
            this.handleNewSubsection(e);
            this.handleEditSubsection(e);
        });
    }

    switchComponent(component, isQuestion, index) {
        this.setState({
            activeComponent: component,
            isQuestion: isQuestion,
            activeQuestionIndex: index
        });
    }

    removeComponent(index) {
        let activeIndex = this.state.activeQuestionIndex;
        if (activeIndex > this.props.questions.questions.length - 2) {
            activeIndex = this.props.questions.questions.length - 2;
        }
        if (activeIndex < 0) {
            this.setState({
                activeComponent: 'introduction'
            });
        } else {
            this.setState({
                activeQuestionIndex: activeIndex
            });
        }
        this.props.questionRemoved(index);
    }

    changeTitle(e, storeName, handlerName) {
        this.props[handlerName]({
            ...this.props[storeName],
            title: e.target.value
        });
    }

    changeQuestionTitle(title, questionIndex) {
        this.props.questionTitleChanged({
            index: questionIndex,
            title: title
        });
    }

    /**
     * Saving newly added or edited subsection.
     */
    save() {
        // Pages saving
        const introductionData = this.props.introduction;

        this.setState({
            isSaving: true
        });

        /**
         * Auxiliary Promise function, we need to wait the backend to handle our requests.
         */
        const sleeper = () => {
            return function(x) {
              return new Promise(resolve => setTimeout(() => resolve(x), 1000));
            };
        };

        if (introductionData.xBlockID) { // if xBlockID is located we assume all data are being edited
            this.props.saveChanges().then((response => {
                this.closeBar();
                window.location.reload();
            })).catch((error)=>{
                this.setState({
                    isSaving: false
                });
                console.log(error);
            });
        } else {
            this.props.createSubsection().then((response => {
                this.closeBar();
                window.location.reload();
            })).catch((error)=>{
                this.setState({
                    isSaving: false
                });
                console.log(error);
            });
        }
    }

    /**
     * Click on "Edit Subsection"
     */
    handleEditSubsection(event) {
        if (event.target.parentElement.className.includes('hera-edit-subsection')) {
            const locator = event.target.parentElement.dataset.locator;
            if (locator.includes('sequential')) {
                this.props.questionsReset();
                getData(locator).then(data => {
                    const subsectionChildren = data.child_info.children;
                    let theLast = false;
                    let questionsParentLocators = [];
                    for (let childInfo in subsectionChildren) {
                        if (+childInfo === subsectionChildren.length-1) {
                            theLast = true;
                        }
                        if (subsectionChildren[childInfo].child_info && subsectionChildren[childInfo].child_info.children.length && subsectionChildren[childInfo].child_info.children[0].id) {
                            questionsParentLocators.push({
                                locator: subsectionChildren[childInfo].id
                            });
                            getXblockData(subsectionChildren[childInfo].child_info.children[0].id).then(response => {
                                const data = {
                                    ...response.data,
                                    shouldReset: true,
                                    xBlockID: subsectionChildren[childInfo].child_info.children[0].id,
                                    title: subsectionChildren[childInfo].display_name,
                                    parentLocator: subsectionChildren[childInfo].id
                                };
                                if (response.data && response.data.blockType && response.data.blockType === 'introduction') {
                                    // save data into Introduction component
                                    this.props.introductionLoaded(data);
                                } else if (response.data && response.data.blockType && response.data.blockType === 'title') {
                                    // save data into Title component
                                } else if (response.data && response.data.blockType && response.data.blockType === 'simulation') {
                                    // save data into Simulation component
                                    this.props.simulationLoaded(data);
                                } else if (response.data && response.data.blockType && response.data.blockType === 'question') {
                                    questionsParentLocators.forEach((v,i) => {
                                        if (data.parentLocator === v.locator) {
                                            v.data = data;
                                        }
                                    });
                                }
                                if (theLast) {
                                    let questions = questionsParentLocators.map((question) => {
                                        if (question.data) {
                                            return question.data;
                                        }
                                    });
                                    this.props.questionLoaded(questions.filter(value=>{return value}));
                                    this.props.subsectionDataLocatorsChanged(questionsParentLocators);
                                }
                            })
                        }
                    }
                    this.props.subsectionDataChanged(data.id, data.category, data.display_name);
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
            this.props.questionsReset();
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
                                <SwitchComponent
                                    switchComponent={this.switchComponent}
                                    isActive={this.state.activeComponent === this.props.title.blockType}
                                    blockType={this.props.title.blockType}
                                    title="Title"/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent
                                    switchComponent={this.switchComponent}
                                    isActive={this.state.activeComponent === this.props.introduction.blockType}
                                    changeTitle={this.changeTitle}
                                    changeHandler="introductionChanged"
                                    storeName='introduction'
                                    blockType={this.props.introduction.blockType}
                                    title={this.props.introduction.title}/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent
                                    switchComponent={this.switchComponent}
                                    isActive={this.state.activeComponent === this.props.simulation.blockType}
                                    changeTitle={this.changeTitle}
                                    changeHandler="simulationChanged"
                                    storeName='simulation'
                                    blockType={this.props.simulation.blockType}
                                    title={this.props.simulation.title}/>
                            </li>
                            <li className="nav-panel-list__item with-add-list">
                                <LeftSidebarQuestions
                                    questionAdded={this.props.questionAdded}
                                    questionRemoved={this.removeComponent.bind(this)}
                                    changeQuestionTitle={this.changeQuestionTitle}
                                    activeComponent={this.state.activeComponent}
                                    activeQuestionIndex={this.state.activeQuestionIndex}
                                    switchComponent={this.switchComponent}
                                    questions={this.props.questions.questions}
                                    questionChanges={this.props.questionChanged}
                                    blockType={this.props.questions.blockType}/>
                            </li>
                            <li className="nav-panel-list__item">
                                <SwitchComponent
                                    switchComponent={this.switchComponent}
                                    isActive={this.state.activeComponent === this.props.endSurvey.blockType}
                                    blockType={this.props.endSurvey.blockType}
                                    title="End Survey"/>
                            </li>
                        </ul>
                        <div className="panel-btn-holder">
                            <button type="button" className={`panel-btn ${this.state.isSaving ? 'is-pending' : ''}`} onClick={this.save.bind(this)}>
                                save
                                <span className="panel-btn__loader" />
                            </button>
                        </div>
                    </div>
                </div>
                <ActiveComponent

                    isQuestion={this.state.isQuestion}
                    activeQuestionIndex={this.state.activeQuestionIndex}
                    questions={this.props.questions.questions}

                    title={this.props.title}

                    introduction={this.props.introduction}
                    introductionChanged={this.props.introductionChanged}
                    introductionImageAdd={this.props.introductionImageAdd}
                    introductionImageChange={this.props.introductionImageChange}
                    introductionImageRemove={this.props.introductionImageRemove}
                    introductionAddContent={this.props.introductionAddContent}
                    introductionRemoveContent={this.props.introductionRemoveContent}

                    simulation={this.props.simulation}
                    simulationChanged={this.props.simulationChanged}
                    simulationImageAdd={this.props.simulationImageAdd}
                    simulationImageChange={this.props.simulationImageChange}
                    simulationImageRemove={this.props.simulationImageRemove}
                    simulationAddContent={this.props.simulationAddContent}
                    simulationRemoveContent={this.props.simulationRemoveContent}

                    questionChanged={this.props.questionChanged}

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
        questions: store.questions,
        subsectionData: store.subsectionData,
        endSurvey: store.endSurvey
    };
};

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        changeTitle: (content) => {
            return dispatch({type: actionTypes.TITLE_CHANGED, content: content});
        },
        // introduction
        introductionChanged: (data) => {
            return dispatch({type: actionTypes.INTRODUCTION_CHANGED, data: data});
        },
        introductionLoaded: (data) => {
            return dispatch({type: actionTypes.INTRODUCTION_LOADED, data: data});
        },
        introductionNew: () => {
            return dispatch({type: actionTypes.INTRODUCTION_NEW});
        },
        introductionImageAdd: () => {
            return dispatch({type: actionTypes.INTRODUCTION_IMAGE_ADD});
        },
        introductionImageChange: (data) => {
            return dispatch({type: actionTypes.INTRODUCTION_IMAGE_CHANGED, data: data});
        },
        introductionImageRemove: (data) => {
            return dispatch({type: actionTypes.INTRODUCTION_IMAGE_REMOVE, data: data});
        },
        introductionAddContent: () => {
            return dispatch({type: actionTypes.INTRODUCTION_ADD_CONTENT});
        },
        introductionRemoveContent: (data) => {
            return dispatch({type: actionTypes.INTRODUCTION_REMOVE_CONTENT, data: data});
        },
        // simulation
        simulationChanged: (data) => {
            return dispatch({type: actionTypes.SIMULATION_CHANGED, data: data});
        },
        simulationAddContent: () => {
            return dispatch({type: actionTypes.SIMULATION_ADD_CONTENT});
        },
        simulationRemoveContent: (data) => {
            return dispatch({type: actionTypes.SIMULATION_REMOVE_CONTENT, data: data});
        },
        simulationLoaded: (data) => {
            return dispatch({type: actionTypes.SIMULATION_LOADED, data: data});
        },
        simulationNew: () => {
            return dispatch({type: actionTypes.SIMULATION_NEW});
        },
        simulationImageAdd: () => {
            return dispatch({type: actionTypes.SIMULATION_IMAGE_ADD});
        },
        simulationImageChange: (data) => {
            return dispatch({type: actionTypes.SIMULATION_IMAGE_CHANGED, data: data});
        },
        simulationImageRemove: (data) => {
            return dispatch({type: actionTypes.SIMULATION_IMAGE_REMOVE, data: data});
        },
        // subsection data
        subsectionDataChanged: (parentLocator, category, displayName) => {
            const data = {
                parentLocator: parentLocator,
                category: category,
                displayName: displayName
            }
            return dispatch({type: actionTypes.SUBSECTION_DATA_CHANGED, data: data});
        },
        subsectionDataLocatorsChanged: (questionsParentLocators) => {
            let onlyLocators = [];
            questionsParentLocators.map(el => {
                if (el.data) {
                    onlyLocators.push(el.locator)
                }
            });
            return dispatch({type: actionTypes.SUBSECTION_DATA_PARENT_LOCATORS_CHANGED, data: onlyLocators});
        },
        // questions
        questionTitleChanged: (data) => {
            return dispatch({type: actionTypes.QUESTION_TITLE_CHANGED, data: data});
        },
        questionChanged: (index, data) => {
            return dispatch({type: actionTypes.QUESTION_CHANGED, index: index, data: data});
        },
        questionAdded: () => {
            return dispatch({type: actionTypes.QUESTION_ADDED});
        },
        questionRemoved: (index) => {
            return dispatch({type: actionTypes.QUESTION_DELETED, index: index});
        },
        questionLoaded: (data) => {
            return dispatch({type: actionTypes.QUESTION_LOADED, data: data});
        },
        questionsReset: () => {
            return dispatch({type: actionTypes.QUESTIONS_RESET});
        }
    };
};

export default connect(mapStateToProps, mapDispatchToProps)(TeacherTemplate);
