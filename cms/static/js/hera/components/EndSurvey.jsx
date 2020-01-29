import React from 'react';
import partial from '../utils/partial';
import WYSWYGComponent from "./WYSWYGComponent";


class SurveyAnswer extends React.Component {
    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        const {dataKey, update} = this.props;
        update(dataKey, event.target.value);
    }

    render() {
        console.log(this.props.key);
        const {dataKey, text, isLast, addAnswer, removeAnswer} = this.props;
        return <div className="questions__list__item">
            <label className="questions__list__label">
                <input className="questions__list__input" type="radio"/>
                <div className="questions__list__text">
                    <input className="questions__list__text-hint"
                           placeholder="Answer text"
                           type="text"
                           onChange={this.handleChange}
                           value={text}/>
                </div>
            </label>
            <div className="end-survey__radio-buttons">
                {isLast && <button className="end-survey__radio-btn is-add"
                                   type="button"
                                   onClick={addAnswer}>
                    <i className="fa fa-plus-square" aria-hidden="true"/>
                </button>}
                <button className="end-survey__radio-btn is-remove"
                        type="button"
                        onClick={() => removeAnswer(dataKey)}>
                    <i className="fa fa-trash-o" aria-hidden="true"/>
                </button>
            </div>
        </div>;
    }
};


class SurveyQuestion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            answers: [],
            questionText: ''

        };

        this.addAnswer = this.addAnswer.bind(this);
        this.removeAnswer = this.removeAnswer.bind(this);
        this.update = this.update.bind(this);
        this.handleQuestionTextChange = this.handleQuestionTextChange.bind(this);
    }

    componentDidMount() {
        this.addAnswer(2);
    }

    handleQuestionTextChange(event) {
        this.setState({questionText: event.target.value})
    }

    addAnswer(bulk = 1) {
        let answers = this.state.answers;
        const self = this;

        // Class is used to avoid implementing deep copy of props object
        // Might be hard to reuse in reducer. Might require refactoring
        class defaultProps {
            constructor() {
                this.update = self.update;
                this.addAnswer = partial(self.addAnswer, 1);  // second arg always will be event
                this.removeAnswer = self.removeAnswer
            }
        }

        for (let n = 0; n < bulk; n++) {
            answers.push(new defaultProps());
        }

        this.setState({answers: answers});
    }

    removeAnswer(idx) {
        let answers = this.state.answers;
        answers.splice(idx, 1);
        this.setState({answers: answers});
    }

    update(idx, value) {
        let answers = this.state.answers;
        answers[idx].text = value;
        this.setState({answers: answers});
    }

    render() {
        const {answers, questionText} = this.state;
        const hasAnswers = !!(answers.length);
        return <div className="end-survey__field">
            <div className="end-survey__field-title">
                <label className="end-survey__field-title__label">
                    Text of the question
                </label>
                <input className="end-survey__field-title__input"
                       type="text"
                       value={questionText}
                       onChange={this.handleQuestionTextChange}
                />
            </div>
            <div className="end-survey__field-radios">
                <div className="questions__wrapper is-radio">
                    {hasAnswers &&
                    answers.map((item, idx) => (
                        <SurveyAnswer key={idx} dataKey={idx} isLast={idx === (answers.length - 1)} {...item}/>
                    ))}
                </div>
            </div>
        </div>;
    }
}


export default class EndSurvey extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            questions: [],
            pageTitle: ''

        };
    }

    componentDidMount() {
        this.addQuestion(2);
    }

    addQuestion(bulk = 1) {
        let questions = this.state.questions;

        for (let n = 0; n < bulk; n++) {
            questions.push({});  // just to track number of items
        }

        this.setState({questions: questions});
    }

    render() {
        const {questions} = this.state;
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__question is-large">
                        <div className="end-survey__row">
                            <div className="end-survey__field">
                                <div className="end-survey__field-title">
                                    <input className="end-survey__field-title__input"
                                           placeholder="Enter title of the page"
                                           type="text"/>
                                </div>
                            </div>
                        </div>
                        <div className="end-survey__row">

                            {!!(questions.length) && questions.map((item, idx) => <SurveyQuestion key={idx}/>)}

                            <div className="end-survey__row-buttons">
                                <button className="end-survey__row-btn is-remove" type="button">
                                    <i className="fa fa-trash-o" aria-hidden="true"/>
                                    Remove row
                                </button>
                                <button className="end-survey__row-btn is-add" type="button">
                                    <i className="fa fa-plus-circle" aria-hidden="true"/>
                                    Add row
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="author-block__image is-small">
                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true"/>
                        </div>
                    </div>
                </div>
                <div className="author-toolbar is-right">
                    <div className="author-toolbar__row">
                        <div className="author-toolbar__row-holder">
                            <input
                                className="author-toolbar__field"
                                type="text"
                                placeholder='Paste URL of the image'
                            />
                            <button className="author-toolbar__btn cancel">
                                <i className="fa fa-trash-o" aria-hidden="true"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
