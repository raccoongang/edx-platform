import { INTRODUCTION_CHANGED, INTRODUCTION_LOADED, INTRODUCTION_NEW } from '../actionTypes';


const initialState = {
    blockType: 'introduction',
    sliderBar: [{content: ''}],
    imgUrl: "",
    iframeUrl: "",
    xBlockID: "",
    shouldReset: false
};

const IntroductionReducer = function(state=initialState, action) {
    switch(action.type) {
        case INTRODUCTION_CHANGED:
            let {index} = action.data;
            return {
                blockType: 'introduction',
                imgUrl: action.data.imgUrl,
                iframeUrl: action.data.iframeUrl,
                sliderBar: state.sliderBar.map((slide, ind) => {
                    if (ind === index) {
                        return {
                            content: action.data.content
                        };
                    }
                    return slide;
                }),
                xBlockID: state.xBlockID,
                shouldReset: action.shouldReset
            };
        case INTRODUCTION_LOADED:
            return {
                ...action.data,
                blockType: 'introduction',
            };
        case INTRODUCTION_NEW:
            return {
                ...initialState,
                shouldReset: true
            };
        default:
            return state;
    }
};

export default IntroductionReducer;
