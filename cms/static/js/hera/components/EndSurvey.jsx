import React from 'react';

export default class EndSurvey extends React.Component{

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__question is-large">
                        <div className="end-survey__row">
                            <div className="end-survey__field">
                                <div className="end-survey__field-title">
                                    <input className="end-survey__field-title__input" placeholder="Enter title of the page" type="text"/>
                                </div>
                            </div>
                        </div>
                        <div className="end-survey__row">
                            <div className="end-survey__field">
                                <div className="end-survey__field-title">
                                    <label className="end-survey__field-title__label">
                                        Text of the question
                                    </label>
                                    <input className="end-survey__field-title__input" type="text"/>
                                </div>
                                <div className="end-survey__field-radios">
                                    <div className="questions__wrapper is-radio">
                                        <div className="questions__list__item">
                                            <label className="questions__list__label">
                                                <input className="questions__list__input" type="radio" />
                                                <div className="questions__list__text">
                                                    <input className="questions__list__text-hint" placeholder="Question text" type="text" />
                                                </div>
                                            </label>
                                            <div className="end-survey__radio-buttons">
                                                <button className="end-survey__radio-btn is-add" type="button">
                                                    <i className="fa fa-plus-square" aria-hidden="true" />
                                                </button>
                                                <button className="end-survey__radio-btn is-remove" type="button">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            </div>
                                        </div>

                                        <div className="questions__list__item">
                                            <label className="questions__list__label">
                                                <input className="questions__list__input" type="radio" />
                                                <div className="questions__list__text">
                                                    <input className="questions__list__text-hint" placeholder="Question text" type="text" />
                                                </div>
                                            </label>
                                            <div className="end-survey__radio-buttons">
                                                <button className="end-survey__radio-btn is-add" type="button">
                                                    <i className="fa fa-plus-square" aria-hidden="true" />
                                                </button>
                                                <button className="end-survey__radio-btn is-remove" type="button">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            </div>
                                        </div>

                                        <div className="questions__list__item">
                                            <label className="questions__list__label">
                                                <input className="questions__list__input" type="radio" />
                                                <div className="questions__list__text">
                                                    <input className="questions__list__text-hint" placeholder="Question text" type="text" />
                                                </div>
                                            </label>
                                            <div className="end-survey__radio-buttons">
                                                <button className="end-survey__radio-btn is-add" type="button">
                                                    <i className="fa fa-plus-square" aria-hidden="true" />
                                                </button>
                                                <button className="end-survey__radio-btn is-remove" type="button">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            </div>
                                        </div>

                                        <div className="questions__list__item">
                                            <label className="questions__list__label">
                                                <input className="questions__list__input" type="radio" />
                                                <div className="questions__list__text">
                                                    <input className="questions__list__text-hint" placeholder="Question text" type="text" />
                                                </div>
                                            </label>
                                            <div className="end-survey__radio-buttons">
                                                <button className="end-survey__radio-btn is-add" type="button">
                                                    <i className="fa fa-plus-square" aria-hidden="true" />
                                                </button>
                                                <button className="end-survey__radio-btn is-remove" type="button">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            </div>
                                        </div>

                                        <div className="questions__list__item">
                                            <label className="questions__list__label">
                                                <input className="questions__list__input" type="radio" />
                                                <div className="questions__list__text">
                                                    <input className="questions__list__text-hint" placeholder="Question text" type="text" />
                                                </div>
                                            </label>
                                            <div className="end-survey__radio-buttons">
                                                <button className="end-survey__radio-btn is-add" type="button">
                                                    <i className="fa fa-plus-square" aria-hidden="true" />
                                                </button>
                                                <button className="end-survey__radio-btn is-remove" type="button">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="end-survey__row-buttons">
                                <button className="end-survey__row-btn is-remove" type="button">
                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                    Remove row
                                </button>
                                <button className="end-survey__row-btn is-add" type="button">
                                    <i className="fa fa-plus-circle" aria-hidden="true" />
                                    Add row with items
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="author-block__image is-small">
                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true" />
                            <br/>
                            <button type="button" className="author-block__image-selector__btn">+ Add image</button>
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
                                <i className="fa fa-trash-o" aria-hidden="true" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
