import { combineReducers } from 'redux';

import TitleReducer from './TitleReducer';
import QuestionsReducer from './QuestionsReducer';

var reducers = combineReducers({
    title: TitleReducer,
    questions: QuestionsReducer
});

export default reducers;
