import React from 'react';
import Slider from "react-slick";

import SingleWYSIWYGComponent from './SingleWYSIWYGComponent';
import Skaffolds from './Skaffolds';


export default class Question extends React.Component{

    constructor(props) {
        super(props);

        this.changeQuestionType = this.changeQuestionType.bind(this);
        this.changeOptionCorrectness = this.changeOptionCorrectness.bind(this);
        this.changeOptionTitle = this.changeOptionTitle.bind(this);
        this.changeDescription = this.changeDescription.bind(this);
        this.scaffoldEditingStateChange = this.scaffoldEditingStateChange.bind(this);
        this.changeAnswer = this.changeAnswer.bind(this);
        this.getOptions = this.getOptions.bind(this);
        this.getButtonAddOption = this.getButtonAddOption.bind(this);

        this.state = {
            showSimulation: false,
            scaffoldEditing: false
        };

        this.settingsImg = {
            arrows: true,
            dots: false,
            infinite: false,
            speed: 500,
            slidesToShow: 1,
            slidesToScroll: 1,
        };
    }

    changeQuestionType(e) {
        const dataset = e.target.dataset;
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    type: dataset.type,
                    options: problemType.options.map(opt => {
                        return {
                            correct: false,
                            title: opt.title
                        };
                    })
                };
            }
            return problemType;
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    addOptionItem(e) {
        const problemTypeIndex = e.target.dataset.problemTypeIndex;
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];

        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +problemTypeIndex) {
                return {
                    ...problemType,
                    options: problemType.options.concat([{
                        correct: false,
                        title: ""
                    }])
                };
            }
            return problemType;
        });

        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    removeOptionItem(e) {
        const dataset = e.target.dataset;
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];

        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    type: problemType.type,
                    options: problemType.options.filter((el, ind) => ind !== +dataset.index)
                };
            }
            return problemType;
        });

        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    changeOptionCorrectness(e) {
        const dataset = e.target.dataset;
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    ...problemType,
                    options: problemType.options.map((opt, ind) => {
                        if (['select', 'radio'].includes(problemType.type)) {
                            if (ind === +dataset.index) {
                                return {
                                    correct: e.target.checked,
                                    title: opt.title
                                };
                            } else {
                                return {
                                    correct: false,
                                    title: opt.title
                                };
                            }
                        } else {
                            if (ind === +dataset.index) {
                                return {
                                    correct: e.target.checked,
                                    title: opt.title
                                };
                            } else {
                                return opt;
                            }
                        }
                    })
                };
            }
            return problemType;
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    changeOptionTitle(e) {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        const dataset = e.target.dataset;
        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    ...problemType,
                    options: problemType.options.map((opt, _ind) => {
                        if (_ind === +dataset.index) {
                            return {
                                ...opt,
                                title: e.target.value
                            };
                        } else {
                            return opt;
                        }
                    })
                }
            }
            return problemType;
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    changeDescription(content) {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            description: content
        });
    }

    addImage() {
        let activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            imgUrls: activeQuestion.imgUrls.concat([''])
        });
    }

    removeImage(e) {
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            imgUrls: activeQuestion.imgUrls.filter((el, ind) => {return ind !== +e.target.dataset.index})
        });
    }

    changeImage(e) {
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            imgUrls: activeQuestion.imgUrls.map((el, ind) => {
                if (ind === +e.target.dataset.index) {
                    return e.target.value;
                }
                return el;
            })
        });
    }

    changeIframeUrl(e) {
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            iframeUrl: e.target.value
        });
    }

    changeAnswer(e) {
        const dataset = e.target.dataset;
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    ...problemType,
                    answer: e.target.value
                };
            }
            return problemType;
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    changePreciseness(e) {
        const dataset = e.target.dataset;
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        const problemTypes = activeQuestion.problemTypes.map((problemType, ind) => {
            if (ind === +dataset.problemTypeIndex) {
                return {
                    ...problemType,
                    preciseness: e.target.value
                };
            }
            return problemType;
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            problemTypes: problemTypes
        });
    }

    showSimulation() {
        this.setState({
            showSimulation: !this.state.showSimulation
        });
    }

    scaffoldEditingStateChange(value) {
        this.setState({
            scaffoldEditing: value
        });
    }

    addProblemType() {
        this.props.questionAddNewProblemType(this.props.activeQuestionIndex);
    }

    removeProblemType(e) {
        this.props.questionRemoveProblemType(+this.props.activeQuestionIndex, +e.target.dataset.problemTypeIndex);
    }

    getOptions(problemType, index) {
        const type = problemType.type === 'select' ? 'radio' : problemType.type;
        if (type === 'number') {
            return (
                <div className="questions__list number">
                    <div className="questions__list__item">
                        <input
                            className="questions__list__field"
                            type="number"
                            data-problem-type-index={index}
                            placeholder="Type numbers here"
                            value={problemType.answer}
                            onChange={this.changeAnswer.bind(this)}
                            />
                    </div>
                    <div className="questions__list__item">
                        <input
                            className="questions__list__field"
                            type="text"
                            data-problem-type-index={index}
                            value={problemType.preciseness}
                            onChange={this.changePreciseness.bind(this)}
                            placeholder="Add a tolerance"
                            />
                        <span className="questions__list__field-hint">It can be number or percentage like 12, 12.04 or 34%</span>
                    </div>
                </div>
            );
        } else if (type === 'text') {
            return (
                <div className="questions__list number">
                    <div className="questions__list__item">
                        <input
                            className="questions__list__field"
                            type="text"
                            data-problem-type-index={index}
                            placeholder="Enter Text"
                            value={problemType.answer}
                            onChange={this.changeAnswer.bind(this)}
                            />
                    </div>
                </div>
            );
        }
        return problemType.options.map((option, ind) => {
            return  (
                <div className="questions__list__item">
                    <label className="questions__list__label">
                        <input
                            key={ind}
                            data-index={ind}
                            data-problem-type-index={index}
                            onChange={this.changeOptionCorrectness}
                            className="questions__list__input"
                            type={type}
                            checked={option.correct}/>
                        <div className="questions__list__text">
                            <input
                                onChange={this.changeOptionTitle}
                                key={ind}
                                data-index={ind}
                                data-problem-type-index={index}
                                className="questions__list__text-hint"
                                type="text"
                                placeholder="Type questions text here..."
                                value={option.title}
                                />
                        </div>
                    </label>
                    {problemType.options.length > 1 && (
                        <button className="questions__list__remove-item" title="Remove item">
                            <i
                                className="fa fa-trash-o"
                                data-problem-type-index={index}
                                aria-hidden="true" data-index={ind} onClick={this.removeOptionItem.bind(this)} />
                        </button>
                    )}
                </div>
            );
        });
    };

    getButtonAddOption(type, index) {
        if (!['number', 'text'].includes(type)) {
            return (
                <div className="questions__list__add-item">
                    <button
                        type="button"
                        className="questions__list__add-item__btn"
                        data-problem-type-index={index}
                        onClick={this.addOptionItem.bind(this)}>
                        + add item
                    </button>
                </div>
            );
        }
    };

    render() {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        if (!activeQuestion) {
            return null;
        }
        // this hack just to understand if we need to reset content for the TinyMCE editor in the SingleWYSIWYGComponent
        const shouldResetEditor = this.props.activeQuestionIndex !== this.activeQuestionIndex;

        this.activeQuestionIndex = this.props.activeQuestionIndex;

        return (
            <div className={`author-block__wrapper${this.state.scaffoldEditing ? ' is-scaffold-open' : ''}`}>
                <div className="author-block__content">
                    <div className="author-block__image is-questions-img">
                        {
                            this.state.showSimulation ? (
                                <iframe src={activeQuestion.iframeUrl} frameborder="0" />
                            ) : (
                                <div ref={c => (this.sliderImg = c)} className="author-block__image__slider">
                                    {activeQuestion.imgUrls.map((imgUrl, ind) => {
                                        return (
                                            <img key={ind} src={imgUrl} alt=""/>
                                        )
                                    })}
                                </div>
                            )
                        }
                        {
                            activeQuestion.imgUrls.length === 0 && !this.state.showSimulation && (
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true" />
                                    <br/>
                                    <button type="button" onClick={this.addImage.bind(this)} className="author-block__image-selector__btn">
                                        + Add image
                                    </button>
                                </div>
                            )
                        }
                    </div>
                    <div className="author-block__question">
                        <div className="text-editor__holder">
                            <SingleWYSIWYGComponent
                                shouldReset={shouldResetEditor}
                                changeHandler={this.changeDescription}
                                content={activeQuestion.description}
                                />
                        </div>
                        {
                            activeQuestion.problemTypes.map((problemType, index) => {
                                return (
                                    <div className={`questions__wrapper is-${problemType.type}`}>
                                        <div className="questions__list__toolbar">
                                            <button
                                                title='Radio'
                                                type="button"
                                                className={`questions__list__toolbar__btn ${problemType.type === 'radio' ? 'is-active' : ''}`}>
                                                <i
                                                    className="fa fa-dot-circle-o"
                                                    data-type="radio"
                                                    data-problem-type-index={index}
                                                    aria-hidden="true"
                                                    onClick={this.changeQuestionType}/>
                                            </button>
                                            <button
                                                title='Checkbox'
                                                type="button"
                                                className={`questions__list__toolbar__btn ${problemType.type === 'checkbox' ? 'is-active' : ''}`}>
                                                <i
                                                    className="fa fa-check-square-o"
                                                    data-type="checkbox"
                                                    data-problem-type-index={index}
                                                    aria-hidden="true"
                                                    onClick={this.changeQuestionType} />
                                            </button>
                                            <button
                                                title='Dropdown'
                                                type="button"
                                                className={`questions__list__toolbar__btn ${problemType.type === 'select' ? 'is-active' : ''}`}>
                                                <i
                                                    className="fa fa-list-alt"
                                                    data-type="select"
                                                    data-problem-type-index={index}
                                                    aria-hidden="true"
                                                    onClick={this.changeQuestionType} />
                                            </button>
                                            <button
                                                title='Numerical'
                                                type="button"
                                                data-type="number"
                                                data-problem-type-index={index}
                                                onClick={this.changeQuestionType}
                                                className={`questions__list__toolbar__btn ${problemType.type === 'number' ? 'is-active' : ''}`}>
                                                123...
                                            </button>
                                            <button
                                                title='Text'
                                                type="button"
                                                data-type="text"
                                                data-problem-type-index={index}
                                                onClick={this.changeQuestionType}
                                                className={`questions__list__toolbar__btn ${problemType.type === 'text' ? 'is-active' : ''}`}>
                                                Text
                                            </button>
                                        </div>

                                        <div className="questions__list">
                                            {this.getOptions(problemType, index)}
                                        </div>
                                        {this.getButtonAddOption(problemType.type, index)}
                                        <div className="questions-toolbar-add">
                                            <button className="questions-toolbar-add__btn is-add" type="button" onClick={this.addProblemType.bind(this)}>
                                                <i className="fa fa-plus-square" aria-hidden="true" />
                                            </button>
                                            {
                                                activeQuestion.problemTypes.length > 1 && (
                                                    <button className="questions-toolbar-add__btn is-remove" type="button" data-problem-type-index={index} onClick={this.removeProblemType.bind(this)}>
                                                        <i className="fa fa-trash" aria-hidden="true" />
                                                    </button>
                                                )
                                            }
                                        </div>
                                    </div>
                                )
                            })
                        }
                    </div>
                </div>
                <div className="questions-toolbar">
                    <div className="author-toolbar">
                        {
                            activeQuestion.iframeUrl && (
                                <div className="author-toolbar__row">
                                    <button className="author-toolbar__btn regular" onClick={this.showSimulation.bind(this)}>
                                        {this.state.showSimulation ? 'Show Images' : 'Show simulation'}
                                    </button>
                                </div>
                            )
                        }

                        <div className="author-toolbar__row">
                            {
                                activeQuestion.imgUrls.map((img, ind) => {
                                    return (
                                        <div className="author-toolbar__row-holder">
                                            <input
                                                className="author-toolbar__field"
                                                type="text"
                                                onChange={this.changeImage.bind(this)}
                                                value={img}
                                                key={ind}
                                                data-index={ind}
                                                placeholder='Paste URL of the image'
                                            />
                                            <button className="author-toolbar__btn cancel" data-index={ind} onClick={this.removeImage.bind(this)}>
                                                <i className="fa fa-trash-o" aria-hidden="true" />
                                            </button>
                                        </div>
                                    )})
                            }
                            {
                                activeQuestion.imgUrls.length > 0 && (
                                    <div className="author-toolbar__add">
                                        <button className="author-toolbar__add__btn" onClick={this.addImage.bind(this)}>
                                            + add image
                                        </button>
                                    </div>
                                )
                            }
                        </div>
                        <div className="author-toolbar__row">
                            <p>"Show simulation" iframe url</p>
                            <input
                                className="author-toolbar__field is-full"
                                type="text"
                                onChange={this.changeIframeUrl.bind(this)}
                                value={activeQuestion.iframeUrl}
                                placeholder='Paste URL of the iframe'
                            />
                        </div>
                    </div>
                    <Skaffolds
                        questionChanged={this.props.questionChanged}
                        activeQuestion={activeQuestion}
                        activeQuestionIndex={this.props.activeQuestionIndex}
                        scaffoldEditingStateChange={this.scaffoldEditingStateChange}
                        />
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
