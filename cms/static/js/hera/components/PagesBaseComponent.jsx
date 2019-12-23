import React from 'react';

import WYSWYGComponent from './WYSWYGComponent';


export default class PagesBaseComponent extends React.Component {

    constructor(props) {
        super(props);
        this.saveContent = this.saveContent.bind(this);
        this.state = {
            imgUrl: "",
            iframeUrl: ""
        };
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
                        <input className="author-toolbar__field" type="text" onChange={this.changeImgUrl.bind(this)} value={imgUrl} placeholder='Paste URL of the image' />
                        <button className="author-toolbar__btn cancel" onClick={this.cancelImgUrl.bind(this)}>
                            <i className="fa fa-trash-o" aria-hidden="true" />
                        </button>
                        <button className="author-toolbar__btn is-disabled" onClick={this.confirmImgUrl.bind(this)}>
                            <i className="fa fa-check" aria-hidden="true"></i>
                        </button>
                        <div className="author-toolbar__add">
                            <button className="author-toolbar__add__btn" onClick={this.confirmImgUrl.bind(this)}>
                                + add image
                            </button>
                        </div>
                    </div>

                    <div className="author-toolbar__row">
                        <input className="author-toolbar__field" type="text" onChange={this.changeIframeUrl.bind(this)} value={iframeUrl} placeholder='Paste URL of the iframe' />
                        <button className="author-toolbar__btn cancel" onClick={this.cancelIframeUrl.bind(this)}>
                            <i className="fa fa-trash-o" aria-hidden="true" />
                        </button>
                        <button className="author-toolbar__btn is-disabled" onClick={this.confirmIframeUrl.bind(this)}>
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
