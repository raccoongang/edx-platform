import React from 'react';

import SwitchComponent from '../components/SwitchComponent';


export default class LeftSidebarQuestions extends React.Component{

    render() {
        return (
            <div>
                <div className="nav-panel-accrd">
                    <input className="nav-panel-accrd__trigger" type="checkbox" id="chck1" />
                    <label className="tab-label nav-panel-accrd__link" htmlFor="chck1">Questions</label>
                    <ul className="nav-panel-questions-list nav-panel-accrd__content">
                        {this.props.questions.map((question, index) => {
                            return (
                                <li className="nav-panel-questions-list__item" key={index}>
                                    <SwitchComponent
                                        questionRemoved={this.props.questionRemoved}
                                        changeQuestionTitle={this.props.changeQuestionTitle}
                                        isActive={this.props.activeQuestionIndex === index}
                                        switchComponent={this.props.switchComponent}
                                        blockType={this.props.blockType}
                                        isQuestion={true}
                                        index={index}
                                        title={question.title}/>
                                </li>
                            )
                        })}
                        <li className="nav-panel-questions-list__item">
                            <button className="add-btn" onClick={this.props.questionAdded}>
                                + add question
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        )
    }
}
