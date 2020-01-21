import { 
    QUESTION_CHANGED,
    QUESTION_LOADED,
    QUESTION_ADDED,
    QUESTION_TITLE_CHANGED,
    QUESTION_DELETED,
    QUESTIONS_RESET,
} from '../actionTypes';


const questionTemplate = {
    title: "New Question",
    description: "",
    imgUrls: [],
    iframeUrl: "",
    confidenceText: "How confident are you",
    correctAnswerText: "The correct answer text",
    incorrectAnswerText: "An incorrect answer text",
    rephrase: {
        // imgUrls: ["https://preview.redd.it/5ew0yywuu5t31.png?auto=webp&s=62712b2bdf101b164de9c3005445b97ae5bf56bd"],
        content: ""
    },
    breakDown: {
        imgUrls: [],
        content: ""
    },
    teachMe: {
        imgUrls: [],
        content: ""
    },
    question: {
        questionType: 'radio', // ['radio', 'checkbox', 'select', 'number', 'text']
        // 'radio', 'checkbox', 'select'
        options: [
            {
                correct: false,
                title: "" // assume this will be the unique identificator
            },
            {
                correct: false,
                title: "" // assume this will be the unique identificator
            },
            {
                correct: false,
                title: "" // assume this will be the unique identificator
            },
            {
                correct: false,
                title: "" // assume this will be the unique identificator
            }
        ],
        answer: "",
        preciseness: ""
    },
    blockType: 'question'
};

const initialState = {
    questions: [],
    blockType: 'questions'
};

const QuestionsReducer = function(state=initialState, action) {
    switch(action.type) {
        case QUESTION_TITLE_CHANGED:
            // TODO: change to the right action
            return Object.assign({}, state, {
                questions: state.questions.map((question, ind) => {
                    if (ind === action.data.index) {
                        return {
                            ...question,
                            title: action.data.title
                        };
                    } else {
                        return question;
                    }
                })
            });
        case QUESTION_CHANGED:
            return Object.assign({}, state, {
                questions: state.questions.map((question, ind) => {
                    if (ind === action.index) {
                        return action.data
                    }
                    return question;
                })
            });
        case QUESTION_ADDED:
            let newQuestion = {...questionTemplate};
            newQuestion.title = newQuestion.title + ' ' + (state.questions.length+1);
            return Object.assign({}, state, {
                questions: state.questions.concat([newQuestion])
            });
        case QUESTION_DELETED:
            return Object.assign({}, state, {
                questions: state.questions.filter((question, ind) => {
                    return ind !== action.index;
                })
            });
        case QUESTION_LOADED:
            return {
                blockType: 'questions',
                questions: action.data
            };
        case QUESTIONS_RESET:
            return {
                blockType: 'questions',
                questions: []
            }
        default:
            return state;
    }
};

// Questions
// {
//     imgUrl: "link",
//     iframeUrl: "link",
//     description: "html content",
//     options: [
//         {
//             correct: true/false,
//             title: "title text" // assume this will be the unique identificator
//         },
//         {
//             correct: true/false,
//             title: "title text" // assume this will be the unique identificator
//         }
//     ],
//     userConfidence: "int",
//     confidenceText: "some text",
//     correctAnswerText: "The correct answer text",
//     incorrectAnswerText: "An incorrect answer text",
//     rephrase: {
//         imgUrl: "link",
//         content: "html content"
//     },
//     breakDown: : {
//         imgUrl: "link",
//         content: "html content"
//     },
//     teachMe: : {
//         imgUrl: "link",
//         content: "html content"
//     },
//     question: {
//         questionType: '', // ['radio', 'checkbox', 'select', 'number', 'text']
//         // 'radio', 'checkbox', 'select'
//         options: [
//             {
//                 correct: true/false,
//                 title: "title text" // assume this will be the unique identificator
//             },
//             {
//                 correct: true/false,
//                 title: "title text" // assume this will be the unique identificator
//             }
//         ],
//         answer: text/number,
//         preciseness: text // +-5, +-0.001, +-0.1% 
//     }

export default QuestionsReducer;
