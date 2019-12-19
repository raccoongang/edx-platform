import { QUESTION_CHANGED, QUESTION_ADDED } from '../actionTypes';


const initialState = {
    questions: [
        {title: "Question1"},
        {title: "Question2"},
        {title: "Question3"}
    ],
};

const QuestionsReducer = function(state=initialState, action) {
    switch(action.type) {
        case QUESTION_CHANGED:
            // TODO: change to the right action
            return Object.assign({}, state, {
                questions: action.questions
            });
        case QUESTION_CHANGED:
            // TODO: change to the right action
            return Object.assign({}, state, {
                questions: action.questions
            });
        default:
            return state;
    }
};

export default QuestionsReducer;
