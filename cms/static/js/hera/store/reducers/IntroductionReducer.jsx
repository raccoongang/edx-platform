import { INTRODUCTION_CHANGED } from '../actionTypes';


const initialState = {
    content: 'Enter an introduction text',
};

const IntroductionReducer = function(state=initialState, action) {
    console.log(action);
    switch(action.type) {
        case INTRODUCTION_CHANGED:
            return Object.assign({}, state, {
                content: action.content
            });
        default:
            return state;
    }
};

export default IntroductionReducer;
