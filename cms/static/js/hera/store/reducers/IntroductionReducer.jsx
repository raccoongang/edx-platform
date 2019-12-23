import {
    INTRODUCTION_CHANGED,
    INTRODUCTION_LOADED,
    INTRODUCTION_NEW,
    INTRODUCTION_ADD_CONTENT,
    INTRODUCTION_REMOVE_CONTENT,
    INTRODUCTION_IMAGE_ADD,
    INTRODUCTION_IMAGE_CHANGED,
    INTRODUCTION_IMAGE_REMOVE,
} from '../actionTypes';


const initialState = {
    blockType: 'introduction',
    sliderBar: [{content: ''}],
    imgUrl: [],
    iframeUrl: "",
    xBlockID: "",
    shouldReset: false
};

const IntroductionReducer = function(state=initialState, action) {
    switch(action.type) {
        case INTRODUCTION_CHANGED:
            return {
                blockType: 'introduction',
                imgUrl: action.data.imgUrl,
                iframeUrl: action.data.iframeUrl,
                sliderBar: state.sliderBar.map((slide, ind) => {
                    if (ind === action.data.index) {
                        return {
                            content: action.data.content
                        };
                    }
                    return slide;
                }),
                xBlockID: state.xBlockID,
                shouldReset: action.shouldReset
            };
        case INTRODUCTION_ADD_CONTENT:
            return {
                ...state,
                sliderBar: state.sliderBar.concat([{content: ""}])
            };
        case INTRODUCTION_REMOVE_CONTENT:
            return {
                ...state,
                sliderBar: state.sliderBar.filter((el, ind) => {
                    return ind !== action.data.index
                })
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
        case INTRODUCTION_IMAGE_ADD:
            return {
                ...state,
                imgUrl: state.imgUrl.concat([''])
            }
        case INTRODUCTION_IMAGE_CHANGED:
            return {
                ...state,
                imgUrl: state.imgUrl.map((img, ind) => {
                    if (ind === action.data.index) {
                        return action.data.img;
                    }
                    return img;
                })
            };
        case INTRODUCTION_IMAGE_REMOVE:
            return {
                ...state,
                imgUrl: state.imgUrl.filter((img, ind) => {
                    return ind !== action.data.index
                })
            };
        default:
            return state;
    }
};

export default IntroductionReducer;
