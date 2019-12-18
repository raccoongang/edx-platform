import React from 'react';


export default class Title extends React.Component{

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img src="https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/introduction_page/u732.png?token=f6d33cc36ed81635257d923e0e57b925e5bd06a6eb3db66f9de415c606ce56c3" alt="/"/>
                    </div>
                    <div className="author-block__question">
                        <div className="author-block__question-title">
                            Title
                        </div>
                        <div className="author-block__question-text">
                            Imagine that you are standing on a cliff, and you've just been hooked up to a bungee cord. The instructor gives you a pat on the back and then it's time to jump. What will happen?
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
