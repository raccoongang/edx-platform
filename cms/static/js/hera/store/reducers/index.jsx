import { combineReducers } from 'redux';

import TitleReducer from './TitleReducer';

var reducers = combineReducers({
    title: TitleReducer
});

export default reducers;
