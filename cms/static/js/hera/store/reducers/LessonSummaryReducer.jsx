const initialState = {
    content: 'Enter a text',
    blockType: 'lessonSummary',
    title: 'Lesson Summary'
};

const LessonSummary = function (state=initialState, action) {
    switch (action.type) {
        case 'TITLE_CHANGED':
            return Object.assign({}, state, {
                content: action.content
            });
        default:
            return state;
    }
};

export default LessonSummary;
