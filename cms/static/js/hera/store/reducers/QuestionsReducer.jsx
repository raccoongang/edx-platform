import { QUESTION_CHANGED, QUESTION_ADDED } from '../actionTypes';


const initialState = {
    questions: [
        {title: "Question1", content: "Content question 1", imgUrl: ""},
        {title: "Question2", content: "Content question 2", imgUrl: ""},
        {title: "Question3", content: "Content question 3", imgUrl: ""}
    ],
    blockType: 'questions'
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
