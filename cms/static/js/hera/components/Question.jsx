import React from 'react';
import Slider from "react-slick";

import SingleWYSIWYGComponent from './SingleWYSIWYGComponent';


export default class Question extends React.Component{

    constructor(props) {
        super(props);

        this.changeQuestionType = this.changeQuestionType.bind(this);
        this.changeOptionCorrectness = this.changeOptionCorrectness.bind(this);
        this.changeOptionTitle = this.changeOptionTitle.bind(this);
        this.changeDescription = this.changeDescription.bind(this);

        this.state = {
            showSimulation: false
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
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        let question = {...activeQuestion.question};
        question.questionType = e.target.dataset.type;
        question.options = question.options.map(opt => {
            return {
                correct: false,
                title: opt.title
            };
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    addOptionItem() {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        let question = {...activeQuestion.question};
        // adding new empty option
        question.options = question.options.concat([{
            correct: false,
            title: ""
        }]);

        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    removeOptionItem(e) {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        let question = {...activeQuestion.question};

        question.options = question.options.filter((el, ind) => ind !== +e.target.dataset.index);

        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    changeOptionCorrectness(e) {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        let question = {...activeQuestion.question};
        question.options = question.options.map((opt, ind) => {
            if (['select', 'radio'].includes(question.questionType)) {
                if (ind === +e.target.dataset.index) {
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
                if (ind === +e.target.dataset.index) {
                    return {
                        correct: e.target.checked,
                        title: opt.title
                    };
                } else {
                    return opt;
                }
            }
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    changeOptionTitle(e) {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        let question = {...activeQuestion.question};
        question.options = question.options.map((opt, ind) => {
            if (ind === +e.target.dataset.index) {
                return {
                    ...opt,
                    title: e.target.value
                };
            } else {
                return opt;
            }
        });
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
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
        console.log(+e.target.dataset.index);
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
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        let question = {...activeQuestion.question};
        question.answer = e.target.value;
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    changePreciseness(e) {
        const activeQuestion = {...this.props.questions[this.props.activeQuestionIndex]};
        let question = {...activeQuestion.question};
        question.preciseness = e.target.value;
        this.props.questionChanged(this.props.activeQuestionIndex, {
            ...activeQuestion,
            question: question
        });
    }

    showSimulation() {
        this.setState({
            showSimulation: !this.state.showSimulation
        })
    }

    render() {
        const activeQuestion = this.props.questions[this.props.activeQuestionIndex];
        if (!activeQuestion) {
            return null;
        }
        // this hack just to understand if we need to reset content for the TinyMCE editor in the SingleWYSIWYGComponent
        const shouldResetEditor = this.props.activeQuestionIndex !== this.activeQuestionIndex;

        this.activeQuestionIndex = this.props.activeQuestionIndex;
        const type = activeQuestion.question.questionType === 'select' ? 'radio' : activeQuestion.question.questionType;

        const getOptions = () => {
            if (type === 'number') {
                return (
                    <div className="questions__list number">
                        <div className="questions__list__item">
                            <input
                                className="questions__list__field"
                                type="number"
                                placeholder="Type numbers here"
                                value={activeQuestion.question.answer}
                                onChange={this.changeAnswer.bind(this)}
                                />
                        </div>
                        <div className="questions__list__item">
                            <input
                                className="questions__list__field"
                                type="text"
                                value={activeQuestion.question.preciseness}
                                onChange={this.changePreciseness.bind(this)}
                                placeholder="Enter preciseness"
                                />
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
                                placeholder="Enter Text"
                                value={activeQuestion.question.answer}
                                onChange={this.changeAnswer.bind(this)}
                                />
                        </div>
                    </div>
                );
            }
            return activeQuestion.question.options.map((option, ind) => {
                return (
                    <div className="questions__list__item">
                        <label className="questions__list__label">
                            <input
                                key={ind}
                                data-index={ind}
                                onChange={this.changeOptionCorrectness}
                                className="questions__list__input"
                                type={type}
                                checked={option.correct}/>
                            <div className="questions__list__text">
                                <input
                                    onChange={this.changeOptionTitle}
                                    key={ind}
                                    data-index={ind}
                                    className="questions__list__text-hint"
                                    type="text"
                                    placeholder="Type questions text here..."
                                    value={option.title}
                                    />
                            </div>
                        </label>
                        {activeQuestion.question.options.length > 1 && (
                            <button className="questions__list__remove-item" title="Remove item">
                                <i className="fa fa-trash-o" aria-hidden="true" data-index={ind} onClick={this.removeOptionItem.bind(this)} />
                            </button>
                        )}
                    </div>
                );
            });
        };

        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        {
                            this.state.showSimulation ? (
                                <iframe src={activeQuestion.iframeUrl} frameborder="0"></iframe>
                            ) : (
                                <Slider ref={c => (this.sliderImg = c)} {...this.settingsImg} className="author-block__image__slider">
                                    {activeQuestion.imgUrls.map((imgUrl, ind) => {
                                        return (
                                            <img key={ind} src={imgUrl} alt=""/>
                                        )
                                    })}
                                </Slider>
                            )
                        }
                        {
                            activeQuestion.imgUrls.length === 0 && (
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true"></i>
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
                        <div className={`questions__wrapper is-${activeQuestion.question.questionType}`}>
                            <div className="questions__list__toolbar">
                                <button
                                    title='Radio'
                                    type="button"
                                    className={`questions__list__toolbar__btn ${activeQuestion.question.questionType === 'radio' ? 'is-active' : ''}`}>
                                    <i className="fa fa-dot-circle-o" data-type="radio" aria-hidden="true" onClick={this.changeQuestionType}/>
                                </button>
                                <button
                                    title='Checkbox'
                                    type="button"
                                    className={`questions__list__toolbar__btn ${activeQuestion.question.questionType === 'checkbox' ? 'is-active' : ''}`}>
                                    <i className="fa fa-check-square-o" data-type="checkbox" aria-hidden="true" onClick={this.changeQuestionType} />
                                </button>
                                <button
                                    title='Dropdown'
                                    type="button"
                                    className={`questions__list__toolbar__btn ${activeQuestion.question.questionType === 'select' ? 'is-active' : ''}`}>
                                    <i className="fa fa-list-alt" data-type="select" aria-hidden="true" onClick={this.changeQuestionType} />
                                </button>
                                <button title='Numerical' type="button" data-type="number" onClick={this.changeQuestionType} className={`questions__list__toolbar__btn ${activeQuestion.question.questionType === 'number' ? 'is-active' : ''}`}>
                                    123...
                                </button>
                                <button title='Text' type="button" data-type="text" onClick={this.changeQuestionType} className={`questions__list__toolbar__btn ${activeQuestion.question.questionType === 'text' ? 'is-active' : ''}`}>
                                    Text
                                </button>
                            </div>

                            <div className="questions__list">
                                {getOptions()}

                                {!['number', 'text'].includes(type) && (
                                    <div className="questions__list__add-item">
                                        <button type="button" className="questions__list__add-item__btn" onClick={this.addOptionItem.bind(this)}>
                                            + add item
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="scaffolds__wrapper">
                            <button type="button" className="scaffolds__btn">
                                Scaffolds 1
                            </button>
                            <button type="button" className="scaffolds__btn">
                                Scaffolds 2
                            </button>
                            <button type="button" className="scaffolds__btn">
                                Scaffolds 3
                            </button>
                        </div>
                    </div>
                </div>
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
                <div className="author-block__buttons">
                    <button type="button" className="author-block__btn">
                        Next
                    </button>
                </div>

                <div className="scaffolds-modal">
                    <div className="scaffolds-modal__content">
                        <div className="scaffolds-modal__content-simple">
                            <SingleWYSIWYGComponent
                                shouldReset={shouldResetEditor}
                                changeHandler={this.changeDescription}
                                content={activeQuestion.description}
                            />
                        </div>
                        <div className="scaffolds-modal__content-additional">
                            <div className="author-block__image">
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true" />
                                </div>
                                <div>
                                    <img src="https://cdn.vox-cdn.com/thumbor/NI4JSzAlBecM9hmBxevfLKNN2AM=/0x0:637x355/1200x800/filters:focal(269x128:369x228)/cdn.vox-cdn.com/uploads/chorus_image/image/65538905/adventuretime.0.png" alt=""/>
                                </div>
                                <div className="author-toolbar__row">
                                    <input
                                        className="author-toolbar__field"
                                        type="text"
                                        placeholder='Paste URL of the image'
                                    />
                                </div>
                            </div>
                            <div className="editor-holder">
                                <SingleWYSIWYGComponent
                                    shouldReset={shouldResetEditor}
                                    changeHandler={this.changeDescription}
                                    content={activeQuestion.description}
                                />
                            </div>
                        </div>
                        <div className="scaffolds-modal__buttons">
                            <button type="button" className="scaffolds-modal__btn is-cancel">
                                cancel
                            </button>
                            <button type="button" className="scaffolds-modal__btn is-save">
                                save
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
