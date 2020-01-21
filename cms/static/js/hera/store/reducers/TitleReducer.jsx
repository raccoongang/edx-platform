import { TITLE_CHANGED, TITLE_DATA_LOADED, TITLE_NEW } from '../actionTypes';


const initialState = {
    content: '',
    blockType: 'title',
    title: 'Title',
    heading: '',
    imgUrl: '',
    shouldReset: true
};

const TitleReducer = function(state=initialState, action) {
    switch(action.type) {
        case TITLE_CHANGED:
            return Object.assign({}, state, {
                ...action.data
            });
        case TITLE_DATA_LOADED:
            return {
                ...action.data
            };
        case TITLE_NEW:
            return initialState;
        default:
            return state;
    }
};

export default TitleReducer;
