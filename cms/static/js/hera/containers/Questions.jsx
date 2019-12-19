import React from 'react';

import SwitchComponent from '../components/SwitchComponent';


export default class Questions extends React.Component{

    render() {
        let activeQuestionIndex;
        for (let i in this.props.questions) {
            if (this.props.questions[i].title === this.props.activeComponent) {
                activeQuestionIndex = i;
            }
        }
        return (
            <div>
                <div className="nav-panel-accrd">
                    <a href="#" onClick={() => null} className="nav-panel-accrd__link">
                        Questions
                    </a>
                </div>
                <ul className="nav-panel-questions-list nav-panel-accrd__content">
                    {this.props.questions.map((question, index) => {
                        return (
                            <li className="nav-panel-questions-list__item" key={index}>
                                <SwitchComponent isActive={activeQuestionIndex == index} switchComponent={this.props.switchComponent} title={`Question${index+1}`}/>
                            </li>
                        )
                    })}
                </ul>
            </div>
        )
    }
}
