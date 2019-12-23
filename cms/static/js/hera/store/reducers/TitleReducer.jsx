import { TITLE_CHANGED } from '../actionTypes';


const initialState = {
    content: 'Enter a text',
};

const TitleReducer = function(state=initialState, action) {
    switch(action.type) {
        case TITLE_CHANGED:
            return Object.assign({}, state, {
                content: action.content
            });
        default:
            return state;
    }
};

export default TitleReducer;
