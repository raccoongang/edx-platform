const initialState = {
    content: 'Enter a text',
    blockType: 'endSurvey'
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
