import React from 'react';

import SingleWYSIWYGComponent from './SingleWYSIWYGComponent';


export default class Scaffolds extends React.Component{

    constructor(props) {
        super(props);

        this.state = {
            showSimulation: false,
            simpleScaffoldOpened: false,
            advancedScaffoldOpened: false,
            isTeachMe: false,
            isRephrase: false,
            isBreakDown: false,
        };
    }

    saveScaffoldData() {
        if (this.state.isRephrase) {
            this.props.questionChanged(this.props.activeQuestionIndex, {
                ...this.props.activeQuestion,
                rephrase: {
                    content: this.state.rephraseContent,
                }
            });
        } else if (this.state.isBreakDown) {
            this.props.questionChanged(this.props.activeQuestionIndex, {
                ...this.props.activeQuestion,
                breakDown: {
                    content: this.state.breakDownContent,
                    imgUrls: this.state.breakDownImgUrls
                }
            });
        } else if (this.state.isTeachMe) {
            this.props.questionChanged(this.props.activeQuestionIndex, {
                ...this.props.activeQuestion,
                teachMe: {
                    content: this.state.teachMeContent,
                    imgUrls: this.state.teachMeImgUrls
                }
            });
        }
        this.closeScaffoldsSettings();
    }

    closeScaffoldsSettings() {
        this.props.scaffoldEditingStateChange(false);
        this.setState({
            advancedScaffoldOpened: false,
            simpleScaffoldOpened: false,
            isBreakDown: false,
            isRephrase: false,
            isTeachMe: false
        });
    }

    openRephraseSettings() {
        this.props.scaffoldEditingStateChange(true);
        this.setState({
            simpleScaffoldOpened: true,
            isRephrase: true,
            isTeachMe: false,
            isBreakDown: false,
            scaffoldsSettingsMode: 'rephrase',
            rephraseContent: this.props.activeQuestion.rephrase.content,
        });
    }

    openTeachMeSettings() {
        this.props.scaffoldEditingStateChange(true);
        this.setState({
            advancedScaffoldOpened: true,
            isRephrase: false,
            isTeachMe: true,
            isBreakDown: false,
            scaffoldsSettingsMode: 'teachMe',
            teachMeContent: this.props.activeQuestion.teachMe.content,
            teachMeImgUrls: this.props.activeQuestion.teachMe.imgUrls,
        });
    }

    openBreakDownSettings() {
        this.props.scaffoldEditingStateChange(true);
        this.setState({
            advancedScaffoldOpened: true,
            isRephrase: false,
            isTeachMe: false,
            isBreakDown: true,
            scaffoldsSettingsMode: 'breakDown',
            breakDownContent: this.props.activeQuestion.breakDown.content,
            breakDownImgUrls: this.props.activeQuestion.breakDown.imgUrls,
        });
    }

    changeRephraseContent(content) {
        this.setState({
            rephraseContent: content
        });
    }

    changeTeachMeBreakDownContent(content) {
        if (this.state.isBreakDown) {
            this.setState({
                breakDownContent: content
            });
        } else if (this.state.isTeachMe) {
            this.setState({
                teachMeContent: content
            });
        }
    }

    changeAdvancedScaffoldImgUrl(e) {
        if (this.state.isBreakDown) {
            this.setState({
                breakDownImgUrls: this.state.breakDownImgUrls.map((el, ind) => {
                    if (ind === +e.target.dataset.index) {
                        return e.target.value;
                    } else {
                        return el;
                    }
                })
            });
        } else if (this.state.isTeachMe) {
            this.setState({
                teachMeImgUrls: this.state.teachMeImgUrls.map((el, ind) => {
                    if (ind === +e.target.dataset.index) {
                        return e.target.value;
                    } else {
                        return el;
                    }
                })
            });
        }
    }

    removeScaffoldImage(e) {
        if (this.state.isBreakDown) {
            this.setState({
                breakDownImgUrls: this.state.breakDownImgUrls.filter((el, ind) => {return ind !== +e.target.dataset.index})
            });
        } else if (this.state.isTeachMe) {
            this.setState({
                teachMeImgUrls: this.state.teachMeImgUrls.filter((el, ind) => {return ind !== +e.target.dataset.index})
            });
        }
    }

    addScaffoldImage(e) {
        if (this.state.isBreakDown) {
            this.setState({
                breakDownImgUrls: this.state.breakDownImgUrls.concat([''])
            });
        } else if (this.state.isTeachMe) {
            this.setState({
                teachMeImgUrls: this.state.teachMeImgUrls.concat([''])
            });
        }
    }

    getScaffoldAdvancedEditorContent() {
        if (this.state.isBreakDown) {
            return this.state.breakDownContent;
        } else if (this.state.isTeachMe) {
            return this.state.teachMeContent;
        }
    }

    getScaffoldAdvancedImgUrls() {
        if (this.state.isBreakDown) {
            return this.state.breakDownImgUrls;
        } else if (this.state.isTeachMe) {
            return this.state.teachMeImgUrls;
        }
        return [];
    }

    getScaffoldTitle() {
        if (this.state.isBreakDown) {
            return 'Break It Down';
        } else if (this.state.isTeachMe) {
            return 'Teach Me';
        } else if (this.state.isRephrase) {
            return 'Rephrase';
        }
    }

    render() {
        const scaffoldSettingsModeChanged = this.scaffoldsSettingsMode !== this.state.scaffoldsSettingsMode;
        this.scaffoldsSettingsMode = this.state.scaffoldsSettingsMode;
        return (
            <div className="scaffolds-holder">
                <div className="scaffolds-modal">
                    <div className="scaffolds-modal__content">
                        <h2 className="scaffolds-modal__title">
                            {this.getScaffoldTitle()}
                        </h2>
                        {
                            this.state.simpleScaffoldOpened && (
                                <div className="scaffolds-modal__content-simple">
                                    <SingleWYSIWYGComponent
                                        shouldReset={scaffoldSettingsModeChanged}
                                        changeHandler={this.changeRephraseContent.bind(this)}
                                        content={this.props.activeQuestion.rephrase.content}
                                    />
                                </div>
                            )
                        }
                        {
                            this.state.advancedScaffoldOpened && (
                                <div className="scaffolds-modal__content-additional">
                                    <div className="author-block__image">
                                        {
                                            this.getScaffoldAdvancedImgUrls().length === 0 && (
                                                <div className="author-block__image-selector">
                                                    <i className="fa fa-picture-o" aria-hidden="true" />
                                                </div>
                                            )
                                        }

                                        <div className="author-block__image-holder">
                                            {this.getScaffoldAdvancedImgUrls().map((src, ind) => {
                                                return <img src={src} data-index={ind} key={ind} alt=""/>
                                            })}
                                        </div>
                                    </div>
                                    <div className="editor-holder">
                                        <SingleWYSIWYGComponent
                                            shouldReset={scaffoldSettingsModeChanged}
                                            changeHandler={this.changeTeachMeBreakDownContent.bind(this)}
                                            content={this.getScaffoldAdvancedEditorContent()}
                                        />
                                    </div>
                                </div>
                            )
                        }
                        <div className="author-toolbar__row">
                            {
                                this.getScaffoldAdvancedImgUrls().map((src, ind) => {
                                    return (
                                        <div className="author-toolbar__row-holder" key={ind}>
                                            <input
                                                className="author-toolbar__field"
                                                type="text"
                                                placeholder='Paste URL of the image'
                                                value={src}
                                                data-index={ind}
                                                onChange={this.changeAdvancedScaffoldImgUrl.bind(this)}
                                            />
                                            <button className="author-toolbar__btn cancel" data-index={ind} onClick={this.removeScaffoldImage.bind(this)}>
                                                <i className="fa fa-trash-o" aria-hidden="true" />
                                            </button>
                                        </div>
                                    )
                                })
                            }
                            {
                                this.state.advancedScaffoldOpened && (
                                    <div className="author-toolbar__add">
                                        <button className="author-toolbar__add__btn" onClick={this.addScaffoldImage.bind(this)}>
                                            + add image
                                        </button>
                                    </div>
                                )
                            }
                            <div className="scaffolds-modal__buttons">
                                <button
                                    type="button"
                                    className="scaffolds-modal__btn is-cancel"
                                    onClick={this.closeScaffoldsSettings.bind(this)}>
                                    cancel
                                </button>
                                <button
                                    type="button"
                                    className="scaffolds-modal__btn is-save"
                                    onClick={this.saveScaffoldData.bind(this)}>
                                    save
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="scaffolds-buttons">
                    <button
                        type="button"
                        className="scaffolds__btn"
                        onClick={this.openRephraseSettings.bind(this)}>
                        Rephrase
                    </button>
                    <button
                        type="button"
                        className="scaffolds__btn"
                        onClick={this.openBreakDownSettings.bind(this)}>
                        Break It Down
                    </button>
                    <button
                        type="button"
                        className="scaffolds__btn"
                        onClick={this.openTeachMeSettings.bind(this)}>
                        Teach Me
                    </button>
                </div>
            </div>
        );
    }
}
