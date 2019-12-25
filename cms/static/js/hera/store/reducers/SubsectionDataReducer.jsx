import { SUBSECTION_DATA_CHANGED } from '../actionTypes';


const initialState = {
    parentLocator: "",
    category: "",
    displayName: "",
    componentsOrder: [
        'title',
        'introduction',
        'simulation',
        'questions',
        'endSurvey'
    ]
};

const SubsectionDataReducer = function(state=initialState, action) {
    switch(action.type) {
        case SUBSECTION_DATA_CHANGED:
            // TODO: change to the right action
            return {
                ...action.data,
                componentsOrder: state.componentsOrder
            };
        default:
            return state;
    }
};

export default SubsectionDataReducer;
