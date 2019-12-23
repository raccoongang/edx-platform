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
                    <input type="text" onChange={this.changeImgUrl.bind(this)} value={imgUrl}/>
                    <button onClick={this.confirmImgUrl.bind(this)}>Confirm image url</button>
                    <button onClick={this.cancelImgUrl.bind(this)}>Cancel</button>

                    <input type="text" onChange={this.changeIframeUrl.bind(this)} value={iframeUrl}/>
                    <button onClick={this.confirmIframeUrl.bind(this)}>Confirm iframe url</button>
                    <button onClick={this.cancelIframeUrl.bind(this)}>Cancel iframe url</button>

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
