import React from 'react';

import WYSWYGComponent from './WYSWYGComponent';


export default class Title extends React.Component{

    saveContent(index, content) {
        console.log(content);
    }

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content-mod">
                    <div className="author-block-title">
                        <input className="author-block-title__field" type="text" placeholder="Enter title here" />
                    </div>
                    <div className="author-block__image">
                        <div className="author-block__image-selector">
                            <i className="fa fa-picture-o" aria-hidden="true" />
                        </div>
                        <div className="author-block__image-holder">
                            <img src="https://www.imgbase.info/images/safe-wallpapers/cartoons/adventure_time/42077_adventure_time_adventure_time_landscape.jpg" alt=""/>
                        </div>
                    </div>
                    <div className="author-toolbar">
                        <div className="author-toolbar__row">
                            <div className="author-toolbar__row-holder">
                                <input className="author-toolbar__field" placeholder="Paste URL of the image" type="text"/>
                            </div>
                        </div>
                    </div>
                    <div className="author-block__question">
                        <WYSWYGComponent content={this.props.title.content} saveContent={this.saveContent.bind(this)}/>
                    </div>
                </div>
            </div>
        )
    }
}
