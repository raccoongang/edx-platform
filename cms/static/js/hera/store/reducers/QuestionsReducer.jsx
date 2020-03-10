import { 
    QUESTION_CHANGED,
    QUESTION_LOADED,
    QUESTION_ADDED,
    QUESTION_TITLE_CHANGED,
    QUESTION_DELETED,
    QUESTION_RESET,
    QUESTION_REMOVE_PROBLEM_TYPE,
    QUESTION_ADD_NEW_PROBLEM_TYPE,
} from '../actionTypes';

const defaultProblemType = {
    title: "",
    type: 'radio', // ['radio', 'checkbox', 'select', 'number', 'text']
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
};

const questionTemplate = {
    title: "Question",
    description: "",
    imgUrls: [],
    iframeUrl: "",
    confidenceText: "How confident are you about your answer?",
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
    problemTypes: [defaultProblemType],
    isScaffoldsEnabled: true,
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
            // transition. 
            // question -> problemTypes - now it's list of problemTypes
            // questionType -> type
            const transitionedQuestions = action.data.map((question, ind) => {
                var question = {...question};
                if (question.isScaffoldsEnabled === undefined) {
                    question.isScaffoldsEnabled = true;
                }
                if (question && question.question) {
                    let problemType = {
                        ...question.question,
                        type: question.question.questionType
                    };
                    delete problemType['questionType'];
                    let newQuestion = {...question, problemTypes: [problemType]};
                    delete newQuestion['question'];
                    return newQuestion;
                }
                return question;
            });
            return {
                blockType: 'questions',
                questions: transitionedQuestions
            };
        case QUESTION_RESET:
            return {
                blockType: 'questions',
                questions: []
            }
        case QUESTION_ADD_NEW_PROBLEM_TYPE:
            return {
                ...state,
                questions: state.questions.map((question, ind) => {
                    if (ind === action.questionIndex) {
                        return {
                            ...question,
                            problemTypes: question.problemTypes.concat([defaultProblemType])
                        }
                    }
                    return question;
                })
            };
        case QUESTION_REMOVE_PROBLEM_TYPE:
            return {
                ...state,
                questions: state.questions.map((question, ind) => {
                    if (ind === action.questionIndex) {
                        return {
                            ...question,
                            problemTypes: question.problemTypes.filter((el, ind) => {
                                return ind !== action.problemTypeIndex;
                            })
                        }
                    }
                    return question;
                })
            };
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
