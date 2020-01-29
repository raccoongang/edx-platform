import React from 'react';
import partial from '../utils/partial';
import WYSWYGComponent from "./WYSWYGComponent";


class SurveyAnswer extends React.Component {
    render() {
        const {dataKey, isLast, answer} = this.props;
        return <div className="questions__list__item">
            <label className="questions__list__label">
                <div className="questions__list__text is-single">
                    <input className="questions__list__text-hint"
                        placeholder="Answer text"
                        type="text"
                        onChange={(event) => this.props.handleQuestionAnswerChange(event, dataKey)}
                        value={answer}/>
                </div>
            </label>
            <div className="end-survey__radio-buttons">
                {isLast && <button className="end-survey__radio-btn is-add"
                                   type="button"
                                   onClick={(event) => this.props.handleQuestionAnswerAdd(event, dataKey)}>
                    <i className="fa fa-plus-square" aria-hidden="true"/>
                </button>}
                {!this.props.hideTrashbox && (
                    <button className="end-survey__radio-btn is-remove"
                            type="button"
                            onClick={(event) => this.props.handleQuestionAnswerRemove(event, dataKey)}>
                        <i className="fa fa-trash-o" aria-hidden="true"/>
                    </button>
                )}
            </div>
        </div>;
    }
};


class SurveyQuestion extends React.Component {
    constructor(props) {
        super(props);
        this.handleQuestionTextChange = this.handleQuestionTextChange.bind(this);
        this.handleQuestionAnswerChange = this.handleQuestionAnswerChange.bind(this);
        this.handleQuestionAnswerAdd = this.handleQuestionAnswerAdd.bind(this);
        this.handleQuestionAnswerRemove = this.handleQuestionAnswerRemove.bind(this);
    }

    handleQuestionTextChange(event) {
        const questionText = event.target.value;
        this.props.changeHandler(this.props.index, {
            type: this.props.type,
            possibleAnswers: this.props.possibleAnswers,
            questionText
        });
    }

    handleQuestionAnswerChange(event, idx) {
        const answer = event.target.value;
        this.props.changeHandler(this.props.index, {
            possibleAnswers: this.props.possibleAnswers.map((item, ind) => {
                if (ind === idx) {
                    return answer;
                }
                return item
            }),
            questionText: this.props.questionText,
            type: this.props.type
        });
    }

    handleQuestionAnswerAdd(event, idx) {
        this.props.changeHandler(this.props.index, {
            possibleAnswers: this.props.possibleAnswers.concat(['']),
            questionText: this.props.questionText,
            type: this.props.type
        });
    }

    handleQuestionAnswerRemove(event, idx) {
        this.props.changeHandler(this.props.index, {
            questionText: this.props.questionText,
            possibleAnswers: this.props.possibleAnswers.filter((item, ind) => {
                return ind !== idx;
            }),
            type: this.props.type
        });
    }

    render() {
        const {possibleAnswers, questionText} = this.props;
        const hasAnswers = !!(possibleAnswers.length);
        return (
            <div className="end-survey__field">
                
                <div className="end-survey__field-title">
                    <label className="end-survey__field-title__label">
                        {this.props.isConfidence ? 'Confidence Question ' : 'Survey Question'}
                        {
                            !this.props.isConfidence && (
                            <button class="end-survey__row-btn is-remove" type="button" onClick={() => this.props.removeHandler(this.props.index)}>
                                <i class="fa fa-trash-o" aria-hidden="true"></i>
                                Remove question
                            </button>
                            )
                        }
                    </label>
                    <input className="end-survey__field-title__input"
                        type="text"
                        value={questionText}
                        onChange={this.handleQuestionTextChange}
                    />
                </div>
                <div className="end-survey__field-radios">
                    <div className="questions__wrapper is-radio">
                        {hasAnswers && possibleAnswers.map((item, idx) => (
                            <SurveyAnswer
                                key={idx}
                                dataKey={idx}
                                isLast={idx === (possibleAnswers.length - 1)}
                                hideTrashbox={possibleAnswers.length === 1}
                                answer={item}
                                handleQuestionAnswerChange={this.handleQuestionAnswerChange}
                                handleQuestionAnswerAdd={this.handleQuestionAnswerAdd}
                                handleQuestionAnswerRemove={this.handleQuestionAnswerRemove}
                            />
                        ))}
                    </div>
                </div>
            </div>
        );
    }
}


export default class EndSurvey extends React.Component {
    constructor(props) {
        super(props);
        this.endSurveyQuestionChanged = this.endSurveyQuestionChanged.bind(this);
        this.endSurveyConfidenceChanged = this.endSurveyConfidenceChanged.bind(this);
        this.addEndSurveyQuestion = this.addEndSurveyQuestion.bind(this);
        this.removeEndSurveyQuestion = this.removeEndSurveyQuestion.bind(this);
    }

    endSurveyQuestionChanged(index, data) {
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            questions: this.props.endSurvey.questions.map((item, idx) => {
                if (idx === index) {
                    return {
                        ...data
                    };
                }
                return item
            })
        });
    }

    endSurveyConfidenceChanged(index, data) {
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            confidence: data
        })
    }

    addEndSurveyQuestion() {
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            questions: this.props.endSurvey.questions.concat([{
                type: 'options',
                questionText: '',
                possibleAnswers: ['']
            }])
        })
    }

    removeEndSurveyQuestion(index) {
        console.log(index);
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            questions: this.props.endSurvey.questions.filter((item, ind) => {
                return ind !== index;
            })
        })
    }

    changeHeading(event) {
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            heading: event.target.value
        })
    }

    changeImgUrl(event) {
        this.props.endSurveyChanged({
            ...this.props.endSurvey,
            imgUrl: event.target.value
        })
    }

    render() {
        const {questions, confidence, heading, imgUrl} = this.props.endSurvey;
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__question is-large">
                        <div className="end-survey__row">
                            <div className="end-survey__field">
                                <div className="end-survey__field-title">
                                    <input className="end-survey__field-title__input"
                                           placeholder="Enter title of the page"
                                           type="text"
                                           value={heading}
                                           onChange={this.changeHeading.bind(this)}/>
                                </div>
                            </div>
                        </div>
                        <div className="end-survey__row">
                            {!!(questions.length) && questions.map((item, idx) => {
                                return (
                                        <SurveyQuestion
                                            key={idx}
                                            index={idx}
                                            removeHandler={this.removeEndSurveyQuestion}
                                            changeHandler={this.endSurveyQuestionChanged}
                                            {...item}/>
                                    )
                            })}

                            <div className="end-survey__row-buttons">
                                <button className="end-survey__row-btn is-add" type="button" onClick={this.addEndSurveyQuestion}>
                                    <i className="fa fa-plus-circle" aria-hidden="true"/>
                                    Add a question
                                </button>
                            </div>
                        </div>
                        <div className="end-survey__row">
                            <SurveyQuestion
                                index={1}
                                isConfidence={true}
                                changeHandler={this.endSurveyConfidenceChanged}
                                {...confidence}
                                />
                        </div>
                    </div>
                    <div className="author-block__image is-small">
                        {
                            imgUrl ? (
                                <img className="end-survey__img" src={imgUrl} alt=""/>
                            ) : (
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true"/>
                                </div>
                            )
                        }
                    </div>
                </div>
                <div className="author-toolbar is-end">
                    <div className="author-toolbar__row">
                        <div className="author-toolbar__row-holder">
                            <input
                                className="author-toolbar__field"
                                type="text"
                                placeholder='Paste URL of the image'
                                value={imgUrl}
                                onChange={this.changeImgUrl.bind(this)}
                            />
                            {/* <button className="author-toolbar__btn cancel">
                                <i className="fa fa-trash-o" aria-hidden="true"/>
                            </button> */}
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
