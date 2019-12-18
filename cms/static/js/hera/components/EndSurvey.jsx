import React from 'react';


export default class EndServey extends React.Component{

    render() {
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        <img src="https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/scenario_page/u620.png?token=937ef3394f9bbd5177382de1fe4cbf677b95681186e42c8b44b00217fe8c6834" alt="/"/>
                    </div>
                    <div className="author-block__question">
                        <div className="author-block__question-title">
                            End Servey
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
