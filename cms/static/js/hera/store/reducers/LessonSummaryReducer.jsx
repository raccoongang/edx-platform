import {LESSON_SUMMARY_LOADED, LESSON_SUMMARY_CHANGED} from '../actionTypes';

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
        default:
            return state;
    }
};

export default LessonSummary;
