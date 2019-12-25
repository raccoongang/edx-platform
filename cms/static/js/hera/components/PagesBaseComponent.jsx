import React from 'react';
import Slider from "react-slick";

import WYSWYGComponent from './WYSWYGComponent';

export default class PagesBaseComponent extends React.Component {

    constructor(props) {
        super(props);
        this.next = this.next.bind(this);
        this.previous = this.previous.bind(this);
        this.saveContent = this.saveContent.bind(this);
        this.state = {
            activeSlideIndex: 0
        };
    }

    changeIframeUrl(e) {
        this.props[this.changeHandlerName]({
            ...this.props[this.componentType],
            iframeUrl: e.target.value
        });
    }

    cancelIframeUrl() {
        this.setState({
            iframeAdding: false
        }, () => {
            this.props[this.changeHandlerName]({
                ...this.props[this.componentType],
                iframeUrl: ''
            });
        });
    }

    saveContent(id, value) {
        this.props[this.changeHandlerName]({
            ...this.props[this.componentType],
            content: value,
            imgUrl: this.props[this.componentType].imgUrl,
            iframeUrl: this.props[this.componentType].iframeUrl,
            index: id
        });
    }

    addContent() {
        this.props[this.addContentHandler]();
        setTimeout(()=>{
            const lastSlideNumber = this.props[this.componentType].sliderBar.length -1;
            this.slider.slickGoTo(lastSlideNumber);
            this.setState({
                activeSlideIndex: lastSlideNumber
            });
        }, 300);
    }

    removeContent(e) {
        this.props[this.removeContentHandler]({
            index: +e.target.dataset.index
        })
    }

    addImage() {
        this.props[this.addImageHandlerName]()
    }

    changeImage(e) {
        this.props[this.changeImageHandlerName]({
            index: +e.target.dataset.index,
            img: e.target.value
        });
    }

    removeImage(e) {
        this.props[this.removeImageHandlerName]({
            index: +e.target.dataset.index
        });
    }

    next() {
        this.slider.slickNext();
        this.setState({
            activeSlideIndex: ++this.state.activeSlideIndex
        });
    }

    previous() {
        this.slider.slickPrev();
        this.setState({
            activeSlideIndex: --this.state.activeSlideIndex
        });
    }

    render() {
        const settings = {
            arrows: false,
            dots: false,
            infinite: false,
            speed: 500,
            slidesToShow: 1,
            slidesToScroll: 1,
        };

        const data = this.props[this.componentType];
        return (
            <div className="author-block__wrapper">
                <div className="author-block__content">
                    <div className="author-block__image">
                        {data.imgUrl.map((img, ind) => {
                            if (img) {
                                return <img src={img} key={ind} alt=""/>
                            }
                        })}
                        {
                            data.iframeUrl && (
                                <iframe src={data.iframeUrl} frameborder="0"></iframe>
                            )
                        }
                        {
                            !data.imgUrl.length > 0 && !this.state.iframeAdding ? (
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true"></i>
                                    <br/>
                                    <button type="button" onClick={this.addImage.bind(this)} className="author-block__image-selector__btn">
                                        + Add image
                                    </button>
                                    <button type="button" onClick={()=>{this.setState({iframeAdding: true})}} className="author-block__image-selector__btn">
                                        + Add iframe
                                    </button>
                                </div>
                            ) : null
                        }
                    </div>
                    <div className="author-block__question">
                        <Slider ref={c => (this.slider = c)} {...settings} className="author-block__question__slider">
                            {data.sliderBar.map((bar, index) => {
                                return (
                                    <div key={index} className="author-block__question__slider-item">
                                        <WYSWYGComponent
                                            key={index}
                                            index={index}
                                            content={bar.content}
                                            saveContent={this.saveContent}
                                            componentType={this.componentType}
                                            popupClosed={this.props.popupClosed}
                                            {...data}
                                        />
                                        {
                                            data.sliderBar.length > 1 && (
                                                <button className="author-block__add-btn remove" data-index={index} onClick={this.removeContent.bind(this)} title="Remove slide">
                                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                                </button>
                                            )
                                        }
                                    </div>
                                )
                            })}
                        </Slider>
                        {
                            data.sliderBar.length > 1 && (
                                <div className="author-block__question__slider-controls">
                                    <button className={`author-block__question__slider-controls__prev ${this.state.activeSlideIndex === 0 ? "is-disabled" : ""}`} onClick={this.previous}>
                                        <i className="fa fa-arrow-left" aria-hidden="true" />
                                    </button>
                                    <button className={`author-block__question__slider-controls__next ${this.state.activeSlideIndex === data.sliderBar.length-1 ? 'is-disabled' : ''}`} onClick={this.next}>
                                        <i className="fa fa-arrow-right" aria-hidden="true" />
                                    </button>
                                </div>
                            )
                        }
                        <button onClick={this.addContent.bind(this)} title="Add slide" className="author-block__add-btn">
                            <i className="fa fa-plus-circle" aria-hidden="true" />
                        </button>
                    </div>
                </div>
                <div className="author-toolbar">
                    <div className="author-toolbar__row">
                        {
                            data.imgUrl.map((img, ind) => {
                                return (
                                    <div>
                                        <input 
                                        className="author-toolbar__field"
                                        type="text"
                                        onChange={this.changeImage.bind(this)}
                                        value={img}
                                        key={ind}
                                        data-index={ind}
                                        placeholder='Paste URL of the image'
                                        />
                                        <button className="author-toolbar__btn cancel" data-index={ind} onClick={this.removeImage.bind(this)}>
                                            <i className="fa fa-trash-o" aria-hidden="true" />
                                        </button>    
                                    </div>
                            )})
                        }
                        {
                            data.imgUrl.length > 0 && (
                                <div className="author-toolbar__add">
                                    <button className="author-toolbar__add__btn" onClick={this.addImage.bind(this)}>
                                        + add image
                                    </button>
                                </div>
                            )
                        }
                    </div>
                    {
                        (this.state.iframeAdding || data.iframeUrl) && (
                        <div className="author-toolbar__row">
                            <input 
                                className="author-toolbar__field"
                                type="text"
                                onChange={this.changeIframeUrl.bind(this)}
                                value={data.iframeUrl}
                                placeholder='Paste URL of the iframe'
                            />
                            <button className="author-toolbar__btn cancel" onClick={this.cancelIframeUrl.bind(this)}>
                                <i className="fa fa-trash-o" aria-hidden="true" />
                            </button>
                        </div>
                        )
                    }
                </div>
                {/*<div className="author-block__buttons">*/}
                {/*    <button type="button" className="author-block__btn">*/}
                {/*        Next*/}
                {/*    </button>*/}
                {/*</div>*/}
            </div>
        )
    }
}
