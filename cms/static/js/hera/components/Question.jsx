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
                        <div className="questions__wrapper">
                            <div className="questions__list__toolbar">
                                <button type="button" className="questions__list__toolbar__btn">
                                    <i className="fa fa-dot-circle-o" aria-hidden="true" />
                                </button>
                                <button type="button" className="questions__list__toolbar__btn">
                                    <i className="fa fa-check-square-o" aria-hidden="true" />
                                </button>
                                <button type="button" className="questions__list__toolbar__btn">
                                    <i className="fa fa-list-ol" aria-hidden="true" />
                                </button>
                                <button type="button" className="questions__list__toolbar__btn">
                                    <i className="fa fa-text-width" aria-hidden="true" />
                                </button>
                            </div>
                            <div className="questions__list radio">
                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__radio" type="radio" name="radio" />
                                        <div className="questions__list__text">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__radio" type="radio" name="radio" />
                                        <div className="questions__list__text">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__radio" type="radio" name="radio" />
                                        <div className="questions__list__text">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__add-item">
                                    <button type="button" className="questions__list__add-item__btn">
                                        + add item
                                    </button>
                                </div>
                            </div>

                            <div className="questions__list checkbox">
                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__checkbox" type="checkbox" name="checkbox" />
                                        <div className="questions__list__text checkbox">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__checkbox" type="checkbox" name="checkbox" />
                                        <div className="questions__list__text checkbox">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__item">
                                    <label className="questions__list__label">
                                        <input className="questions__list__checkbox" type="checkbox" name="checkbox" />
                                        <div className="questions__list__text checkbox">Question 1</div>
                                    </label>
                                </div>

                                <div className="questions__list__add-item">
                                    <button type="button" className="questions__list__add-item__btn">
                                        + add item
                                    </button>
                                </div>
                            </div>

                            <div className="questions__list numerical">
                                <div className="questions__list__item">
                                    <input className="questions__list__numerical" type="number" />
                                </div>
                                <div className="questions__list__add-item">
                                    <button type="button" className="questions__list__add-item__btn">
                                        + add item
                                    </button>
                                </div>
                            </div>

                            <div className="questions__list textarea">
                                <div className="questions__list__item">
                                    <textarea className="questions__list__textarea" name="text" />
                                </div>

                                <div className="questions__list__add-item">
                                    <button type="button" className="questions__list__add-item__btn">
                                        + add item
                                    </button>
                                </div>
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
                <div className="author-block__buttons">
                    <button type="button" className="author-block__btn">
                        Next
                    </button>
                </div>
            </div>
        )
    }
}
