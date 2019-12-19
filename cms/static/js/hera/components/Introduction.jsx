import React from 'react';


export default class Introduction extends React.Component {

    componentDidMount() {
        this.props.initTinyMCE('#Introduction');
    }

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img
                            src="https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/introduction_page/u733.png?token=ed0d6ae774476a9acd8863e3f51e8985a8151957a160a08d8560c68bd6c6b353"
                            alt=""/>
                    </div>
                    <div className="author-block__question">
                        <textarea id="Introduction" cols="30" rows="10" defaultValue={this.props.introduction.content}></textarea>
                        {/* <div className="author-block__question-title">
                            Introduction
                        </div>
                        <div className="author-block__question-text">
                            Imagine that you are standing on a cliff, and you've just been hooked up to a bungee cord. The instructor gives you a pat on the back and then it's time to jump. What will happen?
                        </div> */}
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
