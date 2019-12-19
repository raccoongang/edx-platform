import React from 'react';

import WYSWYGComponent from './WYSWYGComponent';


export default class Title extends React.Component{

    saveContent(index, content) {
        console.log(content);
    }

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img
                            src="https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/introduction_page/u732.png"
                            alt=""/>
                    </div>
                    <div className="author-block__question">
                        <WYSWYGComponent content={this.props.title.content} saveContent={this.saveContent.bind(this)}/>
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
