const initialState = {
    content: 'Enter a text',
    blockType: 'endSurvey',
    title: 'End Survey'
};

const EndSurvey = function(state=initialState, action) {
    switch(action.type) {
        case 'TITLE_CHANGED':
            return Object.assign({}, state, {
                content: action.content
            });
        default:
            return state;
    }
};

export default EndSurvey;
