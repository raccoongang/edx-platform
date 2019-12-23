import React from 'react';

import WYSWYGComponent from './WYSWYGComponent';


export default class PagesBaseComponent extends React.Component {

    constructor(props) {
        super(props);
        this.saveContent = this.saveContent.bind(this);
        this.state = {};
    }

    changeImgUrl(e) {
        this.setState({
            imgUrl: e.target.value,
            imgUrlChanged: true
        });
    }

    changeIframeUrl(e) {
        this.setState({
            iframeUrl: e.target.value,
            iframeUrlChanged: true
        });
    }

    confirmImgUrl() {
        console.log('confirm')
        this.props[this.changeHandlerName]({
            ...this.props[this.componentType],
            imgUrl: this.state.imgUrl,
        });
    }

    confirmIframeUrl() {
        this.props[this.changeHandlerName]({
            ...this.props[this.componentType],
            iframeUrl: this.state.iframeUrl,
        });
    }

    cancelImgUrl() {
        this.setState({
            imgUrlChanged: false
        }, () => {
            this.props[this.changeHandlerName]({
                ...this.props[this.componentType],
                imgUrl: ''
            });
        })
    }

    cancelIframeUrl() {
        this.setState({
            iframeUrlChanged: false
        }, () => {
            this.props[this.changeHandlerName]({
                ...this.props[this.componentType],
                iframeUrl: ''
            });
        })
    }

    saveContent(id, value) {
        this.props[this.changeHandlerName]({
            content: value,
            imgUrl: this.props[this.componentType].imgUrl,
            iframeUrl: this.props[this.componentType].iframeUrl,
            index: id
        });
    }

    render() {
        const data = this.props[this.componentType];
        const imgUrl = this.state.imgUrlChanged ? this.state.imgUrl : data.imgUrl;
        const iframeUrl = this.state.iframeUrlChanged ? this.state.iframeUrl : data.iframeUrl;
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img src={data.imgUrl} alt=""/>

                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true"></i>
                            <br/>
                            <button type="button" className="author-block__image-selector__btn">
                                + Add image
                            </button>
                            <button type="button" className="author-block__image-selector__btn">
                                + Add image
                            </button>
                        </div>
                    </div>
                    <div className="author-block__question">
                        {data.sliderBar.map((bar, index) => {
                            return (
                                <WYSWYGComponent
                                    key={index}
                                    index={index}
                                    content={bar.content}
                                    saveContent={this.saveContent}
                                    componentType={this.componentType}
                                    popupClosed={this.props.popupClosed}
                                    {...data}
                                />
                            )
                        })}
                    </div>
                </div>
                <div className="author-toolbar">
                    <div className="author-toolbar__row">
                        <input 
                            className="author-toolbar__field"
                            type="text"
                            onChange={this.changeImgUrl.bind(this)}
                            value={imgUrl}
                            placeholder='Paste URL of the image'
                        />
                        <button className="author-toolbar__btn cancel" onClick={this.cancelImgUrl.bind(this)}>
                            <i className="fa fa-trash-o" aria-hidden="true" />
                        </button>
                        <button
                            className={`author-toolbar__btn ${imgUrl ? '' : 'is-disabled'}`}
                            onClick={this.confirmImgUrl.bind(this)}
                        >
                            <i className="fa fa-check" aria-hidden="true"></i>
                        </button>
                        <div className="author-toolbar__add">
                            <button className="author-toolbar__add__btn" onClick={this.confirmImgUrl.bind(this)}>
                                + add image
                            </button>
                        </div>
                    </div>

                    <div className="author-toolbar__row">
                        <input 
                            className="author-toolbar__field"
                            type="text"
                            onChange={this.changeIframeUrl.bind(this)}
                            value={iframeUrl}
                            placeholder='Paste URL of the iframe'
                        />
                        <button className="author-toolbar__btn cancel" onClick={this.cancelIframeUrl.bind(this)}>
                            <i className="fa fa-trash-o" aria-hidden="true" />
                        </button>
                        <button className={`author-toolbar__btn ${iframeUrl ? '' : 'is-disabled'}`}  onClick={this.confirmIframeUrl.bind(this)}>
                            <i className="fa fa-check" aria-hidden="true"></i>
                        </button>
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
