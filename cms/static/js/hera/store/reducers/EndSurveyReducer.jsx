import {END_SURVEY_CHANGED, END_SURVEY_LOADED} from '../actionTypes';

const initialState = {
    blockType: 'endSurvey',
    title: 'End Survey',
    confidence: {
        "type": "options",
        "questionText": "Now that I've finished this lesson, I am confident that I understand the concepts/information. ",
        "possibleAnswers": ["Not at all", "Slightly",
        "Moderately", "Extremely"
        ]
    },
    heading: '',
    imgUrl: 'https://qrius.com/wp-content/uploads/2019/07/cute.jpeg',
    questions: [
        {
            "type": "options",
            "questionText": "I feel that I learned something new.",
            "possibleAnswers": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        }, 
        {
            "type": "options",
            "questionText": "The help options were useful.",
            "possibleAnswers": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        },
        {
            "type": "options",
            "questionText": "The simulation was interesting.",
            "possibleAnswers": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        }, 
        {
            "type": "options",
            "questionText": "I can motivate myself to complete science tasks.",
            "possibleAnswers": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        },
        {
            "type": "options",
            "questionText": "Compared to others my age, I am good at science.",
            "possibleAnswers": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        }
    ]
};

const EndSurvey = function(state=initialState, action) {
    switch(action.type) {
        case END_SURVEY_CHANGED:
            // return state
            return Object.assign({}, state, {
                ...action.data
            });
        case END_SURVEY_LOADED:
            return {
                ...action.data
            }
        default:
            return state;
    }
};

export default EndSurvey;
