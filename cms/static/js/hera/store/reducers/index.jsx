import { combineReducers } from 'redux';

import TitleReducer from './TitleReducer';
import QuestionsReducer from './QuestionsReducer';
import IntroductionReducer from './IntroductionReducer';
import SimulationReducer from './SimulationReducer';
import SubsectionDataReducer from './SubsectionDataReducer';
import EndSurvey from './EndSurveyReducer';

var reducers = combineReducers({
    title: TitleReducer,
    introduction: IntroductionReducer,
    simulation: SimulationReducer,
    questions: QuestionsReducer,
    subsectionData: SubsectionDataReducer,
    endSurvey: EndSurvey
});

export default reducers;
