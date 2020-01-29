import {LESSON_SUMMARY_LOADED, LESSON_SUMMARY_CHANGED} from '../actionTypes';

const initialState = {
    imgUrl: 'https://d1icd6shlvmxi6.cloudfront.net/gsc/THB1PC/52/ec/b3/52ecb386d0d140898c3a931c5caaccba/images/home/u12.png?token=57e7eb167b33f7d9850a0cd30df08061a0e44385c175b56e5cf0211d00ee15d9',
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
