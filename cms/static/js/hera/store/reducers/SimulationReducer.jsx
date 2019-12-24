import {
    SIMULATION_CHANGED,
    SIMULATION_LOADED,
    SIMULATION_NEW,
    SIMULATION_ADD_CONTENT,
    SIMULATION_REMOVE_CONTENT,
    SIMULATION_IMAGE_ADD,
    SIMULATION_IMAGE_CHANGED,
    SIMULATION_IMAGE_REMOVE
} from '../actionTypes';


const initialState = {
    blockType: 'simulation',
    sliderBar: [{content: ''}],
    imgUrl: [],
    iframeUrl: "",
    xBlockID: ""
};

const SimulationReducer = function(state=initialState, action) {
    switch(action.type) {
        case SIMULATION_CHANGED:
            let {index} = action.data;
            return {
                blockType: 'simulation',
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
                xBlockID: state.xBlockID
            };
        case SIMULATION_ADD_CONTENT:
            return {
                ...state,
                sliderBar: state.sliderBar.concat([{content: ""}])
            };
        case SIMULATION_REMOVE_CONTENT:
            return {
                ...state,
                sliderBar: state.sliderBar.filter((el, ind) => {
                    return ind !== action.data.index
                })
            };
        case SIMULATION_LOADED:
            return {
                blockType: 'simulation',
                ...action.data
            };
        case SIMULATION_NEW:
            return initialState;
        case SIMULATION_IMAGE_ADD:
            return {
                ...state,
                imgUrl: state.imgUrl.concat([''])
            }
        case SIMULATION_IMAGE_CHANGED:
            console.log(action.data);
            return {
                ...state,
                imgUrl: state.imgUrl.map((img, ind) => {
                    if (ind === action.data.index) {
                        return action.data.img;
                    }
                    return img;
                })
            };
        case SIMULATION_IMAGE_REMOVE:
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

export default SimulationReducer;
