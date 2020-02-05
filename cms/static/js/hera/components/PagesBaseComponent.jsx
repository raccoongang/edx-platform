import React from 'react';
import Slider from "react-slick";

import ActiveTable from './ActiveTable';
import WYSWYGComponent from './WYSWYGComponent';

export default class PagesBaseComponent extends React.Component {

    constructor(props) {
        super(props);
        this.next = this.next.bind(this);
        this.previous = this.previous.bind(this);
        this.saveContent = this.saveContent.bind(this);
        this.removeContent = this.removeContent.bind(this);
        this.addImage = this.addImage.bind(this);
        this.addContent = this.addContent.bind(this);
        this.changeImage = this.changeImage.bind(this);
        this.removeImage = this.removeImage.bind(this);
        this.changeIframeUrl = this.changeIframeUrl.bind(this);
        this.cancelIframeUrl = this.cancelIframeUrl.bind(this);
        this.addTable = this.addTable.bind(this);
        this.removeTable = this.removeTable.bind(this);

        this.sliderSpeed = 500;
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
            this.setState({
                activeSlideIndex: lastSlideNumber
            }, ()=>{
                this.sliderContent.slickGoTo(lastSlideNumber);
            });
        }, 300);
    }

    removeContent(e) {
        const target = e.target;
        target.classList.add('is-disabled');
        this.props[this.removeContentHandler]({
            index: this.state.activeSlideIndex
        });
        setTimeout(()=>{
            const sliderBarLength = this.props[this.componentType].sliderBar.length;
            if (this.state.activeSlideIndex > sliderBarLength - 1 ) {
                this.setState({
                    activeSlideIndex: sliderBarLength - 1
                });
            }
            this.sliderContent.slickGoTo(this.state.activeSlideIndex);
            target.classList.remove('is-disabled');
        }, 300);
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

    next(e) {
        const target = e.target;
        const self = this;
        target.classList.add('is-disabled');
        this.setState({
            activeSlideIndex: this.state.activeSlideIndex+1
        }, ()=>{
            this.sliderContent.slickGoTo(this.state.activeSlideIndex);
            setTimeout(()=>{
                if (this.state.activeSlideIndex < this.props[this.componentType].sliderBar.length-1) {
                    target.classList.remove('is-disabled');
                }
            }, self.sliderSpeed);
        });
    }

    previous(e) {
        const target = e.target;
        const self = this;
        target.classList.add('is-disabled');
        this.setState({
            activeSlideIndex: this.state.activeSlideIndex-1
        }, ()=>{
            this.sliderContent.slickGoTo(this.state.activeSlideIndex);
            setTimeout(()=>{
                if (this.state.activeSlideIndex > 0) {
                    target.classList.remove('is-disabled');
                }
            }, self.sliderSpeed);
        });
    }

    changeTableData(tableData, sliderIndex) {
        const data = this.props[this.componentType];
        this.props[this.changeHandlerName]({
            ...data,
            sliderBar: data.sliderBar.map((item, idx) => {
                if (idx === sliderIndex) {
                    item.tableData = tableData;
                    return item;
                }
                return item;
            })
        });
    }

    addTable(sliderIndex) {
        const data = this.props[this.componentType];
        this.props[this.changeHandlerName]({
            ...data,
            sliderBar: data.sliderBar.map((item, idx) => {
                if (idx === sliderIndex) {
                    item.tableData = {};
                    return item;
                }
                return item;
            })
        });
    }

    removeTable(sliderIndex) {
        const data = this.props[this.componentType];
        this.props[this.changeHandlerName]({
            ...data,
            sliderBar: data.sliderBar.map((item, idx) => {
                if (idx === sliderIndex) {
                    delete item['tableData'];
                    return item;
                }
                return item;
            })
        });
    }

    render() {
        const settingsImg = {
            arrows: true,
            dots: false,
            infinite: false,
            speed: 500,
            slidesToShow: 1,
            slidesToScroll: 1,
        };

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
                        {
                            data.imgUrl.length > 0 && (
                                <Slider ref={c => (this.sliderImg = c)} {...settingsImg} className="author-block__image__slider">
                                    {data.imgUrl.map((img, ind) => {
                                        if (img) {
                                            return (
                                                <div className="author-block__image__slider-item">
                                                    <img src={img} key={ind} alt=""/>
                                                </div>
                                            )
                                        }
                                    })}
                                </Slider>
                            )
                        }
                        {
                            data.iframeUrl && (
                                <iframe src={data.iframeUrl} frameBorder="0"></iframe>
                            )
                        }
                        {
                            !data.imgUrl.length > 0 && !data.iframeUrl && !this.state.iframeAdding ? (
                                <div className="author-block__image-selector">
                                    <i className="fa fa-picture-o" aria-hidden="true"></i>
                                    <br/>
                                    <button type="button" onClick={this.addImage} className="author-block__image-selector__btn">
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
                        <Slider ref={c => (this.sliderContent = c)} {...settings}  className="author-block__question__slider">
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
                                            bar.tableData && (
                                                <div className="table-holder">
                                                    <button type="button" className="table-holder__btn" onClick={() => this.removeTable(index)}>- remove table</button>
                                                    <ActiveTable tableData={bar.tableData} saveHandler={(data) => this.changeTableData(data, index)}/>
                                                </div>
                                            )
                                        }
                                        {
                                            !bar.tableData && (
                                                <button onClick={() => this.addTable(index)} title="Add Table" className="author-block__add-btn is-add-table">
                                                    <i className="fa fa-table" aria-hidden="true" />
                                                </button>
                                            )
                                        }
                                    </div>
                                )
                            })}
                        </Slider>
                        <div className="author-block-navigation">
                            {
                                data.sliderBar.length > 1 && (
                                    <button className="author-block__add-btn" onClick={this.removeContent} title="Remove slide">
                                        <i className="fa fa-trash-o" aria-hidden="true" />
                                    </button>
                                )
                            }
                            {
                                data.sliderBar.length > 1 && (
                                    <div className="author-block__question__slider-controls">
                                        <button className={`author-block__question__slider-controls__prev ${this.state.activeSlideIndex === 0 ? "is-disabled" : ""}`} onClick={this.previous} />
                                        <button className={`author-block__question__slider-controls__next ${this.state.activeSlideIndex === data.sliderBar.length-1 ? 'is-disabled' : ''}`} onClick={this.next} />
                                    </div>
                                )
                            }
                            <button onClick={this.addContent} title="Add slide" className="author-block__add-btn">
                                <i className="fa fa-plus-circle" aria-hidden="true" />
                            </button>
                        </div>
                    </div>
                </div>
                <div className="author-toolbar">
                    <div className="author-toolbar__row">
                        {
                            data.imgUrl.map((img, ind) => {
                                return (
                                    <div className="author-toolbar__row-holder">
                                        <input 
                                        className="author-toolbar__field"
                                        type="text"
                                        onChange={this.changeImage}
                                        value={img}
                                        key={ind}
                                        data-index={ind}
                                        placeholder='Paste URL of the image'
                                        />
                                        <button className="author-toolbar__btn cancel" data-index={ind} onClick={this.removeImage}>
                                            <i className="fa fa-trash-o" aria-hidden="true" />
                                        </button>    
                                    </div>
                            )})
                        }
                        {
                            data.imgUrl.length > 0 && (
                                <div className="author-toolbar__add">
                                    <button className="author-toolbar__add__btn" onClick={this.addImage}>
                                        + add image
                                    </button>
                                </div>
                            )
                        }
                    </div>
                    {
                        (this.state.iframeAdding || data.iframeUrl) && (
                        <div className="author-toolbar__row">
                            <div className="author-toolbar__row-holder">
                                <input
                                    className="author-toolbar__field"
                                    type="text"
                                    onChange={this.changeIframeUrl}
                                    value={data.iframeUrl}
                                    placeholder='Paste URL of the iframe'
                                />
                                <button className="author-toolbar__btn cancel" onClick={this.cancelIframeUrl}>
                                    <i className="fa fa-trash-o" aria-hidden="true" />
                                </button>
                            </div>
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
