import { combineReducers } from 'redux';

import TitleReducer from './TitleReducer';
import QuestionsReducer from './QuestionsReducer';
import IntroductionReducer from './IntroductionReducer';

var reducers = combineReducers({
    title: TitleReducer,
    introduction: IntroductionReducer,
    questions: QuestionsReducer
});

export default reducers;
