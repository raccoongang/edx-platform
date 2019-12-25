import React from 'react';


export default class Question extends React.Component{

    render() {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex]
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img
                        src={activeQuestion.imgUrl}
                        alt=""/>
                    </div>
                    <div className="author-block__question">
                        {activeQuestion.content}
                    </div>
                </div>
                <div className="author-block__buttons">
                    <button type="button" className="author-block__btn">
                        Next
                    </button>
                </div>
            </div>
        )
    }
}
