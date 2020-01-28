import { SUBSECTION_DATA_CHANGED, SUBSECTION_DATA_PARENT_LOCATORS_CHANGED } from '../actionTypes';


const initialState = {
    parentLocator: "",
    category: "",
    displayName: "",
    componentsOrder: [
        'title',
        'introduction',
        'simulation',
        'questions',
        'lessonSummary',
        'endSurvey',
    ],
    questionsParentLocators: []
};

const SubsectionDataReducer = function(state=initialState, action) {
    switch(action.type) {
        case SUBSECTION_DATA_CHANGED:
            // TODO: change to the right action
            return {
                ...action.data,
                componentsOrder: state.componentsOrder,
                questionsParentLocators: state.questionsParentLocators
            };
        case SUBSECTION_DATA_PARENT_LOCATORS_CHANGED:
            return {
                ...state,
                questionsParentLocators: action.data
            }
        default:
            return state;
    }
};

export default SubsectionDataReducer;
