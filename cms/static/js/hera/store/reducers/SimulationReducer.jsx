import { SIMULATION_CHANGED, SIMULATION_LOADED, SIMULATION_NEW } from '../actionTypes';


const initialState = {
    blockType: 'simulation',
    sliderBar: [{content: ''}],
    imgUrl: "",
    iframeUrl: "",
    xBlockID: ""
};

const SimulationReducer = function(state=initialState, action) {
    switch(action.type) {
        case SIMULATION_CHANGED:
            let {index} = action.data;
            return {
                blockType: 'simulation',
                imgUrl: state.imgUrl,
                iframeUrl: state.iframeUrl,
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
        case SIMULATION_LOADED:
            return {
                blockType: 'simulation',
                ...action.data
            };
        case SIMULATION_NEW:
            return initialState;
        default:
            return state;
    }
};

export default SimulationReducer;
