import React from 'react';

import WYSWYGComponent from './WYSWYGComponent';


export default class PagesBaseComponent extends React.Component {

    constructor(props) {
        super(props);
        this.saveContent = this.saveContent.bind(this);
    }

    render() {
        const data = this.props[this.componentType];
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
                <div className="author-block__buttons">
                    <button type="button" className="author-block__btn">
                        Next
                    </button>
                </div>
            </div>
        )
    }
}
