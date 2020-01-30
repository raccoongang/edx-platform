import {LESSON_SUMMARY_LOADED, LESSON_SUMMARY_CHANGED, LESSON_SUMMARY_NEW} from '../actionTypes';

const initialState = {
    imgUrl: '',
    blockType: 'lessonSummary',
    title: 'Lesson Summary'
};

const LessonSummary = function (state=initialState, action) {
    switch (action.type) {
        case LESSON_SUMMARY_LOADED:
            return {
                title: state.title,
                parentLocator: state.parentLocator,
                ...action.data,
                blockType: 'lessonSummary',
            };
        case LESSON_SUMMARY_CHANGED:
            return {
                ...state,
                ...action.data
            };
        case LESSON_SUMMARY_NEW:
            return initialState;
        default:
            return state;
    }
};

export default LessonSummary;
